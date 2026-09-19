from __future__ import annotations
import hashlib, re, unicodedata
from typing import Any

EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\w)(?:\+?\d[\d().\-\s]{6,}\d)")

def text(v: Any) -> str:
    if v is None:
        return ""
    return unicodedata.normalize("NFKC", str(v)).strip()

def norm_name(v: Any) -> str:
    s = re.sub(r"\s+", " ", text(v))
    s = re.sub(r"[^\w\s.'’-]", " ", s, flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip().casefold()

def norm_email(v: Any) -> str:
    return text(v).strip("<> ,;").casefold()

def norm_phone(v: Any) -> str:
    s = text(v)
    plus = s.strip().startswith("+")
    digits = re.sub(r"\D", "", s)
    return ("+" if plus else "") + digits

def stable_id(kind: str, value: str) -> str:
    return f"{kind}:" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]

def extract_emails(v: Any) -> list[str]:
    return sorted({norm_email(x) for x in EMAIL_RE.findall(text(v))})

def extract_phones(v: Any) -> list[str]:
    return sorted({norm_phone(x) for x in PHONE_RE.findall(text(v)) if len(re.sub(r"\D","",x)) >= 7})
