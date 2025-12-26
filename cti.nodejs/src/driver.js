const net = require('net');
const tls = require('tls');
const { Session } = require('./session');

class Driver {
    getSession(uri, options = {}) {
        let host = 'localhost';
        let port = 8099;
        let useSSL = false;

        // Simple URI parsing
        // ctip://host:port/
        // ctips://host:port/
        
        let match = uri.match(/^ctips:\/\/([^:/]+):([0-9]+)\/?$/);
        if (match) {
            useSSL = true;
            host = match[1];
            port = parseInt(match[2], 10);
        } else {
            match = uri.match(/^ctips:\/\/([^:/]+)\/?$/);
            if (match) {
                useSSL = true;
                host = match[1];
            } else {
                match = uri.match(/^ctip:\/\/([^:/]+):([0-9]+)\/?$/);
                if (match) {
                    host = match[1];
                    port = parseInt(match[2], 10);
                } else {
                    match = uri.match(/^ctip:\/\/([^:/]+)\/?$/);
                    if (match) {
                        host = match[1];
                    }
                }
            }
        }

        let socket;
        if (useSSL) {
            // Options for SSL (e.g. self-signed certs) can be passed in options
            const tlsOptions = {
                rejectUnauthorized: options.rejectUnauthorized !== undefined ? options.rejectUnauthorized : true
            };
            socket = tls.connect(port, host, tlsOptions);
        } else {
            socket = net.connect(port, host);
        }

        return new Session(socket, options);
    }
}

module.exports = {
    Driver
};
