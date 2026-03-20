# comm-scrubber

Scripts to:
1. copy a pulled comms folder,
2. scrub common PII patterns from HTML files,
3. convert the scrubbed HTML files to PDFs.

## What it scrubs
- SSNs
- email addresses
- US phone numbers
- DOB fields
- greeting names like `Hi John Smith`
- inline PIN values like `PIN: I67K08`
- split PIN label/value patterns across separate HTML nodes
- simple multi-line mailing address blocks like:
  - `Gerald Kemp`
  - `8926 Dexter`
  - `Detroit, MI 48206`
- card-tail phrases like:
  - `card ending in 7207`
  - `card ending in Visa 7207`
  - `card ending in Apple Pay Visa 5515`

## Files
- `scrub_html_pii_v4.py` – scrubs HTML files in place
- `convert_html_to_pdf.sh` – converts HTML files to PDFs using `wkhtmltopdf` or Chrome headless
- `run_full_pipeline.sh` – copies original folder, scrubs, converts, and collects PDFs

## Setup
```bash
python3 -m pip install -r requirements.txt
chmod +x scrub_html_pii_v4.py convert_html_to_pdf.sh run_full_pipeline.sh
```

## Run the full pipeline
```bash
./run_full_pipeline.sh ~/Desktop/Comm_Files_20260320_190517
```

Outputs:
- a copied scrubbed folder: `~/Desktop/Comm_Files_20260320_190517_scrubbed_<timestamp>`
- a PDF folder: `~/Desktop/Comm_Files_20260320_190517_pdfs_<timestamp>`

## Converting to PDF
The converter tries:
1. `wkhtmltopdf`
2. Google Chrome headless at `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`

Install `wkhtmltopdf` with Homebrew if needed:
```bash
brew install wkhtmltopdf
```

## Integrating with Automat live / pull_comm_files.yaml
I did not have your actual `Automat live/pull_comm_files.yaml` file, so this is the safe integration pattern.

After your pull step writes HTML files into a local folder, call the pipeline script against that folder.

Example pattern inside your existing workflow:
```yaml
after_pull:
  - python3 -m pip install -r comm-scrubber/requirements.txt
  - bash comm-scrubber/run_full_pipeline.sh /path/to/output/Comm_Files_20260320_190517
```

If your workflow already creates the folder on the desktop, you can point directly to that folder.

## GitHub upload
I cannot push to your GitHub from here, but you can upload this repo with:
```bash
cd /path/to/comm-scrubber
git init
git add .
git commit -m "Add HTML PII scrubber and PDF pipeline"
git branch -M main
git remote add origin <YOUR_GITHUB_REPO_URL>
git push -u origin main
```

## Important limitation
This is pattern-based scrubbing, not guaranteed perfect PII detection. Spot-check a sample of output PDFs before sharing them.
