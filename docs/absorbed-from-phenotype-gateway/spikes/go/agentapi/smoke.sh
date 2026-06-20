#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../third_party/agentapi-plusplus"
go build ./...
