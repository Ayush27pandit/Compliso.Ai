"""
Query expansion for Hinglish support, acronym expansion, and compliance jargon mapping.

Improves recall by expanding queries with synonyms, Hindi/regional terms,
and expanding abbreviations to their full forms.
"""

import re
import logfire


# ── Hinglish / Hindi → English Mapping ────────────────────────────────────────

_HINGLISH_MAP = {
    # Common Hindi words used in compliance context
    "kya": "what",
    "kaise": "how",
    "kab": "when",
    "kaun": "who",
    "kyun": "why",
    "kitna": "how much",
    "kitne": "how many",
    "yeh": "this",
    "woh": "that",
    "hai": "is",
    "hain": "are",
    "tha": "was",
    "the": "were",
    "karna": "do",
    "karna": "to do",
    "karo": "do",
    "batao": "tell",
    "samjhao": "explain",
    "dikhao": "show",
    "chahiye": "need",
    "mujhe": "me",
    "humko": "us",
    "aapko": "you",
    "usko": "him/her",
    "iska": "its",
    "uska": "his/her",
    "mere": "my",
    "hamare": "our",
    "aapka": "your",
    "sabse": "most",
    "zyada": "more",
    "kam": "less",
    "accha": "good",
    "bura": "bad",
    "sahi": "correct",
    "galat": "wrong",

    # Compliance-specific Hinglish
    "return": "return filing",
    "file": "filing",
    "filing": "return filing",
    "due date": "deadline",
    "deadline": "due date",
    "late fee": "penalty",
    "penalty": "late fee",
    "fine": "penalty",
    "notice": "notice",
    "registration": "registration",
    "certificate": "certificate",
    "verify": "verification",
    "check": "verification",
}

# ── Acronym Expansion ─────────────────────────────────────────────────────────

_ACRONYM_MAP = {
    "gst": "Goods and Services Tax",
    "gstr": "GST Return",
    "gstr1": "GST Return 1 (outward supplies)",
    "gstr3b": "GST Return 3B (summary return)",
    "gstr9": "GST Return 9 (annual return)",
    "gstr4": "GST Return 4 (composition dealers)",
    "msme": "Micro Small Medium Enterprises",
    "udyam": "Udyam Registration MSME",
    "itc": "Input Tax Credit",
    "hsn": "Harmonized System of Nomenclature",
    "sac": "Services Accounting Code",
    "cbic": "Central Board of Indirect Taxes and Customs",
    "drc": "Demand Recovery Circular",
    "cin": "Corporate Identity Number",
    "tan": "Tax Deduction Account Number",
    "pan": "Permanent Account Number",
    "gstin": "Goods and Services Tax Identification Number",
    "ein": "Enterprise Identification Number",
}

# ── Synonym Dictionary (Compliance Jargon) ───────────────────────────────────

_SYNONYM_MAP = {
    # GST concepts
    "input tax credit": ["ITC", "credit", "tax credit", "input credit"],
    "output tax": ["tax liability", "tax payable", "output GST"],
    "inward supply": ["purchase", "procurement", "buying"],
    "outward supply": ["sale", "supply", "selling"],
    "aggregate turnover": ["total turnover", "annual turnover", "gross turnover"],
    "taxable supply": ["taxable goods", "taxable services", "taxable supplies"],
    "exempt supply": ["exempt goods", "exempt services", "exemption"],
    "nil rated": ["zero rated", "0% GST", "no GST"],
    "reverse charge": ["RCM", "reverse charge mechanism"],
    "e-way bill": ["eway bill", "ewaybill", "electronic way bill"],
    "e-invoice": ["einvoicing", "electronic invoice"],
    "composition scheme": ["composition levy", "composition tax", "composition dealer"],

    # MSME concepts
    "micro enterprise": ["micro business", "micro unit", "micro firm"],
    "small enterprise": ["small business", "small unit", "small firm"],
    "medium enterprise": ["medium business", "medium unit", "medium firm"],
    "udyam registration": ["MSME registration", "MSME certificate", "udyam certificate"],
    "udyam portal": ["MSME portal", "udyam.gov.in"],
    "msme certificate": ["udyam certificate", "MSME registration", "MSME udyam"],

    # Payment terms
    "delayed payment": ["late payment", "payment delay", "overdue payment"],
    "payment terms": ["payment period", "credit period", "payment timeline"],
    "section 43b(h)": ["43B(h)", "section 43B", "43B deduction"],

    # Returns and filing
    "annual return": ["yearly return", "annual filing"],
    "monthly return": ["monthly filing"],
    "quarterly return": ["quarterly filing"],
    "due date": ["deadline", "filing date", "last date"],
    "late fee": ["penalty", "late charges", "late filing fee"],
    "revised return": ["amended return", "correction return"],
}


# ── Query Expansion ───────────────────────────────────────────────────────────

def expand_acronyms(query: str) -> str:
    """
    Expand acronyms in the query to their full forms.
    E.g., "GST registration" → "GST Goods and Services Tax registration"
    """
    expanded = query
    for acronym, full_form in _ACRONYM_MAP.items():
        # Match acronym as whole word (case-insensitive)
        pattern = r'\b' + re.escape(acronym) + r'\b'
        if re.search(pattern, expanded, re.IGNORECASE):
            # Add full form without replacing the acronym
            expanded = f"{expanded} {full_form}"
    return expanded


def expand_hinglish(query: str) -> str:
    """
    Expand Hinglish terms to English equivalents.
    E.g., "kya hai GST registration" → "what is GST registration"
    """
    words = query.lower().split()
    expanded_words = []
    for word in words:
        clean = re.sub(r'[^a-z]', '', word)
        if clean in _HINGLISH_MAP:
            expanded_words.append(_HINGLISH_MAP[clean])
        else:
            expanded_words.append(word)
    return " ".join(expanded_words)


def expand_synonyms(query: str) -> str:
    """
    Add relevant synonyms to improve recall.
    E.g., "composition scheme" → "composition scheme composition levy composition tax"
    """
    query_lower = query.lower()
    extras = []

    for term, synonyms in _SYNONYM_MAP.items():
        if term in query_lower:
            # Add synonyms that aren't already in the query
            for syn in synonyms:
                if syn.lower() not in query_lower:
                    extras.append(syn)

    if extras:
        return f"{query} {' '.join(extras)}"
    return query


def expand_query(query: str) -> str:
    """
    Full query expansion pipeline:
    1. Hinglish → English
    2. Acronym expansion
    3. Synonym expansion
    """
    with logfire.span("🔤 Query Expansion", original=query[:80]):
        expanded = expand_hinglish(query)
        expanded = expand_acronyms(expanded)
        expanded = expand_synonyms(expanded)

        if expanded != query:
            logfire.info(
                "Query expanded",
                original=query[:80],
                expanded=expanded[:120],
            )

        return expanded


# ── Query Expansion for Retrieval ─────────────────────────────────────────────

def expand_for_retrieval(query: str) -> dict:
    """
    Expand query and return both original and expanded versions.
    The original is used for the LLM prompt, expanded for retrieval.
    """
    expanded = expand_query(query)

    return {
        "original": query,
        "expanded": expanded,
        "was_expanded": expanded != query,
    }
