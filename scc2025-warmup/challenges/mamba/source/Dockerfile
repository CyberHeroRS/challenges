# Reproduces the published mamba.pyc byte for byte: it was compiled by CPython 3.12.4
# from a CRLF copy of main.py named .\main.py, modified at the recorded timestamp.
FROM python:3.12.4-slim AS compile
WORKDIR /build
COPY main.py .
RUN mkdir /out && sed -i 's/$/\r/' main.py && touch -d @1740118962 main.py && \
    python -c "import py_compile; py_compile.compile('main.py', cfile='/out/mamba.pyc', dfile=r'.\main.py', doraise=True)"

FROM scratch
COPY --from=compile /out/mamba.pyc /mamba.pyc
