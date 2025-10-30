#!/bin/bash
set -euxo pipefail

docker compose --file container/docker-compose.yaml up --build "$@"
