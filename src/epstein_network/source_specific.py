from __future__ import annotations
import re
from .normalize import text, norm_name, norm_email, norm_phone, stable_id, extract_emails, extract_phones

GENERIC_ORG_FIELDS=("organization","organisation","company","employer","institution","affiliation")
GENERIC_ADDRESS_FIELDS=("address","street_address","location")
GENERIC_DOC_FIELDS=("document","document_id","file","filename","source_document")
GENERIC_FLIGHT_FIELDS=("flight","flight_id","tail_number","aircraft","plane")
GENERIC_DATE_FIELDS=("date","sent","timestamp","flight_date","event_date")

def lowrow(row):
    return {str(k).strip().casefold():v for k,v in row.items()}

def first(low, keys):
    for k in keys:
        v=low.get(k)
        if v not in (None,"",[],{}): return text(v)
    return ""

def explicit_entities(row, profile):
    low=lowrow(row)
    out=[]
    person=first(low,profile.get("person_fields",[]))
    if person: out.append(("Person",person))
    for f in profile.get("email_fields",[]):
        for e in extract_emails(low.get(f,"")): out.append(("EmailAddress",e))
    for f in profile.get("phone_fields",[]):
        for p in extract_phones(low.get(f,"")): out.append(("PhoneNumber",p))
    org=first(low,profile.get("organization_fields",GENERIC_ORG_FIELDS))
    if org: out.append(("Organization",org))
    addr=first(low,profile.get("address_fields",GENERIC_ADDRESS_FIELDS))
    if addr: out.append(("Address",addr))
    doc=first(low,profile.get("document_fields",GENERIC_DOC_FIELDS))
    if doc: out.append(("Document",doc))
    flight=first(low,profile.get("flight_fields",GENERIC_FLIGHT_FIELDS))
    if flight: out.append(("Flight",flight))
    return out

def explicit_edges(row, profile):
    low=lowrow(row)
    edges=[]
    senders=set(); recipients=set()
    for k in ("from","sender","sender_email"):
        senders.update(extract_emails(low.get(k,"")))
    for k in ("to","recipient","recipients","recipient_email"):
        recipients.update(extract_emails(low.get(k,"")))
    cc=set()
    for k in ("cc","bcc"):
        cc.update(extract_emails(low.get(k,"")))
    for s in senders:
        for r in recipients: edges.append((("EmailAddress",s),("EmailAddress",r),"SENT_EMAIL_TO",0.98))
        for r in cc: edges.append((("EmailAddress",s),("EmailAddress",r),"CC_EMAIL",0.98))

    person=first(low,profile.get("person_fields",[]))
    if person:
        for f in profile.get("email_fields",[]):
            for e in extract_emails(low.get(f,"")):
                edges.append((("Person",person),("EmailAddress",e),"HAS_EMAIL",0.90))
        for f in profile.get("phone_fields",[]):
            for p in extract_phones(low.get(f,"")):
                edges.append((("Person",person),("PhoneNumber",p),"HAS_PHONE",0.90))
        org=first(low,profile.get("organization_fields",GENERIC_ORG_FIELDS))
        if org: edges.append((("Person",person),("Organization",org),"AFFILIATED_WITH",0.75))
        addr=first(low,profile.get("address_fields",GENERIC_ADDRESS_FIELDS))
        if addr: edges.append((("Person",person),("Address",addr),"HAS_ADDRESS",0.82))
        flight=first(low,profile.get("flight_fields",GENERIC_FLIGHT_FIELDS))
        if flight: edges.append((("Person",person),("Flight",flight),"FLEW_ON",0.88))
        doc=first(low,profile.get("document_fields",GENERIC_DOC_FIELDS))
        if doc: edges.append((("Person",person),("Document",doc),"MENTIONED_IN",0.72))
    return edges
