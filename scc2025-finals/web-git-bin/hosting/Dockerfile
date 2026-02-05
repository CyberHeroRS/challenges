FROM python:3.12-alpine

# Switch to the app directory
WORKDIR /app 

# Install git and python dependencies
RUN apk add --no-cache git python3 py3-pip

RUN pip install --upgrade --no-cache-dir --root-user-action ignore pip

# Unicorn takes a long time to install, so we install it first
RUN pip install --no-cache-dir --root-user-action ignore unicorn

COPY ./app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --root-user-action ignore -r /app/requirements.txt

# Copy application and templates
COPY ./repo-templates /repo-templates


# Add entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create a non-root user and group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Create necessary directories and set permissions
RUN mkdir -p /repos /data /app /repo-templates /data/db && \
    chmod -R 775 /repos /data /data/db && \
    chown -R appuser:appgroup /repos /data /data/db


# Change ownership of entrypoint script
RUN chown appuser:appgroup /entrypoint.sh


# Switch to non-root user
USER appuser

# Configure git
RUN git config --global init.defaultBranch main
RUN git config --global user.email "repo@server"
RUN git config --global user.name "Repo server"
RUN git config --global core.eol lf
RUN git config --global receive.denyCurrentBranch updateInstead

USER root
COPY ./app /app

# Mark all hooks as executable
RUN chmod +x /app/hooks/*

USER appuser


ARG FLAG
ENV FLAG=$FLAG

ENTRYPOINT ["/entrypoint.sh"]

EXPOSE 80
