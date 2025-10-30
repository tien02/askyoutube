#!/bin/bash
set -euxo pipefail

docker compose --file container/docker-compose.yaml -f container/docker-compose-dev.yaml up --build "$@"
