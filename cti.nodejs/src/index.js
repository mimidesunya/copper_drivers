const { Driver } = require('./driver');
const { Session } = require('./session');

function get_driver(uri) {
    return new Driver();
}

function get_session(uri, options = {}) {
    return new Driver().getSession(uri, options);
}

module.exports = {
    Driver,
    Session,
    get_driver,
    get_session
};
