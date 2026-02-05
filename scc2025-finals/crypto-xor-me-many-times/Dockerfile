FROM python:3.12-slim

EXPOSE 1337

ENV FLAG="SCC{Eucleadian_algorithm_is_bad_randomness_extractor_:(}"

RUN apt-get -y update && \
    apt-get install -y socat coreutils && \
    rm -rf /var/lib/apt/lists/*

COPY ./source/xor_me_many_times.py /

RUN chmod 555 /xor_me_many_times.py

ENTRYPOINT []
CMD socat -T 100 \
    TCP-LISTEN:1337,nodelay,reuseaddr,fork \
    EXEC:"stdbuf -i0 -o0 -e0 python /xor_me_many_times.py"
    