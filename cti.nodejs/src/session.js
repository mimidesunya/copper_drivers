const { Writable } = require('stream');
const { 
    MSG, 
    PacketParser, 
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
    req_close 
} = require('./ctip2');

const { SingleResult, DirectoryResults } = require('./results');
const { StreamBuilder, FileBuilder } = require('./builder');

class IllegalStateError extends Error {
    constructor(message) {
        super(message);
        this.name = 'IllegalStateError';
    }
}

class MainOut extends Writable {
    constructor(session, options) {
        super(options);
        this.session = session;
        this.buffer = Buffer.alloc(MSG.CTI_BUFFER_SIZE);
        this.pos = 0;
    }


    
    // Easier Re-implementation of _write using recursion for backpressure support
    _write(chunk, encoding, callback) {
        let srcOff = 0;
        
        const processChunk = () => {
            if (srcOff >= chunk.length) {
                return callback();
            }
            
            const remaining = MSG.CTI_BUFFER_SIZE - this.pos;
            const copylen = Math.min(remaining, chunk.length - srcOff);
            chunk.copy(this.buffer, this.pos, srcOff, srcOff + copylen);
            this.pos += copylen;
            srcOff += copylen;

            if (this.pos >= MSG.CTI_BUFFER_SIZE) {
                const buf = req_data(this.buffer);
                this.pos = 0;
                if (!this.session.send(buf)) {
                    this.session.socket.once('drain', processChunk);
                    return;
                }
            }
            processChunk();
        };
        
        try {
            processChunk();
        } catch (err) {
            callback(err);
        }
    }

    _final(callback) {
        try {
            this.flush();
            this.session.send(req_eof());
            callback();
        } catch (err) {
            callback(err);
        }
    }
    
    flush() {
        if (this.pos > 0) {
            const slice = this.buffer.slice(0, this.pos);
            const buf = req_data(slice);
            this.session.send(buf);
            this.pos = 0;
        }
    }
}

class ResourceOut extends Writable {
    constructor(session, options) {
        super(options);
        this.session = session;
        this._closed = false;
        this.buffer = Buffer.alloc(MSG.CTI_BUFFER_SIZE);
        this.pos = 0;
    }

    _write(chunk, encoding, callback) {
        let srcOff = 0;
        
        const processChunk = () => {
            if (srcOff >= chunk.length) {
                return callback();
            }
            
            const remaining = MSG.CTI_BUFFER_SIZE - this.pos;
            const copylen = Math.min(remaining, chunk.length - srcOff);
            chunk.copy(this.buffer, this.pos, srcOff, srcOff + copylen);
            this.pos += copylen;
            srcOff += copylen;

            if (this.pos >= MSG.CTI_BUFFER_SIZE) {
                const buf = req_data(this.buffer);
                this.pos = 0;
                if (!this.session.send(buf)) {
                    this.session.socket.once('drain', processChunk);
                    return;
                }
            }
            processChunk();
        };
        
        try {
            processChunk();
        } catch (err) {
            callback(err);
        }
    }

    _final(callback) {
        if (!this._closed) {
            try {
                this.flush();
                this.session.send(req_eof());
                this._closed = true;
                callback();
            } catch (err) {
                callback(err);
            }
        } else {
            callback();
        }
    }
    
    flush() {
        if (this.pos > 0) {
            const slice = this.buffer.slice(0, this.pos);
            const buf = req_data(slice);
            this.session.send(buf);
            this.pos = 0;
        }
    }
}

class Resource {
    constructor(session, uri) {
        this.session = session;
        this.uri = uri;
        this.isMissing = true;
        this.out = null;
    }

    found(opts = {}) {
        const mimeType = opts.mime_type || 'text/css';
        const encoding = opts.encoding || '';
        const length = (opts.length !== undefined) ? opts.length : -1;
        
        this.session.send(req_start_resource(this.uri, mimeType, encoding, length));
        this.isMissing = false;
        this.out = new ResourceOut(this.session);
        return this.out;
    }

    finish() {
        if (this.out) {
            this.out.end();
        }
    }
}


