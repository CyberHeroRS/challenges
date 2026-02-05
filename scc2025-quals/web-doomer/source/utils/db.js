const pool = require('../config/database');
const bcrypt = require('bcrypt');

async function waitForDb() {
    const maxRetries = 30;
    let retries = 0;
    
    while (retries < maxRetries) {
        try {
            const connection = await pool.getConnection();
            connection.release();
            console.log('[+] Database connection successful');
            return;
        } catch (error) {
            retries++;
            console.log(`[*] Waiting for database... (attempt ${retries}/${maxRetries})`);
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
    
    throw new Error('[-] Failed to connect to database after maximum retries');
}

async function initAdminUser() {
    try {
        const adminPassword = process.env.ADMIN_PASSWORD;
        if (!adminPassword) {
            throw new Error('ADMIN_PASSWORD environment variable not set');
        }

        const hashedPassword = await bcrypt.hash(adminPassword, 10);
        const connection = await pool.getConnection();
        
        await connection.query(
            'UPDATE users SET password = ? WHERE username = ?',
            [hashedPassword, 'doomer_admin']
        );
        
        connection.release();
        console.log('[+] Admin password updated successfully');
    } catch (error) {
        console.error('[-] Failed to update admin password:', error);
        throw error;
    }
}

module.exports = {
    waitForDb,
    initAdminUser
}; 