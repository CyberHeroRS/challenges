<?php

include 'classes/Logger.php';

session_start();
$_SESSION = array();

if(isset($_GET['timestamp']) && !empty($_GET['timestamp'])){
    unserialize($_GET['timestamp']);
    header("location: index.php");
    exit; // Prevent developers from logging out and keep track of their work.
    
} else {
    session_destroy();
    header("location: login.php");
    exit;
}

?>