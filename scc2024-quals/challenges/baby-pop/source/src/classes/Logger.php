<?php

class Logger {
    public $timestamp;

    function __construct(){
        if(!isset($this->timestamp)) {
            $this->timestamp = "01-01-2024";
        }
    }
    function __destruct(){
        $devSettings = $this->timestamp;
        $_SESSION['developerSettings'] = $devSettings;
    }
}

?>