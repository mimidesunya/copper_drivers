const fs = require('fs');
const path = require('path');
const os = require('os');
const { Readable } = require('stream');

/**
 * メモリ上のフラグメントの最大サイズです。
 * フラグメントがこの大きさを超えるとディスクに書き込みます。
 */
const FRG_MEM_SIZE = 256;

/**
 * メモリ上に置かれるデータの最大サイズです。
 * メモリ上のデータがこのサイズを超えると、
 * FRG_MEM_SIZEとは無関係にディスクに書き込まれます。
 */
const ON_MEMORY = 1024 * 1024;

/**
 * 一時ファイルのセグメントサイズです。
 */
const SEGMENT_SIZE = 8192;

class Fragment {
    constructor(id) {
        this.id = id;
        this.prev = null;
        this.next = null;
        this.length = 0;
        this.buffer = Buffer.alloc(0);
        
        // Python版と同様のセグメント管理
        // segments: [segmentIndex, segmentIndex, ...] 
        this.segments = null; 
        this.segLen = 0; // 現在のセグメント末尾の使用量
    }

    /**
     * フラグメントにデータを書き込みます。
     * @param {StreamBuilder} builder - 所属するビルダー(TempFile管理)
     * @param {Buffer} data - 書き込むデータ
     * @param {Number} currentTotalOnMemory - 現在のオンメモリ総量
     * @returns {Promise<Number>} - メモリ使用量の変化分(delta)
     */
    async write(builder, data, currentTotalOnMemory) {
        let len = data.length;
        let memoryDelta = 0;
        let currentData = data;

        // メモリに保存できるか判断
        if (this.segments === null &&
            this.length + len <= FRG_MEM_SIZE &&
            currentTotalOnMemory + len <= ON_MEMORY) {
            
            this.buffer = Buffer.concat([this.buffer, data]);
            memoryDelta = len;
            this.length += len;
            return memoryDelta;
        }

        // ディスクへの書き込みが必要
        // すでにバッファにあるデータを先にフラッシュ
        if (this.buffer.length > 0) {
            const flushedLen = this.buffer.length;
            await this._flushBufferToDisk(builder);
            // バッファをクリアしたので、メモリ使用量は減る
            memoryDelta -= flushedLen;
        }

        // 新しいデータをディスクへ書き込む
        // データが大きすぎる場合、複数のセグメントにまたがる可能性がある
        await this._writeToDisk(builder, currentData);
        
        this.length += len;
        
        // 新しいデータはディスクに行ったのでメモリ増減はなし(フラッシュ分のみ減少)
        return memoryDelta;
    }

    async _flushBufferToDisk(builder) {
        if (this.buffer.length === 0) return;
        await this._writeToDisk(builder, this.buffer);
        this.buffer = Buffer.alloc(0);
    }

    async _writeToDisk(builder, data) {
        if (this.segments === null) {
            this.segments = [];
            // 最初のセグメントを確保
            const initialSeg = builder.nextSegmentIndex++;
            this.segments.push(initialSeg);
            this.segLen = 0;
        }

        let offset = 0;
        while (offset < data.length) {
            // 現在のセグメントが満杯なら新しいセグメントを追加
            if (this.segLen === SEGMENT_SIZE) {
                const nextSeg = builder.nextSegmentIndex++;
                this.segments.push(nextSeg);
                this.segLen = 0;
            }

            const currentSegIndex = this.segments[this.segments.length - 1];
            const remainingInSeg = SEGMENT_SIZE - this.segLen;
            const writeSize = Math.min(data.length - offset, remainingInSeg);

            const chunk = data.slice(offset, offset + writeSize);
            
            // ファイルの特定位置へ書き込み (ランダムアクセス)
            const filePos = (currentSegIndex * SEGMENT_SIZE) + this.segLen;
            
            await builder.writeToTempFile(chunk, filePos);

            this.segLen += writeSize;
            offset += writeSize;
        }
    }

