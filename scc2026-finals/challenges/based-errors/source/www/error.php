<?php
require_once 'db.php';
require_once 'user.php';
require_once 'project.php';

$errorId = $_GET['error'] ?? null;

// Fetch project name
$stmt = $db->prepare('SELECT name FROM projects WHERE project_id = :project_id');
$stmt->execute([':project_id' => $projectId]);
$project = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$project) {
    echo '<p>Project not found.</p>';
    exit;
}

$prefix = 'project_' . (int)$projectId;

// Fetch error details
$stmt = $db->prepare("SELECT * FROM `{$prefix}_errors` WHERE error_id = :error_id");
$stmt->execute([':error_id' => $errorId]);
$error = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$error) {
    echo '<p>Error not found.</p>';
    exit;
}

// Get custom field keys for this project
$customFields = get_custom_field_keys($projectId);

require 'header.php';
?>
<style>
.container {
    max-width: 1200px;
}
</style>
<h2>Error Details</h2>
<table>
    <tr><th>Project</th><td><?= htmlspecialchars($project['name']) ?></td></tr>
    <tr><th>Type</th><td><?= htmlspecialchars($error['type']) ?></td></tr>
    <tr><th>Filename</th><td><?= htmlspecialchars($error['filename']) ?></td></tr>
    <tr><th>Line</th><td><?= htmlspecialchars($error['line_number']) ?></td></tr>
    <tr><th>Column</th><td><?= htmlspecialchars($error['column_number']) ?></td></tr>
    <tr><th>Count</th><td><?= htmlspecialchars($error['count']) ?></td></tr>
    <tr><th>First Seen</th><td><?= htmlspecialchars($error['first_timestamp']) ?></td></tr>
    <tr><th>Last Seen</th><td><?= htmlspecialchars($error['last_timestamp']) ?></td></tr>
</table>

<h3>Occurrences</h3>
<table>
    <thead>
        <tr>
            <th>Timestamp</th>
            <th>Message</th>
            <?php foreach ($customFields as $field): ?>
            <th><?= htmlspecialchars($field) ?></th>
            <?php endforeach; ?>
            <th>Stack Trace</th>
        </tr>
    </thead>
    <tbody>
    <?php
    $stmt = $db->prepare("SELECT * FROM `{$prefix}_error_reports` WHERE error_id = :error_id ORDER BY timestamp DESC");
    $stmt->execute([':error_id' => $errorId]);
    $reports = $stmt->fetchAll(PDO::FETCH_ASSOC);
    foreach ($reports as $report):
    ?>
        <tr>
            <td><?= htmlspecialchars($report['timestamp']) ?></td>
            <td><?= nl2br(htmlspecialchars($report['message'])) ?></td>
            <?php foreach ($customFields as $field): ?>
            <td><?= htmlspecialchars($report[$field] ?? '') ?></td>
            <?php endforeach; ?>
            <td><pre><?= htmlspecialchars($report['stack_trace'] ?? '') ?></pre></td>
        </tr>
    <?php endforeach; ?>
    </tbody>
</table>
<?php
require 'footer.php';
