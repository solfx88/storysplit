#!/usr/bin/env python3
"""
get_vendor.py

Downloads the ffmpeg.wasm files StorySplit needs into a local "vendor" folder,
so the app can load them from your own origin instead of a CDN.

Run this once, from the StorySplit folder:

    cd C:\\Tools\\StorySplit
    py get_vendor.py

Total download is about 32 MB (the ffmpeg-core.wasm binary is most of it).
"""

import sys
import urllib.request
from pathlib import Path

FFMPEG_VER = "0.12.10"
CORE_VER = "0.12.6"

# When classWorkerURL is used, ffmpeg creates the worker with {type:"module"},
# so the worker and core must be the ESM builds, not UMD. worker.js also
# imports ./const.js and ./errors.js relatively, so those come along too.
FILES = [
    (f"https://unpkg.com/@ffmpeg/ffmpeg@{FFMPEG_VER}/dist/umd/ffmpeg.js", "ffmpeg.js"),
    (f"https://unpkg.com/@ffmpeg/ffmpeg@{FFMPEG_VER}/dist/esm/worker.js", "worker.js"),
    (f"https://unpkg.com/@ffmpeg/ffmpeg@{FFMPEG_VER}/dist/esm/const.js", "const.js"),
    (f"https://unpkg.com/@ffmpeg/ffmpeg@{FFMPEG_VER}/dist/esm/errors.js", "errors.js"),
    (f"https://unpkg.com/@ffmpeg/core@{CORE_VER}/dist/esm/ffmpeg-core.js", "ffmpeg-core.js"),
    (f"https://unpkg.com/@ffmpeg/core@{CORE_VER}/dist/esm/ffmpeg-core.wasm", "ffmpeg-core.wasm"),
]

# Exact sizes verified against the published npm packages, used as a sanity
# check that we got the real file and not an error page.
EXPECTED_BYTES = {
    "ffmpeg.js": 4_126,
    "worker.js": 4_810,
    "const.js": 974,
    "errors.js": 332,
    "ffmpeg-core.js": 114_494,
    "ffmpeg-core.wasm": 32_129_114,
}


def download(url: str, dest: Path) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": "StorySplit-setup"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        data = resp.read()
    dest.write_bytes(data)
    return len(data)


def main():
    vendor = Path(__file__).resolve().parent / "vendor"
    vendor.mkdir(exist_ok=True)

    print(f"Downloading ffmpeg files into: {vendor}\n")

    failures = []
    for url, name in FILES:
        dest = vendor / name
        print(f"  {name} ... ", end="", flush=True)
        try:
            size = download(url, dest)
        except Exception as e:
            print(f"FAILED ({e})")
            failures.append(name)
            continue

        expected = EXPECTED_BYTES.get(name)
        if expected is not None and size != expected:
            print(f"MISMATCH — got {size:,} bytes, expected {expected:,}")
            failures.append(name)
        else:
            print(f"ok  {size:,} bytes")

    print()
    if failures:
        print("These files did not download correctly:")
        for f in failures:
            print(f"  - {f}")
        print("\nCheck your internet connection and run the script again.")
        sys.exit(1)

    print("All files downloaded. Verifying folder contents:\n")
    for _, name in FILES:
        p = vendor / name
        print(f"  {name:<22} {p.stat().st_size:>12,} bytes")

    print("\nDone. Reload StorySplit in your browser (Ctrl+Shift+R).")


if __name__ == "__main__":
    main()
