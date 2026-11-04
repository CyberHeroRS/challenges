<!DOCTYPE html>
<html>
<head>
  <title>JS Error Testing</title>
  <script src="/snippet.php?project_id=<?= $_GET["project_id"] ?>"></script>
  <script>
    function triggerReferenceError() {
      // undefined variable
      console.log(nonExistentVariable);
    }
    function triggerTypeError() {
      // call non-function as function
      const notAFunction = 5;
      notAFunction();
    }
    function triggerSyntaxError() {
      // invalid eval code
      eval('function(){');
    }
    function triggerRangeError() {
      // recursion leading to stack overflow
      function recurse() { recurse(); }
      recurse();
    }
    function triggerURIError() {
      // malformed URI sequence
      decodeURIComponent('%');
    }
    function triggerCustomError() {
      throw new Error('Custom error');
    }
  </script>
</head>
<body>
  <h1>Trigger JavaScript Errors</h1>
  <p>Add a custom field <strong>user:</strong> <code>window.user.value</code> to capture the user field in this demo</p>
  <label for="user">User:</label>
  <select name="user" id="user">
    <option value="admin">admin</option>
    <option value="steve">steve</option>
    <option value="johnny">johnny</option>
  </select>
  <br>
  <br>
  <button onclick="triggerReferenceError()">ReferenceError</button>
  <button onclick="triggerTypeError()">TypeError</button>
  <button onclick="triggerSyntaxError()">SyntaxError</button>
  <button onclick="triggerRangeError()">RangeError</button>
  <button onclick="triggerURIError()">URIError</button>
  <button onclick="triggerCustomError()">Custom Error</button>
</body>
</html>