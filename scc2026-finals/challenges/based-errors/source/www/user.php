<?php
require_once 'db.php';

$user = $_SERVER['PHP_AUTH_USER'] ?? null;

if ($user === null) {
    echo '<p>No authentication information available.</p>';
    require 'footer.php';
} 

if (basename(__FILE__) == basename($_SERVER['SCRIPT_FILENAME'])) {
    require 'header.php';
    echo '<h2>User Information</h2>';
    echo '<table>';
    echo '<tr><th>Username:</th><td>' . htmlspecialchars($user) . '</td></tr>';
    echo '</table>';
    require 'footer.php';    
}
