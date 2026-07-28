"""
Registry of web data sources for Compliso ingestion.

Each source defines:
  - url/pages to fetch
  - authority tier (determines true_data vs noisy_data)
  - category (gst, msme, payment, general)
  - estimated page count for credit budgeting
"""

from dataclasses import dataclass, field


@dataclass
class Source:
    name: str
    url: str
    authority_tier: int          # 1=government 2=verified 3=professional 4=marketing 5=unconfirmed
    category: str                # gst, msme, payment, general
    doc_type: str                # "web_page" | "pdf" | "html"
    notes: str = ""
    sub_pages: list[str] = field(default_factory=list)


# ── Tier 1: Government (true_data, authority score 1.0) ─────────────────


GST_ACT_PDFS = Source(
    name="CGST Act 2017",
    url="https://cbic-gst.gov.in/pdf/CGST-Act-Updated-01082021.pdf",
    authority_tier=1,
    category="gst",
    doc_type="pdf",
    notes="Central Goods and Services Tax Act 2017 as amended",
)

IGST_ACT_PDF = Source(
    name="IGST Act 2017",
    url="https://www.indiacode.nic.in/bitstream/123456789/2251/1/A201713.pdf",
    authority_tier=1,
    category="gst",
    doc_type="pdf",
    notes="Integrated Goods and Services Tax Act 2017",
)

MSMED_ACT_PDF = Source(
    name="MSMED Act 2006",
    url="https://www.indiacode.nic.in/bitstream/123456789/2013/3/A2006-27.pdf",
    authority_tier=1,
    category="msme",
    doc_type="pdf",
    notes="Micro, Small and Medium Enterprises Development Act 2006",
)

UDYAM_NOTIFICATION = Source(
    name="Udyam Definition Revision 2025",
    url="https://udyamregistration.gov.in/docs/261838_220191.pdf",
    authority_tier=1,
    category="msme",
    doc_type="pdf",
    notes="Modified notification on revision of MSME definition effective 1 April 2025",
)

UDYAM_INFORMAL_MICRO = Source(
    name="Udyam Assist Platform",
    url="https://www.sidbi.in/en/udyam-assist-platform",
    authority_tier=1,
    category="msme",
    doc_type="web_page",
    notes="SIDBI: MSME Formalisation project - Udyam Assist Platform for informal micro enterprises",
)

CBIC_ITC_CIRCULAR = Source(
    name="CBIC Circular on ITC Section 16",
    url="https://cbic-gst.gov.in/pdf/circular-238-32-2024-GST.pdf",
    authority_tier=1,
    category="gst",
    doc_type="pdf",
    notes="Circular No. 238/32/2024-GST — Clarification on ITC under Section 16(5) and 16(6)",
)

CBIC_PROPER_OFFICER_CIRCULAR = Source(
    name="CBIC Circular Proper Officer 74A",
    url="https://www.caalley.com/gst25/Circular-No-254-11-2025-cgst-28102025.pdf",
    authority_tier=1,
    category="gst",
    doc_type="pdf",
    notes="Circular 254/11/2025-GST: Proper officer assignment under sections 74A, 75(2), 122",
)

CBIC_SHIP_TO_GSTIN = Source(
    name="GSTN Ship-to GSTIN Mandatory Advisory",
    url="https://tutorial.gst.gov.in/downloads/news/advisory_einvoice_api_ewb_by_irn_approved.pdf",
    authority_tier=1,
    category="gst",
    doc_type="pdf",
    notes="GSTN advisory: Ship-to GSTIN mandatory from 1 August 2026 (official GSTN)",
)


# ── Tier 2: Verified Portals (true_data, authority score 0.85) ───────────

GST_RULES_CBIC = Source(
    name="CGST Rules 2017",
    url="https://cbic-gst.gov.in/pdf/cgst-rules-30122017.pdf",
    authority_tier=1,
    category="gst",
    doc_type="pdf",
    notes="Central Goods and Services Tax Rules 2017 (official CBIC-GST PDF)",
)

GST_PORTAL_FAQ = Source(
    name="GST Portal FAQ",
    url="https://www.gst.gov.in/help/faq",
    authority_tier=2,
    category="gst",
    doc_type="web_page",
    notes="GST portal frequently asked questions",
)

GST_COUNCIL_PORTAL = Source(
    name="GST Council Portal",
    url="https://www.gstcouncil.gov.in/",
    authority_tier=1,
    category="gst",
    doc_type="web_page",
    notes="GST Council — meeting decisions, press releases, rate changes, official notifications",
)

MSME_MINISTRY_PORTAL = Source(
    name="MSME Ministry Portal",
    url="https://msme.gov.in/",
    authority_tier=2,
    category="msme",
    doc_type="web_page",
    notes="Ministry of MSME — policies, circulars, schemes, notifications",
)


# ── Master list for batch operations ─────────────────────────────────────

ALL_SOURCES: list[Source] = [
    GST_ACT_PDFS,
    IGST_ACT_PDF,
    MSMED_ACT_PDF,
    UDYAM_NOTIFICATION,
    UDYAM_INFORMAL_MICRO,
    CBIC_ITC_CIRCULAR,
    CBIC_PROPER_OFFICER_CIRCULAR,
    CBIC_SHIP_TO_GSTIN,
    GST_RULES_CBIC,
    GST_PORTAL_FAQ,
    GST_COUNCIL_PORTAL,
    MSME_MINISTRY_PORTAL,
]


def get_sources_by_tier(tier: int) -> list[Source]:
    return [s for s in ALL_SOURCES if s.authority_tier == tier]


def get_sources_by_category(category: str) -> list[Source]:
    return [s for s in ALL_SOURCES if s.category == category]


def estimate_credits(sources: list[Source] | None = None) -> int:
    """Estimate FireCrawl credits needed."""
    targets = sources or ALL_SOURCES
    total = 0
    for s in targets:
        if s.doc_type == "web_page":
            total += 1 + len(s.sub_pages)
        elif s.doc_type == "pdf":
            total += 0  # PDFs downloaded directly
    return total
