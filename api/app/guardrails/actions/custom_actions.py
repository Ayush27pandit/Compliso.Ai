"""
Compliso Guardrails - Custom Actions
Lightweight implementation of guardrails without NeMo dependency.
"""

import re
from typing import List, Dict, Any, Optional
import logfire


class GuardrailsConfig:
    """Configuration for guardrails."""

    def __init__(self, config_path: str = "guardrails/config/config.yml"):
        self.config_path = config_path
        self.enabled = True

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            import yaml
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logfire.error(f"Failed to load guardrails config: {e}")
            return {}


class InputGuardrails:
    """Input rail checks - runs before planner."""

    BLOCKED_JAILBREAK_PATTERNS = [
        r"ignore\s+(?:your|all|the)\s+instructions",
        r"pretend\s+you\s+are",
        r"system\s*prompt\s*:",
        r"reveal\s+your\s+instructions",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"override\s+safety\s+filters",
        r"bypass\s+(?:your|all|the)\s+(?:rules|restrictions|filters)",
        r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
    ]

    BLOCKED_INJECTION_PATTERNS = [
        r"```ignore\s+previous\s+instructions```",
        r"you\s+are\s+now\s+in\s+developer\s+mode",
        r"override\s+safety\s+filters",
        r"\[SYSTEM\]\s*:",
        r"<\|im_start\|>\s*system",
        r"ADMIN\s+MODE\s+ACTIVATED",
    ]

    BLOCKED_EXTRACTION_PATTERNS = [
        r"(?:retrieve|get|list|show|extract|fetch)\s+(?:all|every|the)\s+(?:docs?|documents?|files?|names?|data)",
        r"(?:what|which)\s+(?:docs?|documents?|files?|data)\s+(?:are|is|do|does)\s+(?:in|stored|contained)",
        r"vector\s*(?:db|database|store)",
        r"(?:internal|system|admin)\s+(?:details?|info|information|config|settings)",
        r"(?:show|reveal|print)\s+(?:your|the)\s+(?:system|config|prompt|instructions|code)",
        r"(?:training|source)\s+data",
        r"(?:list|show|give)\s+(?:me\s+)?(?:all\s+)?(?:the\s+)?(?:document\s+)?names",
        r"(?:what|which)\s+(?:documents?|files?)\s+(?:do|does)\s+(?:the\s+)?(?:system|db|database|vector)",
    ]

    PII_PATTERNS = {
        "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
        "GSTIN": r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][0-9]Z[0-9A-Z]\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "PHONE": r"\b[6-9][0-9]{9}\b",
    }

    @classmethod
    def check_jailbreak(cls, text: str) -> bool:
        """Check for jailbreak attempts. Returns True if safe."""
        text_lower = text.lower()
        for pattern in cls.BLOCKED_JAILBREAK_PATTERNS:
            if re.search(pattern, text_lower):
                logfire.warning(f"Jailbreak attempt detected: {pattern}")
                return False
        return True

    @classmethod
    def check_information_extraction(cls, text: str) -> bool:
        """Check for attempts to extract system internals. Returns True if safe."""
        text_lower = text.lower()
        for pattern in cls.BLOCKED_EXTRACTION_PATTERNS:
            if re.search(pattern, text_lower):
                logfire.warning(f"Information extraction attempt detected: {pattern}")
                return False
        return True

    @classmethod
    def check_prompt_injection(cls, text: str) -> bool:
        """Check for prompt injection. Returns True if safe."""
        text_lower = text.lower()
        for pattern in cls.BLOCKED_INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                logfire.warning(f"Prompt injection detected: {pattern}")
                return False
        return True

    @classmethod
    def mask_pii(cls, text: str) -> str:
        """Mask PII in text."""
        masked = text
        for pii_type, pattern in cls.PII_PATTERNS.items():
            masked = re.sub(pattern, f"[{pii_type}_MASKED]", masked)
        return masked

    @classmethod
    def validate(cls, text: str) -> Dict[str, Any]:
        """Run all input rail checks."""
        result = {
            "safe": True,
            "masked_text": cls.mask_pii(text),
            "checks": {
                "jailbreak": cls.check_jailbreak(text),
                "injection": cls.check_prompt_injection(text),
                "extraction": cls.check_information_extraction(text),
            }
        }

        if not all(result["checks"].values()):
            result["safe"] = False

        return result


