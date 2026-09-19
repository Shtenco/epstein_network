from __future__ import annotations
import csv, json, sqlite3
from pathlib import Path

class BaseAdapter:
    id="base"
    def accepts(self,path:Path)->bool:return False
    def records(self,path:Path):return []

class CsvAdapter(BaseAdapter):
    id="csv"
    def accepts(self,path):return path.suffix.lower()==".csv"
    def records(self,path):
        with path.open(encoding="utf-8",errors="replace",newline="") as f:
            for i,row in enumerate(csv.DictReader(f),start=2):
                yield i,row

class JsonAdapter(BaseAdapter):
    id="json"
    def accepts(self,path):return path.suffix.lower() in {".json",".jsonl"}
    def records(self,path):
        if path.suffix.lower()==".jsonl":
            with path.open(encoding="utf-8",errors="replace") as f:
                for i,line in enumerate(f,start=1):
                    try:
                        x=json.loads(line)
                        if isinstance(x,dict):yield i,x
                    except Exception:pass
            return
        with path.open(encoding="utf-8",errors="replace") as f:
            try:obj=json.load(f)
            except Exception:return
        seq=obj if isinstance(obj,list) else []
        if isinstance(obj,dict):
            for k in ("data","records","items","contacts","people","nodes","edges","relationships","emails","flights"):
                if isinstance(obj.get(k),list):seq.extend(obj[k])
        for i,x in enumerate(seq,start=1):
            if isinstance(x,dict):yield i,x

class SqliteAdapter(BaseAdapter):
    id="sqlite"
    def accepts(self,path):return path.suffix.lower() in {".db",".sqlite",".sqlite3"}
    def records(self,path):
        con=sqlite3.connect(f"file:{path}?mode=ro",uri=True);con.row_factory=sqlite3.Row
        try:
            tables=[r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
            for table in tables:
                safe=table.replace('"','""')
                try:
                    for i,row in enumerate(con.execute(f'SELECT * FROM "{safe}"'),start=1):
                        d=dict(row);d["__table__"]=table;yield i,d
                except sqlite3.DatabaseError:pass
        finally:con.close()

ADAPTERS=[CsvAdapter(),JsonAdapter(),SqliteAdapter()]
