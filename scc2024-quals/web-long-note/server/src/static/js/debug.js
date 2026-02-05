function sleep(milliseconds) {
    return new Promise(resolve => setTimeout(resolve, milliseconds));
}

function timeout(){
    if(window.debug) {
        setTimeout(debug.timeout, 500)
    } else {
        sleep(1000) // decrease load times
    }
}

export { timeout };