class Session {
    /**
     * Creates a new Session.
     * @param {net.Socket|tls.TLSSocket} socket - The connected socket.
     * @param {Object} [options] - Configuration options.
     * @param {string} [options.user] - Authentication username.
     * @param {string} [options.password] - Authentication password.
     */
    constructor(socket, options = {}) {
        this.socket = socket;
        this.options = options;
        this.state = 0; // 0: init, 1: auth done, 2: transcoding, 3: closed
        
        // Output handlers
        this.results = new SingleResult(new StreamBuilder(process.stdout));
        this.messageFunc = (code, msg, args) => {
            console.error(`Message [${code}]: ${msg}`, args);
        };
        this.progressFunc = null;
        this.resolverFunc = null;

        // Internal buffers
        this.parser = new PacketParser();
        this._handshakeBuffer = Buffer.alloc(0);
        this._handshakeDone = false;
        this._sendBuffer = null; // Buffer for packets sent before handshake completes

        // State variables
        this.mainLength = null;
        this.mainRead = 0;
        this.builder = null;
        this.completionPromise = null;
        this.continuous = false; // continuous mode

        // Initialize connection
        this._initConnection();

        // Setup socket listeners
        this.socket.on('data', (data) => this._onData(data));
        this.socket.on('error', (err) => this._onError(err));
        this.socket.on('close', () => this._onClose());
    }

    _initConnection() {
        const encoding = this.options.encoding || 'UTF-8';
        const user = this.options.user || '';
        const password = this.options.password || '';

        // Authenticate
        this.socket.write(`CTIP/2.0 ${encoding}\n`);
        const authLine = `PLAIN: ${user} ${password}\n`;
        this.socket.write(authLine);
        
        // Handshake buffer for robust parsing
        this._handshakeBuffer = Buffer.alloc(0);
        this._handshakeDone = false;
    }

    _onData(data) {
        if (!this._handshakeDone) {
            this._handshakeBuffer = Buffer.concat([this._handshakeBuffer, data]);
            
            // Wait until we have at least 3 bytes ("NG ") or 4 bytes ("OK \n")
            if (this._handshakeBuffer.length < 3) return;

            const head = this._handshakeBuffer.slice(0, 4).toString('utf8');
            if (head === 'OK \n') {
                this._handshakeDone = true;
                const rest = this._handshakeBuffer.slice(4);
                this._handshakeBuffer = null; // Free memory

                // Flush pending requests AFTER we are authenticated
                this._flushSendBuffer();
                
                if (rest.length > 0) {
                    this.parser.append(rest);
                    this._processPackets();
                }
            } else if (this._handshakeBuffer.toString('utf8').startsWith('NG ')) {
                // Return full error message for debugging
                const msg = this._handshakeBuffer.toString('utf8');
                this._onError(new Error('Authentication failure: ' + JSON.stringify(msg)));
                this.socket.end();
            } else {
                 if (this._handshakeBuffer.length > 100) { 
                     // Safety break: if we received too much without matching OK/NG, something is wrong.
                     this._onError(new Error('Invalid handshake response'));
                     this.socket.end();
                 }
                 // Wait for more data
            }
            return;
        }


        this.parser.append(data);
        this._enqueueProcessPackets();
    }

    // Serialize packet processing to avoid race conditions
    _enqueueProcessPackets() {
        if (!this._processingPromise) {
            this._processingPromise = Promise.resolve();
        }
        this._processingPromise = this._processingPromise.then(() => this._processPackets());
    }

    async _processPackets() {
        let pkt;
        while ((pkt = this.parser.next())) {
            await this._handlePacket(pkt);
        }
    }

