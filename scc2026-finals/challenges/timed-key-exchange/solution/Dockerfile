FROM sagemath/sagemath:latest

RUN sage -pip install --no-cache-dir pwntools tqdm

WORKDIR /home/sage/solution
COPY --chown=sage:sage sol.py ./

# The sagemath/sagemath image's entrypoint is `sage-entrypoint`, which always
# re-wraps the container command as `sage -sh -c "$*"`. Passing a *single*
# CMD string (rather than an exec-form argv list) means "$*" reconstructs it
# verbatim, so this behaves like a normal shell command run inside Sage's
# environment. Kept as a plain .py file (not .sage) -- Sage's preparser
# converts bare integer literals to Sage Integers/Rationals in .sage files,
# which breaks tqdm's percentage formatting (`{percentage:3.0f}`) on a
# Sage Rational; `sage sol.py` still gets the full `sage.all` environment
# without that literal-rewriting.
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sage sol.py > /tmp/out 2>&1; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_flag\" /tmp/out"]
