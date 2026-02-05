CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    embed TEXT,
    likes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO users (username, email, password) VALUES
    ('anxiety_queen', 'anxiety@doom.er', '$2a$10$6k8DZJaPCAPju/qO0nIAiuWkAqtEZ/nTsUjgYoXjOxFmsXGBtwWCO'),
    ('midnight_scroller', 'midnight@doom.er', '$2a$10$6k8DZJaPCAPju/qO0nIAiuWkAqtEZ/nTsUjgYoXjOxFmsXGBtwWCO'),
    ('doom_enthusiast', 'doom@doom.er', '$2a$10$6k8DZJaPCAPju/qO0nIAiuWkAqtEZ/nTsUjgYoXjOxFmsXGBtwWCO'),
    ('digital_void', 'digital@doom.er', '$2a$10$6k8DZJaPCAPju/qO0nIAiuWkAqtEZ/nTsUjgYoXjOxFmsXGBtwWCO'),
    ('scroll_walker', 'scroll@doom.er', '$2a$10$6k8DZJaPCAPju/qO0nIAiuWkAqtEZ/nTsUjgYoXjOxFmsXGBtwWCO'),
    ('doomer_admin', 'admin@doom.er', 'placeholder');

INSERT INTO posts (user_id, content, likes) VALUES
    (1, "Just spent 5 hours scrolling... help <a href='#'>🆘</a>", 2453),
    (2, "Can't sleep, might as well keep scrolling...", 1897),
    (3, "Another day, another endless scroll 🌀 <br><a href='#void'>#void</a>", 3211),
    (4, "The algorithm knows me better than I know myself 👁️ <br><i>we're all just data now</i>", 4521),
    (5, "Lost in the infinite feed, send help 📱<br><br><b>error 404:</b> peace of mind not found", 2876); 