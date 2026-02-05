<?php

ini_set('display_errors','Off');
error_reporting(0);

include 'views/index.html';
include 'hidden/flag.php';

function popup($msg){
    echo '<script>alert(`' . $msg . '`);</script>';
}

if(!isset($_GET['book']) || empty($_GET['book'])){
    die();
} else {
    $book = $_GET['book'];

    if(strtolower($book) === "flag"){
        popup("You don't have enough funds to buy this book.");
        die();
    }

    if(isset($_GET['del']) && is_array($book)) {
        $del = (int)$_GET['del'];
        
        if(count($book) <= 1) {
            popup('Our security system has detected a potential threat, and your actions have been logged.');
            die();
        }

        for($i=0;$i<$del;$i++){ // No limit checks? We don't care, right?
            array_pop($book); 
        }
    } 
    
    if ($book == NULL) {
        popup($flag);
    } else {
        popup('Book added to cart.');
    }
}

?>