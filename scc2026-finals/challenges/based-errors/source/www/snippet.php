<?php
header("Content-type: text/javascript");

require_once 'db.php';
$projectId = $_GET["project_id"];
$submitUrl = ((isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on') ? 'https' : 'http') . '://' . $_SERVER['HTTP_HOST'] . '/submit.php?project_id=' . urlencode($projectId);

$prefix = 'project_' . (int)$projectId;

// Fetch custom fields for this project
$customFields = [];
$stmt = $db->query("SHOW TABLES LIKE '{$prefix}_custom_fields'");
if ($stmt->rowCount() > 0) {
    $stmt = $db->query("SELECT `key`, `value` FROM `{$prefix}_custom_fields`");
    $customFields = $stmt->fetchAll(PDO::FETCH_KEY_PAIR);
}
?>
window.addEventListener("error", async (event) => {
    await fetch('<?= $submitUrl ?>', {
        method: 'POST',
        body: JSON.stringify({
            'filename': event.filename,
            'lineNumber': event.lineno,
            'errorMessage': event.message,
            'errorType': event.error.name,
            'columnNumber': event.colno,
            'stackTrace': event.error.stack
<?php foreach ($customFields as $fieldName => $fieldValue): ?>
            ,'<?= $fieldName ?>': <?= $fieldValue ?>
<?php endforeach; ?>
        })
    })
});
