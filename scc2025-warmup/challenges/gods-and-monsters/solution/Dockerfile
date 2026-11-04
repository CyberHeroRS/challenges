FROM sagemath/sagemath:latest

RUN sage -pip install --no-cache-dir pycryptodome==3.21.0

WORKDIR /home/sage/solution
COPY --chown=sage:sage sol.sage ./
# out.txt is bind-mounted in at test time (see challenge.yaml's
# test[0].mounts).

# The sagemath/sagemath image's entrypoint is `sage-entrypoint`, which always
# re-wraps the container command as `sage -sh -c "$*"`. Passing a *single*
# CMD string (rather than an exec-form argv list) means "$*" reconstructs it
# verbatim, so this behaves like a normal shell command run inside Sage's
# environment.
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sage sol.sage > /tmp/out 2>&1; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
