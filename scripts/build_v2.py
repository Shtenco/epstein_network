from pathlib import Path
import csv, json, yaml
from epstein_network.build import build, iter_records
from epstein_network.entity_resolution import resolve
from epstein_network.normalize import stable_id, norm_name, norm_email, norm_phone, text
from epstein_network.source_specific import explicit_entities, explicit_edges

root=Path(__file__).resolve().parents[1]
out=root/"data/processed"
stats=build(root/"vendor_snapshot",out)

profiles=yaml.safe_load((root/"sources/source_profiles.yaml").read_text(encoding="utf-8")).get("profiles",{})
nodes_path=out/"nodes.csv"; edges_path=out/"edges.csv"
nodes={r["id"]:r for r in csv.DictReader(nodes_path.open(encoding="utf-8"))}
edges={r["id"]:r for r in csv.DictReader(edges_path.open(encoding="utf-8"))}

def norm(kind,value):
    if kind=="Person": return norm_name(value)
    if kind=="EmailAddress": return norm_email(value)
    if kind=="PhoneNumber": return norm_phone(value)
    return text(value).casefold()

def add_node(kind,value,status=""):
    key=norm(kind,value)
    if not key:return None
    nid=stable_id(kind.lower(),key)
    nodes.setdefault(nid,{"id":nid,"type":kind,"canonical":value,"normalized":key,"status":status})
    return nid

def add_edge(a,b,rel,source_repo,source_file,source_row,confidence):
    aid=add_node(*a,status="historical_or_unknown" if a[0]=="EmailAddress" else "")
    bid=add_node(*b,status="historical_or_unknown" if b[0]=="EmailAddress" else "")
    if not aid or not bid or aid==bid:return
    eid=stable_id("edge",f"{aid}|{rel}|{bid}|{source_repo}|{source_file}|{source_row}")
    edges[eid]={"id":eid,"source":aid,"target":bid,"type":rel,"confidence":confidence,
                "source_repo":source_repo,"source_file":source_file,"source_row":source_row}

for path,rownum,row in iter_records(root/"vendor_snapshot"):
    rel=path.relative_to(root/"vendor_snapshot")
    source_repo=rel.parts[0] if rel.parts else "unknown"
    profile=profiles.get(source_repo,{})
    for kind,value in explicit_entities(row,profile):
        add_node(kind,value,status="historical_or_unknown" if kind=="EmailAddress" else "")
    for a,b,reltype,conf in explicit_edges(row,profile):
        add_edge(a,b,reltype,source_repo,str(rel),rownum,conf)

with nodes_path.open("w",encoding="utf-8",newline="") as f:
    fields=["id","type","canonical","normalized","status"]
    w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(nodes.values())
with edges_path.open("w",encoding="utf-8",newline="") as f:
    fields=["id","source","target","type","confidence","source_repo","source_file","source_row"]
    w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(edges.values())

er=resolve(nodes_path,out/"entity_map.csv",out/"entity_review.csv")
kind_counts={}
for n in nodes.values():kind_counts[n["type"]]=kind_counts.get(n["type"],0)+1
edge_counts={}
for e in edges.values():edge_counts[e["type"]]=edge_counts.get(e["type"],0)+1
v2={"graph":{"nodes":len(nodes),"edges":len(edges),"node_types":kind_counts,"edge_types":edge_counts},"entity_resolution":er}
(out/"v2_stats.json").write_text(json.dumps(v2,indent=2,ensure_ascii=False),encoding="utf-8")
print(json.dumps(v2,indent=2,ensure_ascii=False))
