# Diagnostics (Intro Web CTF)

Standalone challenge folder (no dependency on `matrix-web`).

## Run

```bash
cd diagnostics
npm start
```

Open: `http://localhost:4545`

## Organizer note

The intended reconstructed flag is:

`SCC{d14gn05t1c_5c4v3n63r_hun7_1n_n00k5_BR0W53R5_3V3RY_5URF4C3}`

## Quick writeup (organizer)

This is an intro recon challenge. Players should inspect:
- page source
- CSS in DevTools
- browser console
- network headers
- localStorage
- minified JS comments
- sourcemap by manual URL access
- robots.txt

Collect all shards and concatenate in this order:
1. `FLAG_PART_A=pt1{SCC{d14gn05t1c_}` from HTML source comment in `public/index.html`
2. `FLAG_PART_B=pt2{5c4v3n63r_}` from CSS comment in `public/assets/style.css`
3. `FLAG_PART_C=pt3{hun7_}` from console log in `public/assets/app.js`
4. `FLAG_PART_D=pt4{1n_}` from `x-diagnostic-relay` response header on `/api/pulse`
5. `FLAG_PART_E=pt5{n00k5_}` from `public/robots.txt`
6. `FLAG_PART_F=pt6{BR0W53R5_}` by base64-decoding localStorage key `FLAG_PART_F_B64` value `cHQ2e0JSMFc1M1I1X30=`
7. `FLAG_PART_G=pt7{3V3RY_}` from minified comment in `public/assets/runtime.min.js`
8. `FLAG_PART_H=pt8{5URF4C3}}` from `public/assets/source_part.js.map`
