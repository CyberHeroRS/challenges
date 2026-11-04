<?php
$projectId = $_GET['project_id'] ?? null;
if ($projectId === null) {
    echo '<p>Project ID not specified.</p>';
    require 'footer.php';
    exit;
}

if (isset($user)) {
    // Verify that the current user is the owner of the project
    $stmt = $db->prepare('SELECT user_id FROM projects WHERE project_id = ?');
    $stmt->execute([$projectId]);
    $ownerId = $stmt->fetchColumn();
    if ($ownerId === false) {
        echo '<p>Project not found.</p>';
        require 'footer.php';
        exit;
    }
    if ($ownerId !== $user) {
        echo '<p>You are not the owner of this project.</p>';
        require 'footer.php';
        exit;
    }
}

?>