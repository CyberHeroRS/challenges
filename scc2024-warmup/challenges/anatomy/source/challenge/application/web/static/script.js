var count = 0;

function increase() {
    // This function makes the counter work and also hides the third part of the flag in a comment: __FLAG_PART_3__
    count++;
    document.getElementById("counter").innerHTML = count;
}

function fetch_stuff() {
    fetch('/api/fourth');
}

fetch_stuff();
