<?php
require_once 'db.php';
require_once 'user.php';
require 'header.php';

// Handle project creation form submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST['project_name'])) {
    $user_id = $_SERVER['PHP_AUTH_USER'];
    create_project($_POST['project_name'], $user_id);
    echo '<p>Project created successfully.</p>';
}

// Fetch list of projects
$stmt = $db->query('SELECT * FROM projects');
$projects = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>
<h2>Projects</h2>
<ul>
<?php foreach ($projects as $project): ?>
    <li>
        <a href="/errors.php?project_id=<?= htmlspecialchars($project['project_id']) ?>"><?= htmlspecialchars($project['name']) ?></a>
        (owner: <?= htmlspecialchars($project['user_id']) ?>)
    </li>
<?php endforeach; ?>
</ul>

<h3>Create New Project</h3>
<form method="post" action="">
    <label for="project_name">Project Name:</label>
    <input type="text" id="project_name" name="project_name" required />
    <button type="submit">Create Project</button>
</form>
<?php
require 'footer.php';
?>