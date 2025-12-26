const { Buffer } = require('buffer');

const MSG = {
    REQ_PROPERTY: 0x01,
    REQ_START_MAIN: 0x02,
    REQ_SERVER_MAIN: 0x03,
    REQ_CLIENT_RESOURCE: 0x04,
    REQ_CONTINUOUS: 0x05,
    REQ_DATA: 0x11,
    REQ_START_RESOURCE: 0x21,
    REQ_MISSING_RESOURCE: 0x22,
    REQ_EOF: 0x31,
    REQ_ABORT: 0x32,
    REQ_JOIN: 0x33,
    REQ_RESET: 0x41,
    REQ_CLOSE: 0x42,
    REQ_SERVER_INFO: 0x51,

    RES_START_DATA: 0x01,
    RES_BLOCK_DATA: 0x11,
    RES_ADD_BLOCK: 0x12,
    RES_INSERT_BLOCK: 0x13,
    RES_MESSAGE: 0x14,
    RES_MAIN_LENGTH: 0x15,
    RES_MAIN_READ: 0x16,
    RES_DATA: 0x17,
    RES_CLOSE_BLOCK: 0x18,
    RES_RESOURCE_REQUEST: 0x21,
    RES_EOF: 0x31,
    RES_ABORT: 0x32,
    RES_NEXT: 0x33,

    CTI_BUFFER_SIZE: 1024
};

// --- Write Helpers ---

function writeInt(buf, offset, value) {
    buf.writeUInt32BE(value, offset);
    return offset + 4;
}

function writeShort(buf, offset, value) {
    buf.writeUInt16BE(value, offset);
    return offset + 2;
}

function writeByte(buf, offset, value) {
    buf.writeUInt8(value, offset);
    return offset + 1;
}

function writeBytes(buf, offset, strOrBuf) {
    const b = Buffer.isBuffer(strOrBuf) ? strOrBuf : Buffer.from(strOrBuf, 'utf8');
    offset = writeShort(buf, offset, b.length);
    b.copy(buf, offset);
    return offset + b.length;
}

function writeLong(buf, offset, value) {
    const bigVal = BigInt(value);
    buf.writeBigInt64BE(bigVal, offset);
    return offset + 8;
}

// --- Request Generators ---

function req_server_info(uri) {
    const uriBuf = Buffer.from(uri, 'utf8');
    const payloadSize = 1 + 2 + uriBuf.length;
    const buf = Buffer.alloc(4 + payloadSize);
    
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_SERVER_INFO);
    off = writeBytes(buf, off, uriBuf);
    return buf;
}

function req_client_resource(mode) {
    const payloadSize = 2;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_CLIENT_RESOURCE);
    off = writeByte(buf, off, mode ? 1 : 0);
    return buf;
}

function req_continuous(mode) {
    const payloadSize = 2;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_CONTINUOUS);
    off = writeByte(buf, off, mode ? 1 : 0);
    return buf;
}

function req_missing_resource(uri) {
    const uriBuf = Buffer.from(uri, 'utf8');
    const payloadSize = 1 + 2 + uriBuf.length;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_MISSING_RESOURCE);
    off = writeBytes(buf, off, uriBuf);
    return buf;
}

function req_reset() {
    const payloadSize = 1;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_RESET);
    return buf;
}

function req_abort(mode) {
    const payloadSize = 2;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_ABORT);
    off = writeByte(buf, off, mode);
    return buf;
}

function req_join() {
    const payloadSize = 1;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_JOIN);
    return buf;
}

function req_eof() {
    const payloadSize = 1;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_EOF);
    return buf;
}

function req_property(name, value) {
    const nameBuf = Buffer.from(name, 'utf8');
    const valBuf = Buffer.from(value, 'utf8');
    const payloadSize = 5 + nameBuf.length + valBuf.length;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_PROPERTY);
    off = writeBytes(buf, off, nameBuf);
    off = writeBytes(buf, off, valBuf);
    return buf;
}

function req_server_main(uri) {
    const uriBuf = Buffer.from(uri, 'utf8');
    const payloadSize = 1 + 2 + uriBuf.length;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_SERVER_MAIN);
    off = writeBytes(buf, off, uriBuf);
    return buf;
}

function req_start_resource(uri, mimeType = 'text/css', encoding = '', length = -1) {
    const uriBuf = Buffer.from(uri, 'utf8');
    const mimeBuf = Buffer.from(mimeType, 'utf8');
    const encBuf = Buffer.from(encoding, 'utf8');
    const payloadSize = 1 + 2 + uriBuf.length + 2 + mimeBuf.length + 2 + encBuf.length + 8;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_START_RESOURCE);
    off = writeBytes(buf, off, uriBuf);
    off = writeBytes(buf, off, mimeBuf);
    off = writeBytes(buf, off, encBuf);
    off = writeLong(buf, off, length);
    return buf;
}

function req_start_main(uri, mimeType = 'text/html', encoding = '', length = -1) {
    const uriBuf = Buffer.from(uri, 'utf8');
    const mimeBuf = Buffer.from(mimeType, 'utf8');
    const encBuf = Buffer.from(encoding, 'utf8');
    const payloadSize = 1 + 2 + uriBuf.length + 2 + mimeBuf.length + 2 + encBuf.length + 8;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_START_MAIN);
    off = writeBytes(buf, off, uriBuf);
    off = writeBytes(buf, off, mimeBuf);
    off = writeBytes(buf, off, encBuf);
    off = writeLong(buf, off, length);
    return buf;
}

