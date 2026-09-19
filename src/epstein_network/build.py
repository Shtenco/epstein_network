from __future__ import annotations
import argparse, csv, json, sqlite3
from collections import defaultdict
from pathlib import Path
from .normalize import extract_emails, extract_phones, norm_email, norm_name, stable_id, text

PERSON_KEYS = {"name","person","person_name","full_name","contact","passenger","sender_name","recipient_name"}
EMAIL_KEYS = {"email","emails","email_address","from","to","sender","recipient","recipients","cc","bcc","sender_email","recipient_email"}
PHONE_KEYS = {"phone","phones","phone_number","telephone","mobile"}

def _json_records(p: Path):
    with p.open("r",encoding="utf-8",errors="replace") as f:
        if p.suffix.lower()==".jsonl":
            for i,line in enumerate(f,start=1):
                try:
                    x=json.loads(line)
                    if isinstance(x,dict): yield i,x
                except Exception:
                    pass
            return
        try:
            obj=json.load(f)
        except Exception:
            return
        if isinstance(obj,list):
            seq=obj
        elif isinstance(obj,dict):
            seq=[]
            for key in ("data","records","items","contacts","people","nodes","edges","relationships","emails","flights"):
                if isinstance(obj.get(key),list):
                    seq.extend(obj[key])
        else:
            seq=[]
        for i,x in enumerate(seq,start=1):
            if isinstance(x,dict): yield i,x

def _sqlite_records(p: Path):
    con=sqlite3.connect(f"file:{p}?mode=ro",uri=True)
    con.row_factory=sqlite3.Row
    try:
        tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        for table in tables:
            safe=table.replace('"','""')
            try:
                cur=con.execute(f'SELECT * FROM "{safe}"')
                for i,row in enumerate(cur,start=1):
                    d=dict(row); d["__table__"]=table
                    yield i,d
            except sqlite3.DatabaseError:
                continue
    finally:
        con.close()

def iter_records(root: Path):
    for p in root.rglob("*"):
        if not p.is_file() or ".git" in p.parts:
            continue
        try:
            suf=p.suffix.lower()
            if suf==".csv":
                with p.open("r",encoding="utf-8",errors="replace",newline="") as f:
                    for i,row in enumerate(csv.DictReader(f),start=2): yield p,i,row
            elif suf in {".json",".jsonl"}:
                for i,row in _json_records(p): yield p,i,row
            elif suf in {".db",".sqlite",".sqlite3"}:
                for i,row in _sqlite_records(p): yield p,i,row
        except Exception:
            continue

def pick_person(row):
    low={str(k).casefold():v for k,v in row.items()}
    for k in PERSON_KEYS:
        if k in low and text(low[k]):
            return text(low[k])
    return ""

def collect_values(row, keys):
    vals=[]
    for k,v in row.items():
        if str(k).casefold() in keys:
            if isinstance(v,list): vals.extend(map(text,v))
            else: vals.append(text(v))
    return vals

def build(vendor: Path, out: Path):
    nodes,edges={},{}
    evidence=[]
    source_counts=defaultdict(int)

    def add_node(kind,canonical,**attrs):
        key={"Person":norm_name,"EmailAddress":norm_email}.get(kind,text)(canonical)
        if not key:return None
        nid=stable_id(kind.lower(),key)
        n=nodes.setdefault(nid,{"id":nid,"type":kind,"canonical":canonical,"normalized":key})
        for k,v in attrs.items():
            if v not in ("",None,[]):n.setdefault(k,v)
        return nid

    def add_edge(a,b,rel,source_repo,source_file,source_row,confidence=0.6,**attrs):
        if not a or not b or a==b:return
        eid=stable_id("edge",f"{a}|{rel}|{b}|{source_repo}|{source_file}|{source_row}")
        e={"id":eid,"source":a,"target":b,"type":rel,"confidence":confidence,
           "source_repo":source_repo,"source_file":source_file,"source_row":source_row}
        e.update({k:v for k,v in attrs.items() if v not in ("",None,[])})
        edges[eid]=e

    for path,rownum,row in iter_records(vendor):
        relpath=str(path.relative_to(vendor))
        source_repo=path.parts[len(vendor.parts)] if len(path.parts)>len(vendor.parts) else "unknown"
        source_counts[source_repo]+=1
        person=pick_person(row)
        pid=add_node("Person",person) if person else None
        all_text=" | ".join(text(v) for v in row.values())

        emails=set()
        for v in collect_values(row,EMAIL_KEYS)+[all_text]:
            emails.update(extract_emails(v))
        phones=set()
        for v in collect_values(row,PHONE_KEYS)+[all_text]:
            phones.update(extract_phones(v))

        for email in emails:
            eid=add_node("EmailAddress",email,status="historical_or_unknown")
            if pid:add_edge(pid,eid,"HAS_EMAIL",source_repo,relpath,rownum,0.8)
        for phone in phones:
            phid=add_node("PhoneNumber",phone)
            if pid:add_edge(pid,phid,"HAS_PHONE",source_repo,relpath,rownum,0.75)

        low={str(k).casefold():text(v) for k,v in row.items()}
        senders,recipients=set(),set()
        for k in ("from","sender","sender_email"):
            senders.update(extract_emails(low.get(k,"")))
        for k in ("to","recipient","recipients","recipient_email","cc","bcc"):
            recipients.update(extract_emails(low.get(k,"")))
        for s in senders:
            sid=add_node("EmailAddress",s,status="historical_or_unknown")
            for r in recipients:
                rid=add_node("EmailAddress",r,status="historical_or_unknown")
                add_edge(sid,rid,"SENT_EMAIL_TO",source_repo,relpath,rownum,0.95)

        evidence.append({"source_repo":source_repo,"source_file":relpath,"source_row":rownum})

    out.mkdir(parents=True,exist_ok=True)
    with (out/"nodes.csv").open("w",encoding="utf-8",newline="") as f:
        fields=["id","type","canonical","normalized","status"]
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(nodes.values())
    with (out/"edges.csv").open("w",encoding="utf-8",newline="") as f:
        fields=["id","source","target","type","confidence","source_repo","source_file","source_row"]
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(edges.values())
    with (out/"evidence.jsonl").open("w",encoding="utf-8") as f:
        for x in evidence:f.write(json.dumps(x,ensure_ascii=False)+"\n")
    stats={"nodes":len(nodes),"edges":len(edges),"records_scanned":sum(source_counts.values()),
           "records_by_source":dict(sorted(source_counts.items()))}
    (out/"stats.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2),encoding="utf-8")
    return stats

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--vendor",default="vendor")
    ap.add_argument("--out",default="data/processed")
    a=ap.parse_args()
    print(json.dumps(build(Path(a.vendor),Path(a.out)),indent=2))

if __name__=="__main__":main()
