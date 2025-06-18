#!/bin/bash
url="http://localhost/"
timeout=30
interval=2
elapsed=0

while ! curl -sSf "$url" > /dev/null; do
  echo "Waiting for server..."
  sleep $interval
  elapsed=$((elapsed + interval))
  if [ $elapsed -ge $timeout ]; then
    echo "Server failed to start in $timeout seconds"
    exit 1
  fi
done

echo "Server is up"