function req_data(data) {
    const dBuf = Buffer.isBuffer(data) ? data : Buffer.from(data, 'utf8');
    const payloadSize = 1 + dBuf.length;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, MSG.REQ_DATA);
    dBuf.copy(buf, off);
    return buf;
}

function req_close() {
    return req_simple(MSG.REQ_CLOSE);
}

// 内部ヘルパー
function req_simple(type) {
    const payloadSize = 1;
    const buf = Buffer.alloc(4 + payloadSize);
    let off = 0;
    off = writeInt(buf, off, payloadSize);
    off = writeByte(buf, off, type);
    return buf;
}


// --- Packet Parsing ---

// BufferReader helper class to maintain offset state
class BufferReader {
    constructor(buffer) {
        this.buffer = buffer;
        this.offset = 0;
    }
    
    readByte() {
        const v = this.buffer.readUInt8(this.offset);
        this.offset += 1;
        return v;
    }
    
    readShort() {
        const v = this.buffer.readUInt16BE(this.offset);
        this.offset += 2;
        return v;
    }
    
    readInt() {
        const v = this.buffer.readUInt32BE(this.offset);
        this.offset += 4;
        return v;
    }
    
    readLong() {
        const v = this.buffer.readBigInt64BE(this.offset);
        this.offset += 8;
        return Number(v); // Note: Precision loss for values > 2^53, but typical usage fits safe integer.
    }
    
    readBytes() {
        const len = this.readShort();
        const b = this.buffer.slice(this.offset, this.offset + len);
        this.offset += len;
        return b;
    }
    
    readString() {
        return this.readBytes().toString('utf8');
    }

    readRaw(len) {
        const b = this.buffer.slice(this.offset, this.offset + len);
        this.offset += len;
        return b;
    }
}

class PacketParser {
    constructor() {
        this.buffer = Buffer.alloc(0);
    }

    append(data) {
        this.buffer = Buffer.concat([this.buffer, data]);
    }

    next() {
        if (this.buffer.length < 4) {
            return null; // Not enough data for header
        }

        const payloadSize = this.buffer.readUInt32BE(0);
        const totalSize = 4 + payloadSize;

        if (this.buffer.length < totalSize) {
            return null; // Not enough data for full packet
        }

        // Extract packet payload
        // We skip the length header (4 bytes)
        const payloadBuf = this.buffer.slice(4, totalSize);
        
        // Remove processed data from buffer
        this.buffer = this.buffer.slice(totalSize);

        return this.parsePacket(payloadBuf, payloadSize);
    }

    parsePacket(buf, len) {
        const reader = new BufferReader(buf);
        const type = reader.readByte();
        
        // Default response object
        const res = { type };

        switch (type) {
            case MSG.RES_ADD_BLOCK:
            case MSG.RES_EOF:
            case MSG.RES_NEXT:
                break;

            case MSG.RES_START_DATA:
                res.uri = reader.readString();
                res.mime_type = reader.readString();
                res.encoding = reader.readString();
                res.length = reader.readLong();
                break;

            case MSG.RES_MAIN_LENGTH:
            case MSG.RES_MAIN_READ:
                res.length = reader.readLong();
                break;

            case MSG.RES_INSERT_BLOCK:
            case MSG.RES_CLOSE_BLOCK:
                res.block_id = reader.readInt();
                break;

            case MSG.RES_MESSAGE:
                res.code = reader.readShort();
                // To calculate remaining bytes for message and args, we rely on reader usage
                // Message
                res.message = reader.readString();
                // Args
                res.args = [];
                while (reader.offset < buf.length) {
                    res.args.push(reader.readString());
                }
                break;

            case MSG.RES_BLOCK_DATA: {
                // Payload: block_id(4) + data
                // len is the total payload size (Type + BlockID + Data).
                // Type(1) is consumed. BlockID(4) will be consumed.
                // dataLen = len - 1(Type) - 4(BlockID) = len - 5.
                const dataLen = len - 5;
                res.block_id = reader.readInt();
                res.bytes = reader.readRaw(dataLen);
                break;
            }

            case MSG.RES_ADD_BLOCK:
                break;

            case MSG.RES_INSERT_BLOCK:
                res.block_id = reader.readInt();
                break;
            
            case MSG.RES_CLOSE_BLOCK:
                res.block_id = reader.readInt();
                break;

            case MSG.RES_DATA: {
                // Payload: data
                // len is total payload size (Type + Data).
                // Type(1) is consumed.
                // dataLen = len - 1.
                const dataLen = len - 1;
                res.bytes = reader.readRaw(dataLen);
                break;
            }

            case MSG.RES_RESOURCE_REQUEST:
                res.uri = reader.readString();
                break;

            case MSG.RES_ABORT:
                res.mode = reader.readByte();
                res.code = reader.readShort();
                res.message = reader.readString();
                res.args = [];
                while (reader.offset < buf.length) {
                    res.args.push(reader.readString());
                }
                break;
            
            default:
                throw new Error(`Unknown response type: ${type}`);
        }

        return res;
    }
}

module.exports = {
    MSG,
    req_server_info,
    req_client_resource,
    req_continuous,
    req_missing_resource,
    req_reset,
    req_abort,
    req_join,
    req_eof,
    req_property,
    req_server_main,
    req_start_resource,
    req_start_main,
    req_data,
    req_close,
    PacketParser
};
