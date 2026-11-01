const bcrypt = require('bcrypt');

async function validatePassword(password, hashedPassword) {
    return await bcrypt.compare(password, hashedPassword);
}

module.exports = {
    validatePassword
}; 