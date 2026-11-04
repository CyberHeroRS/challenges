const FLAG = process.env.FLAG || "SCC{fake_flag}";
const PORT = process.env.PORT || 3000;
const BASE_URL = process.env.BASE_URL + ":" + PORT || `http://localhost:${PORT}`;

module.exports = { FLAG, PORT, BASE_URL };
