<?php
require_once 'db.php';
require_once 'user.php';
require_once 'project.php';

// Fetch project name
$stmt = $db->prepare('SELECT name FROM projects WHERE project_id = :project_id');
$stmt->execute([':project_id' => $projectId]);
$project = $stmt->fetch(PDO::FETCH_ASSOC);
if (!$project) {
    echo '<p>Project not found.</p>';
    exit;
}

$prefix = 'project_' . (int)$projectId;

require 'header.php';
?>
<style>
.container {
    max-width: 1200px;
}
</style>
<h2>Errors for <?= htmlspecialchars($project['name']) ?></h2>
<table>
    <thead>
        <tr>
            <th>Type</th>
            <th>Filename</th>
            <th>Line</th>
            <th>Count</th>
            <th>First Seen</th>
            <th>Last Seen</th>
            <th>Actions</th>
        </tr>
    </thead>
    <tbody>
    <?php
    $stmt = $db->query("SELECT * FROM `{$prefix}_errors` ORDER BY last_timestamp DESC");
    $errors = $stmt->fetchAll(PDO::FETCH_ASSOC);
    foreach ($errors as $error):
    ?>
        <tr>
            <td><?= htmlspecialchars($error['type']) ?></td>
            <td><?= htmlspecialchars($error['filename']) ?></td>
            <td><?= htmlspecialchars($error['line_number']) ?></td>
            <td><?= htmlspecialchars($error['count']) ?></td>
            <td><?= htmlspecialchars($error['first_timestamp']) ?></td>
            <td><?= htmlspecialchars($error['last_timestamp']) ?></td>
            <td><a href="/error.php?project_id=<?= htmlspecialchars($projectId) ?>&error=<?= htmlspecialchars($error['error_id']) ?>">View Occurrences</a></td>
        </tr>
    <?php endforeach; ?>
    </tbody>
</table>
<?php
require 'footer.php';
