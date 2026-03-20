#!/usr/bin/env bash
set -euo pipefail

SRC_DIR="${1:-.}"

convert_one() {
  local input="$1"
  local output="${input%.*}.pdf"

  if command -v wkhtmltopdf >/dev/null 2>&1; then
    wkhtmltopdf "$input" "$output"
    return 0
  fi

  if [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    local abs
    abs="file://$(python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$input")"
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
      --headless \
      --disable-gpu \
      --print-to-pdf="$output" \
      "$abs" >/dev/null 2>&1
    return 0
  fi

  echo "No PDF converter found. Install wkhtmltopdf or Google Chrome." >&2
  return 1
}

export -f convert_one
find "$SRC_DIR" \( -iname "*.html" -o -iname "*.htm" \) -print0 | while IFS= read -r -d '' f; do
  convert_one "$f"
done
