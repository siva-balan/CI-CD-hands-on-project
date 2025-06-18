#!/bin/bash

curl -sSf http://localhost:8090/ > /dev/null
status=$?

if [ "$status" -eq 0 ]; then
  echo "Server is up"
else
  echo "Server is down (status=$status)"
fi



