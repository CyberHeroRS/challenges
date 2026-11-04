<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>basedErrors</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <nav>
        <a href="/"><strong>basedErrors</strong></a>
        <a href="/index.php">Projects</a>
        <?php if (isset($projectId)): ?>
        <a href="/errors.php?project_id=<?= $projectId ?>">Errors</a>
        <a href="/custom_fields.php?project_id=<?= $projectId ?>">Custom fields</a>
        <a href="/test.php?project_id=<?= $projectId ?>" target="_blank">Test</a>
        <?php endif ?>
    </nav>
    <main class="container">
