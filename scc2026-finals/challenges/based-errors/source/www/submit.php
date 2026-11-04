<?php
ini_set('display_errors', '1');
error_reporting(E_ALL);

header('Content-Type: application/json');

require_once 'db.php';

$projectId = (int)$_GET['project_id'];
$prefix = 'project_' . $projectId;

$jsonBody = file_get_contents('php://input');
$payload = json_decode($jsonBody, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    echo json_encode(['error' => 'Invalid JSON payload']);
    exit;
}

$baseFields = ['filename', 'lineNumber', 'errorMessage', 'errorType', 'columnNumber', 'stackTrace'];
$customFields = get_custom_field_keys($projectId);

foreach (array_keys($payload) as $key) {
    if (!in_array($key, $baseFields) && !in_array($key, $customFields)) {
        echo json_encode(['error' => "Unsupported field: $key"]);
        exit;
    }
}

$filename = $payload['filename'] ?? null;
$lineNumber = $payload['lineNumber'] ?? null;
$errorType = $payload['errorType'] ?? null;
$columnNumber = $payload['columnNumber'] ?? null;
$errorMessage = $payload['errorMessage'] ?? null;
$stackTrace = $payload['stackTrace'] ?? null;
try {
    // Check if this error already exists
    $stmt = $db->prepare("SELECT error_id, `count` FROM `{$prefix}_errors` WHERE type = ? AND filename = ? AND line_number = ?");
    $stmt->execute([$errorType, $filename, $lineNumber]);
    $error = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($error) {
        $errorId = $error['error_id'];
        $stmt = $db->prepare("UPDATE `{$prefix}_errors` SET `count` = `count` + 1, last_timestamp = NOW() WHERE error_id = ?");
        $stmt->execute([$errorId]);
    } else {
        $stmt = $db->prepare("INSERT INTO `{$prefix}_errors` (type, filename, line_number, column_number, `count`, first_timestamp, last_timestamp) VALUES (?, ?, ?, ?, 1, NOW(), NOW())");
        $stmt->execute([$errorType, $filename, $lineNumber, $columnNumber]);
        $errorId = $db->lastInsertId();
    }

    // Build dynamic INSERT for error_reports with custom columns using positional placeholders.
    $columns = ['error_id', 'message', 'timestamp', 'column_number', 'stack_trace'];
    $placeholders = ['?', '?', 'NOW()', '?', '?'];
    $params = [$errorId, $errorMessage, $columnNumber, $stackTrace];

    foreach ($customFields as $field) {
        // if (array_key_exists($field, $payload)) {
            $columns[] = "`$field`";
            $placeholders[] = '?';
            $params[] = $payload[$field];
        // }
    }

    $sql = "INSERT INTO `{$prefix}_error_reports` (" . implode(', ', $columns) . ") VALUES (" . implode(', ', $placeholders) . ")";
    $stmt = $db->prepare($sql);
    $stmt->execute($params);

    echo json_encode([
        'error' => false,
    ]);
} catch (Exception $e) {
    echo json_encode([
        'error' => 'Database error: ' . $e->getMessage(),
    ]);
    exit;
}
?>
