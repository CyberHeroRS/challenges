FROM python:3.12-slim-bookworm
RUN pip install --no-cache-dir pycryptodome==3.21.0
ENV PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solv.py ./
# The flag is only rendered inside the decrypted flag.png, so the runner passes when the solver
# exits cleanly and recovers the exact image that shows the static flag.
CMD ["sh", "-c", "python solv.py && sha256sum flag.png && echo '4ab49daabd60453bec184a13f249bfb94742ed481237671d8196047435b61cc8  flag.png' | sha256sum -c -"]
