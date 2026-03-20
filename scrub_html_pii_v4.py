#!/usr/bin/env python3
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
HTML_FILES = list(ROOT.rglob('*.html')) + list(ROOT.rglob('*.htm'))

INLINE_REGEXES = [
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[REDACTED_SSN]'),
    (re.compile(r'\b\d{9}\b'), '[REDACTED_SSN]'),
    (re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I), '[REDACTED_EMAIL]'),
    (re.compile(r'\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b'), '[REDACTED_PHONE]'),
    (re.compile(r'(?i)(DOB|Date of Birth)(\s*[:\-]?\s*)(\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4})'), r'\1\2[REDACTED_DOB]'),
    (re.compile(r'(?i)\b(Hi\s+)([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})(?=(?:[,\-!<\n\r ]|&nbsp;|$))'), r'\1[REDACTED_NAME]'),
    (re.compile(r'(?i)\b(Hi\s+)([A-Z][a-z]+)(?=(?:[,\-!<\n\r ]|&nbsp;|$))'), r'\1[REDACTED_NAME]'),
    (re.compile(r'(?i)((?:Login\s*)?PIN\s*[:=\-]\s*)([^<\s\n\r,;]+)'), r'\1[REDACTED]'),
    (
        re.compile(r'(?i)(\bcard\s+ending\s+in\s+(?:[A-Za-z][A-Za-z ]{0,30}\s+)?)(\d{3,6})\b'),
        r'\1[REDACTED_CARD]'
    ),
    (
        re.compile(r'(?i)(\bending\s+in\s+(?:[A-Za-z][A-Za-z ]{0,30}\s+)?)(\d{3,6})\b'),
        r'\1[REDACTED_CARD]'
    ),
    (re.compile(r'(?i)(Name|Full Name|First Name|Last Name)(\s*[:\-]\s*)([^<\n\r]+)'), r'\1\2[REDACTED_NAME]'),
    (re.compile(r'(?i)(Address|Street Address|Mailing Address)(\s*[:\-]\s*)([^<\n\r]+)'), r'\1\2[REDACTED_ADDRESS]'),
]


def apply_inline_regexes(text: str) -> str:
    for pattern, repl in INLINE_REGEXES:
        text = pattern.sub(repl, text)
    return text


def looks_like_pin_label(text: str) -> bool:
    t = ' '.join(text.split()).strip().lower()
    return t in {'pin:', 'pin', 'login pin:', 'login pin'}


def looks_like_pin_value(text: str) -> bool:
    t = text.strip()
    if not t or '[' in t or ']' in t:
        return False
    return re.fullmatch(r'[A-Z0-9]{4,20}', t) is not None


def looks_like_name(text: str) -> bool:
    t = ' '.join(text.split()).strip()
    return re.fullmatch(r"[A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+){1,3}", t) is not None


def looks_like_street(text: str) -> bool:
    t = ' '.join(text.split()).strip()
    return re.fullmatch(r"\d{1,6}\s+[A-Za-z0-9.#'\- ]{2,120}", t) is not None


def looks_like_city_state_zip(text: str) -> bool:
    t = ' '.join(text.split()).strip()
    return re.fullmatch(r"[A-Z][A-Za-z .'\-]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?", t) is not None


def scrub_dom(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')

    text_nodes = [n for n in soup.find_all(string=True) if isinstance(n, NavigableString)]
    for node in text_nodes:
        original = str(node)
        updated = apply_inline_regexes(original)
        if updated != original:
            node.replace_with(updated)

    text_nodes = [n for n in soup.find_all(string=True) if isinstance(n, NavigableString)]
    for i, node in enumerate(text_nodes):
        text = str(node).strip()
        if looks_like_pin_label(text):
            for j in range(i + 1, min(i + 12, len(text_nodes))):
                candidate = str(text_nodes[j]).strip()
                if looks_like_pin_value(candidate):
                    text_nodes[j].replace_with(str(text_nodes[j]).replace(candidate, '[REDACTED]'))
                    break

    text_nodes = [n for n in soup.find_all(string=True) if isinstance(n, NavigableString)]
    i = 0
    while i < len(text_nodes) - 2:
        a = ' '.join(str(text_nodes[i]).split()).strip()
        b = ' '.join(str(text_nodes[i + 1]).split()).strip()
        c = ' '.join(str(text_nodes[i + 2]).split()).strip()

        if looks_like_name(a) and looks_like_street(b) and looks_like_city_state_zip(c):
            text_nodes[i].replace_with('[REDACTED_NAME]')
            text_nodes[i + 1].replace_with('[REDACTED_ADDRESS]')
            text_nodes[i + 2].replace_with('[REDACTED_CITY_STATE_ZIP]')
            i += 3
            continue
        i += 1

    out = str(soup)
    out = re.sub(
        r'(?is)(Hi\s+\[REDACTED_NAME\][,!\s]*(?:<br\s*/?>|\r?\n|</p>\s*<p>)\s*){2,}',
        'Hi [REDACTED_NAME],\n',
        out,
    )
    return out


def main() -> int:
    changed = 0
    for path in HTML_FILES:
        try:
            html = path.read_text(encoding='utf-8', errors='ignore')
            scrubbed = scrub_dom(html)
            if scrubbed != html:
                path.write_text(scrubbed, encoding='utf-8')
                print(f'Scrubbed: {path}')
                changed += 1
            else:
                print(f'No changes: {path}')
        except Exception as e:
            print(f'ERROR: {path}: {e}')
    print(f'Finished. Updated {changed} file(s).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