    async _handlePacket(res) {
        const type = res.type;

        switch (type) {
            case MSG.RES_START_DATA:
                if (this.builder) {
                    await this.builder.finish();
                    await this.builder.dispose();
                }
                this.builder = this.results.nextBuilder(res);
                break;

            case MSG.RES_BLOCK_DATA:
                if (this.builder) await this.builder.write(res.block_id, res.bytes);
                break;

            case MSG.RES_ADD_BLOCK:
                if (this.builder) this.builder.addBlock();
                break;

            case MSG.RES_INSERT_BLOCK:
                if (this.builder) this.builder.insertBlockBefore(res.block_id);
                break;
            
            case MSG.RES_CLOSE_BLOCK:
                if (this.builder) this.builder.closeBlock(res.block_id);
                break;

            case MSG.RES_DATA:
                if (this.builder) await this.builder.serialWrite(res.bytes);
                break;

            case MSG.RES_MESSAGE:
                if (this.messageFunc) {
                    this.messageFunc(res.code, res.message, res.args);
                }
                break;

            case MSG.RES_MAIN_LENGTH:
                this.mainLength = res.length;
                if (this.progressFunc) this.progressFunc(this.mainLength, this.mainRead);
                break;

            case MSG.RES_MAIN_READ:
                this.mainRead = res.length;
                if (this.progressFunc) this.progressFunc(this.mainLength, this.mainRead);
                break;

            case MSG.RES_RESOURCE_REQUEST: {
                const r = new Resource(this, res.uri);
                if (this.resolverFunc) {
                    await Promise.resolve(this.resolverFunc(res.uri, r));
                }
                r.finish();
                if (r.isMissing) {
                    this.send(req_missing_resource(res.uri));
                }
                break;
            }

            case MSG.RES_ABORT:
                 if (this.builder) {
                     if (res.mode === 0) await this.builder.finish();
                     await this.builder.dispose();
                     this.builder = null;
                 }
                if (this._rejectCompletion) {
                    this._rejectCompletion(new Error(`Transcoding aborted: ${res.message}`));
                }
                this.mainLength = null;
                this.mainRead = 0;
                this.state = 1; // Back to authenticated state? or stay?
                // Depending on mode?
                break;
            
            case MSG.RES_EOF:
                if (this.builder) {
                    await this.builder.finish();
                    await this.builder.dispose();
                    this.builder = null;
                }
                if (this._resolveCompletion) {
                    this._resolveCompletion();
                }
                this.mainLength = null;
                this.mainRead = 0;
                this.state = 1;
                this._resolveCompletion();
                break;

            case MSG.RES_NEXT:
                this.state = 1;
                this._resolveCompletion();
                break;
        }
    }

    _onError(err) {
        console.error('Session Error:', err);
        if (this.completionReject) {
            this.completionReject(err);
            this.completionReject = null;
            this.completionResolve = null;
        }
    }

    _onClose() {
        // console.log('DEBUG: Session Socket closed');
        this.state = 3;
        if (this.builder) {
             this.builder.dispose(); 
        }
        if (this._rejectCompletion) {
            this._rejectCompletion(new Error('Connection closed unexpectedly during transcoding'));
            this._rejectCompletion = null;
            this._resolveCompletion = null;
        }
    }
    
    _resolveCompletion() {
        if (this._resolveCompletion) {
            this._resolveCompletion();
            this._resolveCompletion = null;
            this._rejectCompletion = null;
        }
    }

    send(data) {
        if (this.state >= 3) {
            throw new IllegalStateError("Session is closed");
        }
        if (!this._handshakeDone) {
            if (!this._sendBuffer) this._sendBuffer = [];
            this._sendBuffer.push(data);
             // Return true to pretend write success, or handle flow control strictly?
             // Since we are buffering in memory, we take responsibility.
             return true;
        }
        return this.socket.write(data);
    }
    
    _flushSendBuffer() {
        if (this._sendBuffer && this._sendBuffer.length > 0) {
            for (const chunk of this._sendBuffer) {
                this.socket.write(chunk);
            }
            this._sendBuffer = null;
        }
    }
    
    // --- Public API ---

    setResults(results) {
        if (this.state >= 2) throw new IllegalStateError("Main content already sent");
        this.results = results;
    }
    
    setOutputAsFile(file) {
        this.setResults(new SingleResult(new FileBuilder(file)));
    }
    
    setOutputAsDirectory(dir, prefix = '', suffix = '') {
        this.setResults(new DirectoryResults(dir, prefix, suffix));
    }
    
    setOutputAsStream(stream) {
        this.setResults(new SingleResult(new StreamBuilder(stream)));
    }

    setMessageFunc(func) {
        if (this.state >= 2) throw new IllegalStateError("Main content already sent");
        this.messageFunc = func;
    }
    
