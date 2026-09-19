from __future__ import annotations
import hashlib, json, os, shutil, subprocess
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
CFG=yaml.safe_load((ROOT/"sources/sources.yaml").read_text(encoding="utf-8"))
VENDOR=ROOT/"vendor"
SNAP=ROOT/"vendor_snapshot"
MANIFEST=ROOT/"vendor_manifest.json"

INCLUDE_EXT={".csv",".json",".jsonl",".parquet",".db",".sqlite",".sqlite3",".py",".js",".ts",".tsx",".md",".yaml",".yml",".txt",".gexf",".graphml",".cypher"}
MAX_FILE=95*1024*1024

def sha256(path: Path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def run(*args, cwd=None):
    return subprocess.run(args,cwd=cwd,check=False,text=True,capture_output=True)

def clone_or_update(src):
    dst=VENDOR/src["id"]
    if (dst/".git").exists():
        run("git","fetch","--all","--tags","--prune",cwd=dst)
        run("git","reset","--hard","origin/HEAD",cwd=dst)
    else:
        run("git","clone","--depth","1",src["repo"],str(dst))
    return dst

def copy_relevant(src_id, repo_dir):
    target=SNAP/src_id
    if target.exists(): shutil.rmtree(target)
    target.mkdir(parents=True,exist_ok=True)
    copied=[]; skipped=[]
    for p in repo_dir.rglob("*"):
        if not p.is_file() or ".git" in p.parts: continue
        rel=p.relative_to(repo_dir)
        if p.suffix.lower() not in INCLUDE_EXT:
            skipped.append({"path":str(rel),"reason":"extension"})
            continue
        size=p.stat().st_size
        if size>MAX_FILE:
            skipped.append({"path":str(rel),"reason":"size","bytes":size,"sha256":sha256(p)})
            continue
        out=target/rel
        out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,out)
        copied.append({"path":str(rel),"bytes":size,"sha256":sha256(p)})
    return copied, skipped

def main():
    VENDOR.mkdir(exist_ok=True); SNAP.mkdir(exist_ok=True)
    manifest={"sources":[]}
    for src in sorted(CFG["sources"],key=lambda x:-x.get("priority",0)):
        if not src.get("canonical",True): continue
        print("SOURCE",src["id"])
        repo_dir=clone_or_update(src)
        head=run("git","rev-parse","HEAD",cwd=repo_dir).stdout.strip()
        copied,skipped=copy_relevant(src["id"],repo_dir)
        manifest["sources"].append({
            "id":src["id"],"repo":src["repo"],"head":head,
            "roles":src.get("roles",[]),"copied":copied,"skipped":skipped
        })
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print("WROTE",MANIFEST)

if __name__=="__main__": main()
