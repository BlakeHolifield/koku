#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CJI_SCRIPT_DIR="${SCRIPT_DIR}/cji_scripts"
${CJI_SCRIPT_DIR}/mp_truncate_lineitem_tables.py
