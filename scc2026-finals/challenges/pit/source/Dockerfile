FROM python:3.14-alpine

WORKDIR /app
ENV FILEDIR=/files
ENV FLAG=FAKE{this_is_a_fake_flag}
EXPOSE 3000

RUN apk add zip unzip

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy the application code
COPY ./ /app


CMD \
    echo -n "${FLAG}" > /flag.txt && \
    uv run filepit/main.py --files-dir ${FILEDIR} --port 3000
