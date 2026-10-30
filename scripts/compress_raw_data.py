from pathlib import Path
import gzip
src = Path("data/raw")
out = Path("data/derived/compressed")
out.mkdir(parents=True, exist_ok=True)
for path in sorted(src.glob("*.json")):
    target = out / (path.name + ".gz")
    with path.open("rb") as fin, gzip.open(target, "wb", compresslevel=9) as fout:
        while True:
            chunk = fin.read(1024 * 1024)
            if not chunk:
                break
            fout.write(chunk)
    print(f"{path.name}: {path.stat().st_size} bytes -> {target.stat().st_size} bytes")
