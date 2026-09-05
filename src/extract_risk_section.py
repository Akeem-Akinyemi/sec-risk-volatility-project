"""
Extracts the Risk Factors (Item 1A) section from raw SEC 10-K filings.
"""
import re
from bs4 import BeautifulSoup


def extract_risk_factors(filing_path: str, min_section_length: int = 5000) -> str:
    """
    Extracts the Risk Factors section (Item 1A) from a raw SEC 10-K filing.
    Handles period/dash/em-dash header styles. Skips matches immediately
    followed by a quotation mark, since those are cross-references quoting
    the section name inside a sentence, not the real header.
    """
    with open(filing_path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    soup = BeautifulSoup(raw, "lxml")
    text = soup.get_text(separator=" ")

    candidates = [m.start() for m in re.finditer(r"item\s+1a[\.\s\u2014\-]", text, re.IGNORECASE)]

    for start_pos in candidates:
        # Skip if this match is immediately followed by a quotation mark —
        # that means it's a cross-reference quoting the section name,
        # not the actual section header
        nearby_text = text[start_pos:start_pos + 30]
        if "\u201d" in nearby_text or "\u201c" in nearby_text or '"' in nearby_text:
            continue

        end_match = re.search(r"item\s+1b", text[start_pos:], re.IGNORECASE)
        if not end_match:
            continue

        section_length = end_match.start()
        if section_length >= min_section_length:
            return text[start_pos:start_pos + section_length]

    return ""