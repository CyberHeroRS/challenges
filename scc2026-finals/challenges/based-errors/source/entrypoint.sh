#!/bin/sh
# Run db.php repeatedly until it exits successfully
echo "initializing db..."
while ! php db.php; do
  echo "failed, retrying..."
  sleep 1
done
echo "success!"

exec docker-php-entrypoint apache2-foreground