    /**
     * フラグメントの内容を出力ストリームへ書き出す
     */
    async flushToStream(builder, outStream) {
        // メモリにある場合
        if (this.segments === null) {
            if (this.buffer.length > 0) {
                if (!outStream.write(this.buffer)) {
                    await new Promise(resolve => outStream.once('drain', resolve));
                }
            }
            return;
        }

        // ディスクにある場合
        // セグメント順に読み出して書き込む
        for (let i = 0; i < this.segments.length; i++) {
            const segIndex = this.segments[i];
            // 最後のセグメントだけは segLen まで読む。それ以外は SEGMENT_SIZE フルに読む。
            const readSize = (i === this.segments.length - 1) ? this.segLen : SEGMENT_SIZE;
            
            if (readSize > 0) {
                const filePos = segIndex * SEGMENT_SIZE;
                const buf = Buffer.alloc(readSize); // use alloc via zero-fill for safety or check bytesRead
                const bytesRead = await builder.readFromTempFile(buf, filePos);
                
                const dataToWrite = (bytesRead === readSize) ? buf : buf.slice(0, bytesRead);
                
                if (dataToWrite.length > 0) {
                    if (!outStream.write(dataToWrite)) {
                        await new Promise(resolve => outStream.once('drain', resolve));
                    }
                }
            }
        }
    }

    async dispose() {
        // 実際にはBuilderが一括でファイルを消すので、ここでは個別にやることなし
        this.buffer = null;
        this.segments = null;
    }
}

class StreamBuilder {
    constructor(outStream, finishFunc = null) {
        this.out = outStream;
        this.finishFunc = finishFunc;
        this.frgs = [];
        this.first = null;
        this.last = null;
        this.onMemory = 0;
        this.totalLength = 0;

        // Temp file management (Shared by all fragments)
        this.tempPath = null;
        this.fd = null;
        this.nextSegmentIndex = 0; // 次に割り当てるセグメント番号
    }

    // --- Temp File Helpers ---
    async _ensureTempFile() {
        if (!this.fd) {
            this.tempPath = path.join(os.tmpdir(), `cti-node-${Date.now()}-${Math.random()}.tmp`);
            this.fd = await fs.promises.open(this.tempPath, 'w+');
        }
    }

    async writeToTempFile(buffer, position) {
        await this._ensureTempFile();
        await this.fd.write(buffer, 0, buffer.length, position);
    }

    async readFromTempFile(buffer, position) {
        if(!this.fd) return 0;
        const { bytesRead } = await this.fd.read(buffer, 0, buffer.length, position);
        return bytesRead;
    }
    // -------------------------

    addBlock() {
        const id = this.frgs.length;
        const frg = new Fragment(id);
        this.frgs.push(frg);

        if (this.first === null) {
            this.first = frg;
        } else {
            this.last.next = frg;
            frg.prev = this.last;
        }
        this.last = frg;
    }

    insertBlockBefore(anchorId) {
        const id = this.frgs.length;
        const frg = new Fragment(id);
        this.frgs.push(frg);
        
        const anchor = this.frgs[anchorId];
        
        frg.prev = anchor.prev;
        frg.next = anchor;
        
        if (anchor.prev) {
            anchor.prev.next = frg;
        }
        anchor.prev = frg;

        if (this.first === anchor) {
            this.first = frg;
        }
    }

    async write(id, data) {
        const frg = this.frgs[id];
        const delta = await frg.write(this, data, this.onMemory);
        this.onMemory += delta;
        this.totalLength += data.length;
    }
    
    async serialWrite(data) {
        if (!this.out.write(data)) {
            await new Promise(resolve => this.out.once('drain', resolve));
        }
    }

    closeBlock(id) {
        // No-op
    }

    async finish() {
        try {
            if (this.finishFunc) {
                await this.finishFunc(this.totalLength);
            }

            let frg = this.first;
            while (frg) {
                await frg.flushToStream(this, this.out);
                frg = frg.next;
            }
        } finally {
            await this.disposeTemp();
        }
    }

    async dispose() {
        await this.disposeTemp();
        this.frgs = [];
    }
    
    async disposeTemp() {
        if (this.fd) {
            await this.fd.close().catch(() => {});
            this.fd = null;
        }
        if (this.tempPath) {
            await fs.promises.unlink(this.tempPath).catch(() => {});
            this.tempPath = null;
        }
    }
}

class FileBuilder extends StreamBuilder {
    constructor(filePath) {
        const stream = fs.createWriteStream(filePath);
        super(stream, null);
    }
    
    async finish() {
        await super.finish();
        this.out.end();
        await new Promise(resolve => this.out.once('finish', resolve));
    }
}

class NullBuilder {
    addBlock() {}
    insertBlockBefore(id) {}
    async write(id, data) {}
    closeBlock(id) {}
    async serialWrite(data) {}
    async finish() {}
    async dispose() {}
}

module.exports = {
    StreamBuilder,
    FileBuilder,
    NullBuilder
};
