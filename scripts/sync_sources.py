from __future__ import annotations
import subprocess
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[1]
cfg=yaml.safe_load((ROOT/"sources/sources.yaml").read_text(encoding="utf-8"))
vendor=ROOT/"vendor"; vendor.mkdir(exist_ok=True)

for src in sorted(cfg["sources"], key=lambda x: -x.get("priority",0)):
    if not src.get("canonical",True):
        continue
    dst=vendor/src["id"]
    if (dst/".git").exists():
        print("UPDATE",src["id"])
        subprocess.run(["git","-C",str(dst),"pull","--ff-only"],check=False)
    else:
        print("CLONE",src["id"])
        subprocess.run(["git","clone","--depth","1",src["repo"],str(dst)],check=False)
