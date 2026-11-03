# The challenge image builds its binary against ubuntu:22.04's own libc/libstdc++
# (installed via apt at image-build time, not vendored in source/), so the
# solver needs to pull the matching libc6/libstdc++6/libgcc-s1 build from the
# same apt snapshot rather than bundling fixed .so files.
FROM ubuntu:22.04 AS libs
RUN apt-get update && \
    apt-get install -y --no-install-recommends libstdc++6 && \
    rm -rf /var/lib/apt/lists/*

FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pwntools==4.14.1
ENV PWNLIB_NOTERM=1 PYTHONUNBUFFERED=1
WORKDIR /solution
COPY --from=libs /lib/x86_64-linux-gnu/libc.so.6 ./libc.so.6
COPY --from=libs /lib/x86_64-linux-gnu/libstdc++.so.6.0.30 ./libstdc++.so.6.0.30
COPY --from=libs /lib/x86_64-linux-gnu/libgcc_s.so.1 ./libgcc_s.so.1
COPY --from=libs /lib/x86_64-linux-gnu/libm.so.6 ./libm.so.6
COPY sol.py ./
# Passes only when the solver exits cleanly and its output contains the expected flag.
CMD ["sh", "-c", "python sol.py > /tmp/out; status=$?; cat /tmp/out; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" /tmp/out"]
