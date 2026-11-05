import os

from pwn import context, remote

# STATUS: NOT YET WORKING -- analysis only, no working exploit yet.
#
# "the-matrix-revenge" is a hardened follow-up to "the-matrix" (same
# forum app). Diffing against the original source confirms two of the
# original's shortcuts are deliberately closed:
#   - THREAD_FLAG is now a hardcoded placeholder (no env lookup at
#     all), so the "flag posted publicly as thread 9999" freebie is
#     gone.
#   - bot.ts's page.setCookie() now sets the "flag" cookie ONLY on
#     BOT_ORIGIN (the real app's own origin), never on the arbitrary
#     reported URL's origin -- so the self-hosted-page cookie-exfil
#     trick from the original (host our own page, have the bot set the
#     cookie there before navigating) no longer works; the cookie never
#     reaches an origin we control.
#
# dashboard.html still has the same "must be opened via window.open()"
# check (window.opener must be set) gating a postMessage listener that
# writes attacker-controlled fields into innerHTML (a real XSS sink,
# per the ORIGINAL file's own comment: "INTENTIONALLY UNSAFE... so that
# crafted payloads from the monitor chain can trigger XSS"). However,
# the embedded iframe (dashboard-monitor.html) that's allowed to
# postMessage into it only ever sends hardcoded, randomly-generated,
# non-attacker-controlled stats (uptime/ghosts/reports counters) -- no
# query param, hash, or other injectable surface was found feeding into
# that iframe's postMessage payload, so the XSS sink doesn't appear to
# be directly reachable as shipped.
#
# The flag's own name ("window_hijacking") suggests the intended path
# involves getting the bot to window.open() the real dashboard from a
# page we control (satisfying window.opener), then somehow leveraging
# that opener relationship (or a popup-target race against bot.ts's
# own activePage tracking via the 'targetcreated' event) to redirect or
# read from the resulting window -- but no concrete injection point
# into dashboard-monitor.html's postMessage payload was found within
# the time spent on this.
#
# Next step for whoever picks this up: check whether bot.ts's own popup
# tracking (onTargetCreated / activePage reassignment) can be raced --
# e.g. if our reported page itself opens a SECOND popup immediately
# after the real dashboard, activePage may end up pointing at a
# same-origin-with-us window instead, and the bot's later
# #dashboard-btn click/#close-dashboard-btn click could then act on a
# page we control rather than the real one, perhaps letting us smuggle
# something back out.

HOST = os.environ.get("SERVICE_THE_MATRIX_WEB_HOST", "127.0.0.1")
PORT = int(os.environ.get("SERVICE_THE_MATRIX_WEB_PORT", "3000"))

raise SystemExit("exploit not yet implemented -- see header comment for analysis so far")
