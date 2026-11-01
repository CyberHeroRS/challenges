CREATE DATABASE IF NOT EXISTS spyme;
USE spyme;

-- Disable foreign key checks temporarily to allow any order of inserts
SET FOREIGN_KEY_CHECKS=0;

-- Drop table if exists to ensure clean state
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    secret_code VARCHAR(36) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    codename VARCHAR(255),
    specialization VARCHAR(255),
    status ENUM('Active', 'Under Investigation', 'Training'),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TEMPORARY TABLE random_ids (
    id INT NOT NULL,
    ord INT NOT NULL AUTO_INCREMENT PRIMARY KEY
);

INSERT INTO random_ids (id)
SELECT DISTINCT number
FROM (
    SELECT FLOOR(1 + RAND() * 300) as number
    FROM information_schema.columns
    LIMIT 1000
) AS numbers
LIMIT 12;

-- Insert initial users with random IDs
INSERT INTO users (id, first_name, last_name, username, secret_code, is_admin, codename, specialization, status, notes)
SELECT 
    r.id,
    CASE r.ord
        WHEN 1 THEN 'Gazda'
        WHEN 2 THEN 'Ilija'
        WHEN 3 THEN 'Petar'
        WHEN 4 THEN 'Danica'
        WHEN 5 THEN 'Sonja'
        WHEN 6 THEN 'Djura'
        WHEN 7 THEN 'Mirko'
        WHEN 8 THEN 'Ana'
        WHEN 9 THEN 'Dragan'
        WHEN 10 THEN 'Vesna'
        WHEN 11 THEN 'Branko'
        WHEN 12 THEN 'Zoran'
    END,
    CASE r.ord
        WHEN 1 THEN 'Gazdinovic'
        WHEN 2 THEN 'Cvorovic'
        WHEN 3 THEN 'Jakovljevic'
        WHEN 4 THEN 'Cvorovic'
        WHEN 5 THEN 'Cvorovic'
        WHEN 6 THEN 'Cvorovic'
        WHEN 7 THEN 'Nikic'
        WHEN 8 THEN 'Petrovic'
        WHEN 9 THEN 'Nikolic'
        WHEN 10 THEN 'Markovic'
        WHEN 11 THEN 'Simic'
        WHEN 12 THEN 'Mihajlovic'
    END,
    CASE r.ord
        WHEN 1 THEN 'admin'
        WHEN 2 THEN 'icvorovic'
        WHEN 3 THEN 'pjakovljevic'
        WHEN 4 THEN 'dcvorovic'
        WHEN 5 THEN 'scvorovic'
        WHEN 6 THEN 'djcvorovic'
        WHEN 7 THEN 'mnikic'
        WHEN 8 THEN 'apetrovic'
        WHEN 9 THEN 'dnikolic'
        WHEN 10 THEN 'vmarkovic'
        WHEN 11 THEN 'bsimic'
        WHEN 12 THEN 'zmihajlovic'
    END,
    UUID(),
    CASE r.ord WHEN 1 THEN TRUE ELSE FALSE END,
    CASE r.ord
        WHEN 1 THEN 'Director'
        WHEN 2 THEN 'Agent Cvorovic'
        WHEN 3 THEN 'Agent Jakovljevic'
        WHEN 4 THEN 'Agent Danica'
        WHEN 5 THEN 'Agent Sonja'
        WHEN 6 THEN 'Agent Djura'
        WHEN 7 THEN 'Agent Phantom'
        WHEN 8 THEN 'Agent Shadow'
        WHEN 9 THEN 'Agent Dragon'
        WHEN 10 THEN 'Agent Viper'
        WHEN 11 THEN 'Agent Ghost'
        WHEN 12 THEN 'Agent Enigma'
    END,
    CASE r.ord
        WHEN 1 THEN 'Administration'
        WHEN 2 THEN 'Counter Intelligence'
        WHEN 3 THEN 'Deep Cover Operations'
        WHEN 4 THEN 'Domestic Surveillance'
        WHEN 5 THEN 'Field Operations'
        WHEN 6 THEN 'Intelligence Analysis'
        WHEN 7 THEN 'Cyber Operations'
        WHEN 8 THEN 'Covert Surveillance'
        WHEN 9 THEN 'Asset Recruitment'
        WHEN 10 THEN 'Signals Intelligence'
        WHEN 11 THEN 'Black Operations'
        WHEN 12 THEN 'Cryptography'
    END,
    CASE r.ord
        WHEN 1 THEN 'Active'
        WHEN 2 THEN 'Active'
        WHEN 3 THEN 'Under Investigation'
        WHEN 4 THEN 'Active'
        WHEN 5 THEN 'Training'
        WHEN 6 THEN 'Active'
        WHEN 7 THEN 'Active'
        WHEN 8 THEN 'Active'
        WHEN 9 THEN 'Under Investigation'
        WHEN 10 THEN 'Active'
        WHEN 11 THEN 'Training'
        WHEN 12 THEN 'Active'
    END,
    CASE r.ord
        WHEN 1 THEN 'Head of Balkan Intelligence Bureau'
        WHEN 2 THEN 'Highly paranoid, sees foreign agents everywhere'
        WHEN 3 THEN 'Suspected western sympathizer'
        WHEN 4 THEN 'Expert in neighborhood watch operations'
        WHEN 5 THEN 'New recruit, shows promise'
        WHEN 6 THEN 'Specializes in pattern recognition'
        WHEN 7 THEN 'Expert in studying high-value targets, such as Johnny Walker'
        WHEN 8 THEN 'Specializes in urban surveillance and tracking'
        WHEN 9 THEN 'Suspected of running unauthorized operations'
        WHEN 10 THEN 'Expert in communications interception'
        WHEN 11 THEN 'Promising recruit with unique infiltration methods'
        WHEN 12 THEN 'Master of codes and ciphers, suspected double agent'
    END
FROM random_ids r;

CREATE TABLE id_sequence (
    next_id INT NOT NULL DEFAULT 301
);
INSERT INTO id_sequence VALUES (301);

DROP TEMPORARY TABLE IF EXISTS random_ids;

SET FOREIGN_KEY_CHECKS=1;