    setProgressFunc(func) {
        if (this.state >= 2) throw new IllegalStateError("Main content already sent");
        this.progressFunc = func;
    }
    
    setResolverFunc(func) {
        if (this.state >= 2) throw new IllegalStateError("Main content already sent");
        this.resolverFunc = func;
        this.send(req_client_resource(func ? 1 : 0));
    }
    
    setContinuous(continuous) {
        if (this.state >= 2) throw new IllegalStateError("Main content already sent");
        this.send(req_continuous(continuous));
    }
    
    setProperty(name, value) {
        if (this.state >= 2) throw new IllegalStateError("Main content already sent");
        this.send(req_property(name, value));
    }
    
    resource(uri, opts = {}) {
        if (this.state >= 2) throw new IllegalStateError("Main content already sent");
        const mimeType = opts.mime_type || 'text/css';
        const encoding = opts.encoding || '';
        const length = (opts.length !== undefined) ? opts.length : -1;
        
        this.send(req_start_resource(uri, mimeType, encoding, length));
        return new ResourceOut(this);
    }
    
    /**
     * Starts transcoding logic.
     * @param {string} [uri='.'] - Identification URI for the document.
     * @param {Object} [opts] - Options.
     * @param {string} [opts.mimeType='text/html'] - MIME type of the input.
     * @param {string} [opts.encoding='UTF-8'] - Encoding of the input.
     * @param {number} [opts.length=-1] - Total length of the input if known.
     * @returns {stream.Writable} - Writable stream to send the document content.
     */
    transcode(uri = '.', opts = {}) {
         if (this.state >= 2) throw new IllegalStateError("Main content already sent");
         const mimeType = opts.mimeType || 'text/html';
         const encoding = opts.encoding || 'UTF-8';
         const length = (opts.length === undefined) ? -1 : opts.length;

         // Reset state for new transcoding
         this.mainLength = null;
         this.mainRead = 0;
         this.builder = null;
         
         let resolve, reject;
         this.completionPromise = new Promise((r, j) => {
             resolve = r;
             reject = j;
         });
         // Attach resolvers to the instance so handlePacket can use them
         this._resolveCompletion = resolve;
         this._rejectCompletion = reject;

         this.send(req_start_main(uri, mimeType, encoding, length));
         
         // Return a writable stream for the user to pipe content into
         return new MainOut(this);
    }
    
    transcodeServer(uri) {
        if (this.state >= 2) throw new IllegalStateError("Main content already sent");
        this.send(req_server_main(uri));
        this.state = 2;
        this.completionPromise = new Promise((resolve, reject) => {
             this.completionResolve = resolve;
             this.completionReject = reject;
         });
    }
    
    /**
     * Waits for the transcoding process to complete.
     * @returns {Promise<void>} - Resolves when transcoding is finished.
     */
    async waitForCompletion() {
        if (this.completionPromise) {
            await this.completionPromise;
        }
    }
    
    abort(mode) {
        if (this.state >= 2) {
             this.send(req_abort(mode));
        }
    }
    
    reset() {
        if (this.state >= 3) throw new IllegalStateError("Session is closed");
        if (this.socket) this.send(req_reset());
        this.progressFunc = null;
        this.messageFunc = null;
        this.resolverFunc = null;
        this.builder = null;
        this.mainLength = null;
        this.mainRead = 0;
        this.results = new SingleResult(new StreamBuilder(process.stdout));
        this.state = 1;
        this.completionPromise = null;
    }
    
    /**
     * Sends a JOIN request (for combining multiple documents).
     * @throws {Error} If session is closed.
     */
    join() {
        if (this.state >= 3) throw new IllegalStateError("Session is closed");
        this.send(req_join());
        this.state = 2;
        this.completionPromise = new Promise((resolve, reject) => {
             this.completionResolve = resolve;
             this.completionReject = reject;
         });
    }

    close() {
        if (this.state >= 3) return;
        try {
            this.send(req_close());
        } catch (e) {
            // ignore
        }
        this.state = 3;
        this.socket.end();
    }
}

module.exports = {
    Session
};
