from __future__ import annotations
import csv, json, re
from collections import defaultdict
from pathlib import Path
from difflib import SequenceMatcher
from .normalize import norm_name, norm_email, norm_phone, stable_id

def token_key(name:str)->str:
    toks=[t for t in re.split(r"\s+",norm_name(name)) if t]
    return " ".join(sorted(toks))

def initials_key(name:str)->str:
    toks=[t for t in re.split(r"\s+",norm_name(name)) if t]
    return "".join(t[0] for t in toks if t)

def similarity(a:str,b:str)->float:
    if not a or not b:return 0.0
    if norm_name(a)==norm_name(b):return 1.0
    if token_key(a)==token_key(b):return 0.97
    return SequenceMatcher(None,norm_name(a),norm_name(b)).ratio()

def resolve(nodes_csv:Path,out_csv:Path,review_csv:Path):
    rows=list(csv.DictReader(nodes_csv.open(encoding="utf-8")))
    persons=[r for r in rows if r["type"]=="Person"]
    groups=defaultdict(list)
    for r in persons:
        groups[token_key(r["canonical"])].append(r)
    canonical_map={}
    review=[]
    for key,items in groups.items():
        if not key: continue
        canonical=max(items,key=lambda r:len(r["canonical"]))
        for r in items:
            canonical_map[r["id"]]=canonical["id"]
            if r["id"]!=canonical["id"]:
                review.append({"left":r["canonical"],"right":canonical["canonical"],"score":1.0,"reason":"token_key"})
    # cautious fuzzy pass: only high similarity and same initials
    reps=[r for r in persons if canonical_map.get(r["id"],r["id"])==r["id"]]
    for i,a in enumerate(reps):
        for b in reps[i+1:]:
            if initials_key(a["canonical"])!=initials_key(b["canonical"]): continue
            s=similarity(a["canonical"],b["canonical"])
            if s>=0.94:
                review.append({"left":a["canonical"],"right":b["canonical"],"score":round(s,4),"reason":"fuzzy_review"})
    out_csv.parent.mkdir(parents=True,exist_ok=True)
    with out_csv.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["source_id","canonical_id"])
        w.writeheader()
        for r in persons:w.writerow({"source_id":r["id"],"canonical_id":canonical_map.get(r["id"],r["id"])})
    with review_csv.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["left","right","score","reason"]);w.writeheader();w.writerows(review)
    return {"persons":len(persons),"mapped":sum(1 for k,v in canonical_map.items() if k!=v),"review_candidates":len(review)}
