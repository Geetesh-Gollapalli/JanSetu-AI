import re, uuid
from datetime import datetime, timezone

PHONE_PATTERN = re.compile(r'(\+91[\-\s]?)?[6-9]\d{9}')
AADHAAR_PATTERN = re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b')

class IngestionPipeline:
    @staticmethod
    def scrub_pii(text):
        had_pii = bool(PHONE_PATTERN.search(text) or AADHAAR_PATTERN.search(text))
        cleaned = PHONE_PATTERN.sub('[REDACTED_PHONE]', text)
        cleaned = AADHAAR_PATTERN.sub('[REDACTED_AADHAAR]', cleaned)
        return cleaned, had_pii

    @staticmethod
    def detect_language(text):
        for c in text:
            code = ord(c)
            if 0x0900 <= code <= 0x097F: return ("mr" if any(w in text for w in ['आहे', 'पूल', 'गाव']) else "hi"), "Hindi/Marathi"
            if 0x0B00 <= code <= 0x0B7F: return "or", "Odia"
            if 0x0980 <= code <= 0x09FF: return "bn", "Bengali"
            if 0x0B80 <= code <= 0x0BFF: return "ta", "Tamil"
            if 0x0C00 <= code <= 0x0C7F: return "te", "Telugu"
            if 0x0C80 <= code <= 0x0CFF: return "kn", "Kannada"
        return "en", "English"

    @staticmethod
    def classify_sector(text):
        t = text.lower()
        if any(w in t for w in ['पानी', 'जल', 'हैंडपंप', 'water', 'arsenic', 'fluoride']): return "Water & Sanitation"
        if any(w in t for w in ['सड़क', 'पुल', 'road', 'bridge', 'पूल']): return "Roads & Bridges"
        if any(w in t for w in ['अस्पताल', 'डॉक्टर', 'ambulance', 'health', 'ଡାକ୍ତରଖାନା']): return "Healthcare & Sanitation"
        return "General Public Works"

    @classmethod
    def process_raw_input(cls, payload):
        txt, pii = cls.scrub_pii(payload.get('text', ''))
        code, name = cls.detect_language(txt)
        return {
            "request_id": f"REQ-{uuid.uuid4().hex[:6].upper()}",
            "original_transcript": txt,
            "language": name,
            "sector": cls.classify_sector(txt),
            "urgency_level": "Critical" if any(w in txt.lower() for w in ['मरीज', 'emergency', 'मौत', 'तुटतात', 'arsenic']) else "High",
            "pii_redacted": pii
        }
