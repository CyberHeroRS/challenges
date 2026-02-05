const processWhitelistData = (data) => {
    const result = {};
    
    function processObject(obj) {
        for (const key in obj) {
            const value = obj[key];
            if (value && typeof value === 'object') {
                result[key] = result[key] || {};
                Object.assign(result[key], processObject(value));
            } else {
                result[key] = value;
            }
        }
        return result;
    }

    return processObject(data);
};

const encodeJsonToBase64 = (data) => {
    return Buffer.from(JSON.stringify(data)).toString('base64');
};

const decodeBase64ToJson = (base64Str) => {
    return JSON.parse(Buffer.from(base64Str, 'base64').toString());
};

const validateUrl = (url) => {
    if (!url || typeof url !== 'string') {
        throw new Error('Invalid URL');
    }

    try {
        const urlObj = new URL(url);
        if (!urlObj.protocol || !['http:', 'https:'].includes(urlObj.protocol)) {
            throw new Error('URL must use HTTP or HTTPS protocol');
        }
        return urlObj;
    } catch (error) {
        throw new Error('Invalid URL format');
    }
};

const sanitizeFilename = (filename) => {
    return filename.replaceAll("../", "");
};

module.exports = {
    processWhitelistData,
    encodeJsonToBase64,
    decodeBase64ToJson,
    validateUrl,
    sanitizeFilename
}; 