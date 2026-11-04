<?php
require_once 'db.php';
require_once 'user.php';
require_once 'project.php';
require 'header.php';

require_once 'project.php';

$prefix = 'project_' . (int)$projectId;
$table = "{$prefix}_custom_fields";

// Ensure table exists
create_tables($projectId);

// ---------- Handle form submissions ----------
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Add a new custom field
    if (isset($_POST['add'])) {
        $new_key   = $_POST['new_key'] ?? '';
        $new_value = $_POST['new_value'] ?? '';
        if (trim($new_key) !== '') {
            $stmt = $db->prepare("INSERT INTO `$table` (`key`, `value`) VALUES (?, ?)");
            $stmt->execute([
                $new_key,
                $new_value
            ]);
            add_custom_field_column($projectId, $new_key);
        }
    }

    // Update existing values
    if (isset($_POST['update']) && isset($_POST['value']) && is_array($_POST['value'])) {
        $stmt = $db->prepare("UPDATE `$table` SET `value` = ? WHERE field_id = ?");
        foreach ($_POST['value'] as $field_id => $val) {
            $stmt->execute([
                $val,
                $field_id
            ]);
        }
    }

    // Delete selected custom fields
    if (isset($_POST['delete']) && is_array($_POST['delete'])) {
        $stmt = $db->prepare("SELECT `key` FROM `$table` WHERE field_id = ?");
        $delStmt = $db->prepare("DELETE FROM `$table` WHERE field_id = ?");
        foreach ($_POST['delete'] as $field_id) {
            $stmt->execute([$field_id]);
            $delStmt->execute([$field_id]);
            
            $field = $stmt->fetch(PDO::FETCH_ASSOC);
            if ($field) {
                drop_custom_field_column($projectId, $field['key']);
            }
        }
    }
}

// ---------- Retrieve current custom fields ----------
$stmt = $db->query("SELECT field_id, `key`, `value` FROM `$table`");
$fields = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<h2>Custom Fields for Project <?php echo htmlspecialchars($projectId); ?></h2>

<form method="post">
    <table border="1" cellpadding="5" cellspacing="0">
        <tr>
            <th>Key</th>
            <th>Value (JS expression)</th>
            <th>Delete</th>
        </tr>
        <?php foreach ($fields as $field): ?>
        <tr>
            <td><?php echo htmlspecialchars($field['key']); ?></td>
            <td><input type="text" name="value[<?php echo $field['field_id']; ?>]" value="<?php echo htmlspecialchars($field['value']); ?>"></td>
            <td style="text-align:center;"><input type="checkbox" name="delete[]" value="<?php echo $field['field_id']; ?>"></td>
        </tr>
        <?php endforeach; ?>
    </table>
    <p>
        <button type="submit" name="update">Update Values</button>
        <button type="submit">Delete Selected</button>
    </p>
</form>

<h3>Add New Custom Field</h3>
<form method="post">
    <p>
        <label>Key: <input type="text" name="new_key" required></label>
    </p>
    <p>
        <label>Value (JS expression): <input type="text" name="new_value"></label>
    </p>
    <p>
        <button type="submit" name="add">Add Field</button>
    </p>
</form>

<?php
require 'footer.php';
?>
