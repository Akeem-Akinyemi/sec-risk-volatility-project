"""
Extracts the Risk Factors (Item 1A) section from raw SEC 10-K filings.
"""
import re
from bs4 import BeautifulSoup


def isolate_10k_document(raw_text: str) -> str:
    """
    SEC full-submission files bundle the 10-K together with many exhibits
    and other documents. This isolates just the document tagged as the
    actual 10-K.
    """
    doc_match = re.search(r"<DOCUMENT>.*?<TYPE>10-K.*?</DOCUMENT>", raw_text, re.DOTALL | re.IGNORECASE)
    if doc_match:
        return doc_match.group(0)
    return raw_text


def extract_risk_factors(filing_path: str, min_section_length: int = 15000) -> str:
    """
    Extracts the Risk Factors section (Item 1A) from a raw SEC 10-K filing.
    """
    with open(filing_path, "r", encoding="utf-8", errors="ignore") as f:
        raw = f.read()

    tenk_only = isolate_10k_document(raw)
    soup = BeautifulSoup(tenk_only, "lxml")
    text = soup.get_text(separator=" ")

    candidates = [m.start() for m in re.finditer(r"item\s+1a", text, re.IGNORECASE)]

    best_start = None
    best_length = 0

    for start_pos in candidates:
        nearby = text[start_pos:start_pos + 40]

        if "," in text[start_pos:start_pos + 15]:
            continue
        if not re.search(r"ri\s?sk\s+factor\s?s", nearby, re.IGNORECASE):
            continue

        end_match = re.search(r"item\s+1b", text[start_pos:], re.IGNORECASE)
        if not end_match:
            continue

        section_length = end_match.start()

        if section_length >= min_section_length and section_length > best_length:
            best_start = start_pos
            best_length = section_length

    if best_start is not None:
        return text[best_start:best_start + best_length]

    return ""