#!/usr/bin/env bash
set -euo pipefail
export USE_MOCK_LLM=true
pytest

