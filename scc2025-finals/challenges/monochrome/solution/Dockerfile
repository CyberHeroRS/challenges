FROM python:3.12-slim-bookworm
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends tshark zbar-tools && \
    rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir matplotlib==3.10.0
ENV MPLBACKEND=Agg PYTHONUNBUFFERED=1
WORKDIR /solution
COPY solv_keyboard.py solv_wacom.py ./
# Both solvers read capture.pcapng from the working directory, where the published capture is mounted.
# The keystrokes only reveal a hint; the flag is the QR code drawn on the tablet, which solv_wacom.py
# renders to wacom.png and zbarimg scans.
# Passes only when every step exits cleanly and the output contains the expected flag.
CMD ["sh", "-c", "python solv_keyboard.py > out.txt && python solv_wacom.py && zbarimg -q --nodbus wacom.png >> out.txt; status=$?; cat out.txt; [ \"$status\" -eq 0 ] && grep -qF \"$flag_main\" out.txt"]
