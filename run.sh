#!/bin/bash
# Kept for compatibility: same as ./bh serve
cd "$(dirname "$0")"
exec ./bh serve "$@"
