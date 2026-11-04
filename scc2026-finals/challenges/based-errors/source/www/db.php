<?php
// Disable error reporting and logging
error_reporting(0);
ini_set('display_errors', '0');
// ini_set('log_errors', '0');

$host = getenv('MYSQL_HOST') ?: 'localhost';
$port = getenv('MYSQL_PORT') ?: '3306';
$dbname = getenv('MYSQL_DATABASE') ?: 'test';
$user = getenv('MYSQL_USER') ?: 'root';
$password = getenv('MYSQL_PASSWORD') ?: '';

$dsn = "mysql:host=$host;port=$port;dbname=$dbname;charset=utf8mb4";

$db = new PDO($dsn, $user, $password);
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

function get_custom_fields($projectId) {
    global $db;
    $table = 'project_' . (int)$projectId . '_custom_fields';
    $stmt = $db->query("SHOW TABLES LIKE '$table'");
    if ($stmt->rowCount() === 0) {
        return [];
    }
    $stmt = $db->query("SELECT `key`, `value` FROM `$table`");
    return $stmt->fetchAll(PDO::FETCH_KEY_PAIR);
}

function get_custom_field_keys($projectId) {
    $keys = array_keys(get_custom_fields($projectId));
    sort($keys, SORT_STRING | SORT_FLAG_CASE);
    return $keys;
}

function create_tables($projectId) {
    global $db;
    $prefix = 'project_' . (int)$projectId;

    $db->exec("CREATE TABLE IF NOT EXISTS `{$prefix}_errors` (
        error_id INT AUTO_INCREMENT PRIMARY KEY,
        `type` VARCHAR(100) NOT NULL,
        filename VARCHAR(255) NOT NULL,
        line_number INT NOT NULL,
        column_number INT NOT NULL,
        `count` INT NOT NULL DEFAULT 1,
        first_timestamp DATETIME NOT NULL DEFAULT NOW(),
        last_timestamp DATETIME NOT NULL DEFAULT NOW()
    ) ENGINE=InnoDB");

    $db->exec("CREATE TABLE IF NOT EXISTS `{$prefix}_error_reports` (
        report_id INT AUTO_INCREMENT PRIMARY KEY,
        error_id INT NOT NULL,
        message TEXT NOT NULL,
        `timestamp` DATETIME NOT NULL DEFAULT NOW(),
        column_number INT,
        stack_trace TEXT,
        CONSTRAINT `fk_{$prefix}_reports_error` FOREIGN KEY (error_id) REFERENCES `{$prefix}_errors`(error_id) ON DELETE CASCADE
    ) ENGINE=InnoDB");

    $db->exec("CREATE TABLE IF NOT EXISTS `{$prefix}_custom_fields` (
        field_id INT AUTO_INCREMENT PRIMARY KEY,
        `key` VARCHAR(255) NOT NULL,
        `value` TEXT
    ) ENGINE=InnoDB");
}

function create_project($project_name, $user_id, $flag) {
    global $db;
    $stmt = $db->prepare('INSERT INTO projects (name, user_id, flag) VALUES (?, ?, ?)');
    $stmt->execute([$project_name, $user_id, $flag]);
    $newProjectId = $db->lastInsertId();
    create_tables($newProjectId);
}

function add_custom_field_column($projectId, $key) {
    global $db;
    $prefix = 'project_' . (int)$projectId;
    // Validate column name to prevent SQL injection (allow only alphanumeric and underscore)
    if (!preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/', $key)) {
        die('Invalid column name');
    }
    $db->exec("ALTER TABLE `{$prefix}_error_reports` ADD COLUMN `{$key}` TEXT");
}

function drop_custom_field_column($projectId, $key) {
    global $db;
    $prefix = 'project_' . (int)$projectId;
    // Validate column name to prevent SQL injection (allow only alphanumeric and underscore)
    if (!preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/', $key)) {
        die('Invalid column name');
    }
    $db->exec("ALTER TABLE `{$prefix}_error_reports` DROP COLUMN `{$key}`");
}

function init_db() {
    global $db;
    
    error_reporting(E_ALL);
    ini_set('log_errors', '1');
    
    echo "Initializing db...";
    echo $db->exec("DROP TABLE IF EXISTS projects;");
    echo $db->exec("CREATE TABLE IF NOT EXISTS projects (
        project_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        user_id VARCHAR(255) NOT NULL,
        flag VARCHAR(255) NOT NULL
    ) ENGINE=InnoDB;");

    echo "Creating demo project...";
    create_project("demo", "demo", "I have no flag :(");

    echo "Creating victim project...";
    create_project("victim", "victim", getenv("FLAG"));

    echo "DONE";
}
if (php_sapi_name() === 'cli') {
    init_db();
}