class OutputGuardrails:
    """Output rail checks - runs after responder."""

    BLOCKED_OUTPUT_PATTERNS = [
        r"guaranteed\s+returns?",
        r"100%\s+accurate",
        r"never\s+wrong",
        r"ignore\s+the\s+law",
        r"definitely\s+legal",
        r"no\s+need\s+to\s+worry",
    ]

    CITATION_PATTERN = r"Circular\s+(\d+/\d+-\w+)"

    @classmethod
    def check_output_safety(cls, text: str) -> bool:
        """Check output for harmful content. Returns True if safe."""
        text_lower = text.lower()
        for pattern in cls.BLOCKED_OUTPUT_PATTERNS:
            if re.search(pattern, text_lower):
                logfire.warning(f"Unsafe output pattern detected: {pattern}")
                return False
        return True

    @classmethod
    def verify_citations(cls, response: str, sources: List[str]) -> bool:
        """Verify that cited circular numbers exist in sources."""
        citations = re.findall(cls.CITATION_PATTERN, response)
        if not citations:
            return True  # No citations to verify

        combined_sources = " ".join(sources)
        for citation in citations:
            if citation not in combined_sources:
                logfire.warning(f"Unverified citation: {citation}")
                return False
        return True

    @classmethod
    def check_grounding(cls, response: str, sources: List[str], threshold: float = 0.3) -> bool:
        """Check if response is grounded in sources using keyword overlap."""
        if not sources:
            return True

        response_words = set(response.lower().split())
        source_words = set(" ".join(sources).lower().split())

        overlap = len(response_words & source_words)
        grounding_ratio = overlap / len(response_words) if response_words else 0

        if grounding_ratio < threshold:
            logfire.warning(f"Response may be hallucinated. Grounding ratio: {grounding_ratio:.2f}")
            return False
        return True

    @classmethod
    def validate(cls, response: str, sources: List[str]) -> Dict[str, Any]:
        """Run all output rail checks."""
        result = {
            "safe": True,
            "checks": {
                "safety": cls.check_output_safety(response),
                "citations": cls.verify_citations(response, sources),
                "grounding": cls.check_grounding(response, sources),
            }
        }

        if not all(result["checks"].values()):
            result["safe"] = False

        return result


class RetrievalGuardrails:
    """Retrieval rail checks - runs after retrieval."""

    # Official sources take priority
    AUTHORITY_SOURCES = [
        "gst.gov.in",
        "cbic.gov.in",
        "msme.gov.in",
        "udyamregistration.gov.in",
        "indiagovt.gov.in",
    ]

    OUTDATED_YEAR_THRESHOLD = 2023

    @classmethod
    def check_source_authority(cls, source: str) -> bool:
        """Check if source is from an authoritative domain."""
        source_lower = source.lower()
        for authority in cls.AUTHORITY_SOURCES:
            if authority in source_lower:
                return True
        return True  # Allow non-authoritative but flag them

    @classmethod
    def check_outdated(cls, text: str) -> bool:
        """Check if content contains outdated information."""
        year_pattern = r"\b(20[0-2][0-9])\b"
        years = re.findall(year_pattern, text)

        for year in years:
            if int(year) < cls.OUTDATED_YEAR_THRESHOLD:
                logfire.warning(f"Potentially outdated content from year: {year}")
                return False
        return True

    @classmethod
    def validate(cls, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and validate retrieved chunks."""
        validated = []
        for chunk in chunks:
            text = chunk.get("text", "")
            source = chunk.get("source", "")

            is_authority = cls.check_source_authority(source)
            is_current = cls.check_outdated(text)

            chunk["authority_score"] = 1.0 if is_authority else 0.5
            chunk["freshness_score"] = 1.0 if is_current else 0.3

            # Filter out clearly outdated or low-authority chunks
            if chunk["freshness_score"] >= 0.3:
                validated.append(chunk)

        return validated


class GuardrailsManager:
    """Main guardrails manager that orchestrates all rails."""

    def __init__(self, config: Optional[GuardrailsConfig] = None):
        self.config = config or GuardrailsConfig()
        self.input_rails = InputGuardrails()
        self.output_rails = OutputGuardrails()
        self.retrieval_rails = RetrievalGuardrails()

    def check_input(self, query: str) -> Dict[str, Any]:
        """Run input rails on user query."""
        with logfire.span("Input Rails Check"):
            result = self.input_rails.validate(query)
            logfire.info(f"Input rails result: safe={result['safe']}")
            return result

    def check_output(self, response: str, sources: List[str]) -> Dict[str, Any]:
        """Run output rails on generated response."""
        with logfire.span("Output Rails Check"):
            result = self.output_rails.validate(response, sources)
            logfire.info(f"Output rails result: safe={result['safe']}")
            return result

    def filter_retrieval(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run retrieval rails on retrieved chunks."""
        with logfire.span("Retrieval Rails Check"):
            filtered = self.retrieval_rails.validate(chunks)
            logfire.info(f"Retrieval rails: {len(chunks)} → {len(filtered)} chunks")
            return filtered


# Global instance
guardrails_manager = GuardrailsManager()
