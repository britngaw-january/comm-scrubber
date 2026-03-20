#!/usr/bin/env bash
set -euo pipefail

ORIG_DIR="${1:-$HOME/Desktop/Comm_Files_20260320_190517}"
STAMP="$(date +%Y%m%d_%H%M%S)"
WORK_DIR="${ORIG_DIR}_scrubbed_${STAMP}"
PDF_DIR="${ORIG_DIR}_pdfs_${STAMP}"
REPO_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ ! -d "$ORIG_DIR" ]; then
  echo "Original folder not found: $ORIG_DIR" >&2
  exit 1
fi

cp -R "$ORIG_DIR" "$WORK_DIR"
python3 "$REPO_DIR/scrub_html_pii_v4.py" "$WORK_DIR" | tee "$WORK_DIR/scrub_log.txt"
"$REPO_DIR/convert_html_to_pdf.sh" "$WORK_DIR"
mkdir -p "$PDF_DIR"
find "$WORK_DIR" -iname "*.pdf" -exec cp {} "$PDF_DIR"/ \;

echo "Scrubbed copy: $WORK_DIR"
echo "PDF output:   $PDF_DIR"
