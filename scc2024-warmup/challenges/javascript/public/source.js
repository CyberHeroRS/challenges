const enc = [23, 16, 55, 23, 83, 4, 85, 81, 117, 16, 90, 93, 76, 9, 86, 1, 34, 126, 64, 84, 86, 6, 73, 4, 36, 68, 9, 72, 88, 13, 89, 80, 32, 50, 65, 94, 85, 81, 7, 83, 63];
(Object.getOwnPropertyNames(window).reduce(
	(acc, x, y, z) => acc.b.length !== 19 ?
	(
		{ ...acc, a: acc.a + 1, b: z.filter(x => x.length === acc.a) }
	) :
	(
		acc.c[(acc.b.slice(0, 16).reduce(
			(a, b, c) => a + b[c % b.length], ''
		))]++ || z.splice(1)
	),
	{ a: 0, b: [], c: window }
))
function A() {
    let x = document.getElementById("password").value;
    try {
        eval(x);
        const flag = enc.map((a, b) => String.fromCharCode(a ^ x.charCodeAt(b % x.length))).join("");
        if (flag.startsWith("SCC")) {
            document.getElementById("flag").innerHTML = "Congrats, here's your flag: " + flag;
            document.getElementById("flag").style = "color: green;"
        }
        else {
            document.getElementById("flag").innerHTML = "Incorrect";
            document.getElementById("flag").style = "color: red;"
        }

    } catch (e) {
        document.getElementById("flag").innerHTML = "Incorrect";
        document.getElementById("flag").style = "color: red;"
    }
}
