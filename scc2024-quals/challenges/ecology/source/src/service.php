<?php

if (isset($_GET['destination'])) {
    $destination = $_GET['destination'];
    
    $options = array(
        'http' => array(
            'method' => 'POST',
            'header' => 'Content-Type: text/plain',
            'content' => getenv('FLAG')
        )
    );
    
    // HTTPS doesn't work in some environments
    $context = stream_context_create($options);
    
    $response = file_get_contents($destination, false, $context);
    
    echo 'Flag sent.';
} else {
    echo 'No destination provided.';
}
 
?>