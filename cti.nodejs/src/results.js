const path = require('path');
const { FileBuilder, NullBuilder } = require('./builder');

class SingleResult {
    constructor(builder, finishFunc = null) {
        this.builder = builder;
        this.finishFunc = finishFunc;
    }

    nextBuilder(opts = {}) {
        if (!this.builder) {
            return new NullBuilder();
        }

        if (this.finishFunc) {
            this.finishFunc(opts);
        }

        const b = this.builder;
        this.builder = null; // Single use
        return b;
    }
}

class DirectoryResults {
    constructor(dir, prefix = '', suffix = '') {
        this.dir = dir;
        this.prefix = prefix;
        this.suffix = suffix;
        this.counter = 0;
    }

    nextBuilder(opts = {}) {
        this.counter++;
        const filename = `${this.prefix}${this.counter}${this.suffix}`;
        const filepath = path.join(this.dir, filename);
        return new FileBuilder(filepath);
    }
}

module.exports = {
    SingleResult,
    DirectoryResults
};
