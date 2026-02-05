// query string and read msg and err from it, show notifications using toastr and remove from query string

let urlParams = new URLSearchParams(window.location.search);
let msg = urlParams.get('msg');
let err = urlParams.get('err');

if (msg) {
    toastr.success(msg);
}

if (err) {
    toastr.error(err);
}

// remove err and msg from query string but keep other params
urlParams.delete('msg');
urlParams.delete('err');

let newUrl = window.location.pathname + '?' + urlParams.toString();

window.history.replaceState({}, document.title, newUrl);

