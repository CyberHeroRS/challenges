FROM debian:bullseye-slim AS base
RUN sed -i 's|deb.debian.org|archive.debian.org|g' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends dosbox && \
    rm -rf /var/lib/apt/lists/*

# Borland C++ (a/) builds b/ with compile.bat. The -v debug info records the source mtime,
# so it is pinned to the published build's to reproduce MAIN1.EXE byte for byte.
FROM base AS compile
WORKDIR /build
COPY a a
COPY b/main1.cpp b/compile.bat b/
RUN touch -d "2025-03-18 22:34:48 UTC" b/main1.cpp && \
    SDL_VIDEODRIVER=dummy TZ=UTC timeout 600 dosbox -noconsole -noautoexec \
        -c "mount a a" -c "mount b b" -c "SET PATH=%PATH%;A:\BIN" -c "B:" \
        -c "call compile.bat" -c "exit" >/dev/null && \
    test -f b/MAIN1.EXE

FROM scratch AS participant
COPY --from=compile /build/b/MAIN1.EXE /MAIN1.EXE

FROM base
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 socat && \
    rm -rf /var/lib/apt/lists/* && \
    useradd --create-home --uid 1000 user
COPY --chmod=0555 piton.py /home/user/chall
COPY a /home/user/a
COPY b /home/user/b
COPY --from=compile /build/b/MAIN1.EXE /home/user/b/MAIN1.EXE
COPY dosbox.conf /home/user/
WORKDIR /home/user
EXPOSE 9198
USER user
CMD ["socat", "TCP-LISTEN:9198,reuseaddr,fork", "EXEC:/home/user/chall,stderr"]
