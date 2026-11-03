"use strict";
// Genuinely executes the unmodified challenge source (source.js) inside a
// vm sandbox that stubs just enough of `window`/`document` for the page's
// top-level IIFE and A() to run exactly as they would in a browser, then
// reports whatever the real logic decides to put in the #flag element.
const fs = require("fs");
const vm = require("vm");

const [, , sourcePath, candidatePassword] = process.argv;
if (!sourcePath || candidatePassword === undefined) {
  console.error("usage: node run_source.js <source.js> <candidate-password>");
  process.exit(2);
}

const code = fs.readFileSync(sourcePath, "utf8");

const flagElement = { innerHTML: "", style: "" };
const passwordElement = { value: candidatePassword };

const document = {
  getElementById(id) {
    if (id === "password") return passwordElement;
    if (id === "flag") return flagElement;
    return null;
  },
};

// A plain object stands in for `window` so the top IIFE's
// Object.getOwnPropertyNames(window).reduce(...) runs over a small, inert
// property list instead of throwing for lack of a real `window`.
const window = { location: "stub", stubA: 1, stubB: 2 };

const sandbox = { window, document, console };
vm.createContext(sandbox);

// Run the real, unmodified source, then invoke the real A() exactly like
// clicking the page's Submit button would.
vm.runInContext(code + "\nA();", sandbox, { filename: sourcePath });

const result = {
  innerHTML: flagElement.innerHTML,
  ok: /^Congrats, here's your flag: /.test(flagElement.innerHTML),
};
if (result.ok) {
  result.flag = flagElement.innerHTML.replace("Congrats, here's your flag: ", "");
}
console.log(JSON.stringify(result));
