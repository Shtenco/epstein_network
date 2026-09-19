from __future__ import annotations
import hashlib, json, os, shutil, subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/"sources/sources.json").read_text(encoding="utf-8"))
VENDOR=ROOT/"vendor"
SNAP=ROOT/"vendor_snapshot"
MANIFEST=ROOT/"vendor_manifest.json"

INCLUDE_EXT={".csv",".json",".jsonl",".parquet",".db",".sqlite",".sqlite3",".py",".js",".ts",".tsx",".md",".yaml",".yml",".txt",".gexf",".graphml",".cypher"}
MAX_FILE=95*1024*1024
MAX_SOURCE=350*1024*1024

def run(args,cwd=None,text=True):
    return subprocess.run(args,cwd=cwd,check=False,capture_output=True,text=text)

def ensure_repo(src):
    dst=VENDOR/src["id"]
    if dst.exists(): shutil.rmtree(dst)
    r=run(["git","clone","--depth","1","--filter=blob:none","--no-checkout",src["repo"],str(dst)])
    if r.returncode:
        raise RuntimeError(f"clone failed {src['id']}: {r.stderr[-1000:]}")
    return dst

def tree(repo):
    r=run(["git","ls-tree","-r","-l","HEAD"],cwd=repo)
    if r.returncode: raise RuntimeError(r.stderr)
    for line in r.stdout.splitlines():
        try:
            left,path=line.split("\t",1)
            mode,typ,sha,size=left.split()
            yield path,int(size) if size!="-" else 0,sha
        except Exception:
            continue

def blob(repo,path):
    r=run(["git","show",f"HEAD:{path}"],cwd=repo,text=False)
    if r.returncode: raise RuntimeError(r.stderr.decode("utf-8","replace")[-1000:])
    return r.stdout

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()

def score_path(path):
    p=path.casefold()
    score=0
    for word,w in [("email",30),("contact",30),("black_book",30),("blackbook",30),("flight",25),("relationship",25),("network",20),("person",20),("entity",20),("node",15),("edge",15),("graph",15),("data/",10),("processed",10),("final",10)]:
        if word in p: score+=w
    return score

def snapshot(src,repo):
    target=SNAP/src["id"]
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True,exist_ok=True)
    candidates=[]; skipped=[]; copied=[]; used=0
    for path,size,git_sha in tree(repo):
        ext=Path(path).suffix.lower()
        if ext not in INCLUDE_EXT:
            skipped.append({"path":path,"reason":"extension","bytes":size,"git_sha":git_sha}); continue
        if size>MAX_FILE:
            skipped.append({"path":path,"reason":"file_size","bytes":size,"git_sha":git_sha}); continue
        candidates.append((score_path(path),path,size,git_sha))
    candidates.sort(key=lambda x:(-x[0],x[2],x[1]))
    for _,path,size,git_sha in candidates:
        if used+size>MAX_SOURCE:
            skipped.append({"path":path,"reason":"source_budget","bytes":size,"git_sha":git_sha}); continue
        try:b=blob(repo,path)
        except Exception as e:
            skipped.append({"path":path,"reason":"blob_error","error":str(e),"bytes":size,"git_sha":git_sha}); continue
        out=target/path; out.parent.mkdir(parents=True,exist_ok=True); out.write_bytes(b)
        used+=len(b)
        copied.append({"path":path,"bytes":len(b),"git_sha":git_sha,"sha256":sha256_bytes(b)})
    return copied,skipped,used

def main():
    VENDOR.mkdir(exist_ok=True); SNAP.mkdir(exist_ok=True)
    manifest={"version":2,"strategy":"partial-clone + graph-relevant snapshot","sources":[]}
    for src in sorted(CFG["sources"],key=lambda x:-x.get("priority",0)):
        if not src.get("canonical",True): continue
        print("SOURCE",src["id"],flush=True)
        try:
            repo=ensure_repo(src)
            head=run(["git","rev-parse","HEAD"],cwd=repo).stdout.strip()
            copied,skipped,total=snapshot(src,repo)
            manifest["sources"].append({"id":src["id"],"repo":src["repo"],"head":head,"roles":src.get("roles",[]),"status":"ok","snapshot_bytes":total,"copied":copied,"skipped":skipped})
        except Exception as e:
            manifest["sources"].append({"id":src["id"],"repo":src["repo"],"roles":src.get("roles",[]),"status":"error","error":str(e)})
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    ok=sum(1 for x in manifest["sources"] if x["status"]=="ok")
    print(f"VENDORED {ok}/{len(manifest['sources'])}",flush=True)

if __name__=="__main__": main()
