import gzip, json
from pathlib import Path

base = Path("data/derived/compressed")
files = sorted(base.glob("cfbd_*.json.gz"))
out = {}
for path in files:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        sample = data[0] if data else None
        out[path.name] = {
            "type": "list", "rows": len(data),
            "sample_keys": sorted(sample.keys()) if isinstance(sample, dict) else [],
            "sample": sample
        }
    elif isinstance(data, dict):
        out[path.name] = {
            "type": "dict", "keys": sorted(data.keys()),
            "sample": {k: (v[0] if isinstance(v, list) and v else v) for k,v in data.items()}
        }
    else:
        out[path.name] = {"type": type(data).__name__}
Path("data/derived/cfbd_schema_inspection.json").write_text(
    json.dumps(out, indent=2, default=str), encoding="utf-8"
)
print(json.dumps({k: {x:v for x,v in d.items() if x != "sample"} for k,d in out.items()}, indent=2))
