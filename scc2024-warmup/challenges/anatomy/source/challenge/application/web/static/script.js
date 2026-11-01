var count = 0;

function increase() {
    // This function makes the counter work and also hides the third part of the flag in a comment: oF_a_w
    count++;
    document.getElementById("counter").innerHTML = count;
}

function fetch_stuff() {
    fetch('/api/fourth');
}

fetch_stuff();
