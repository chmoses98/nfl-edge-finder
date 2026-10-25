#!/usr/bin/env python3
"""Which RUN NFL packet did the analyst read?  pin_packet.py --submission S --reports hr [--github-env FILE]

Prints `LATEST`, or the artifact name (run-nfl-<season>-w<NN>-<run id>) recorded in <reports>/history/index.jsonl for the packet sha named in the submission.
The workflow downloads that artifact with `gh run download`; the branch itself holds only the newest packet."""
import argparse
import json
import re
import sys


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submission", required=True)
    ap.add_argument("--reports", required=True)
    a = ap.parse_args(argv)
    sha = str(json.load(open(a.submission)).get("packet_sha") or "")
    latest = json.load(open(a.reports + "/latest/packet.json")).get("packet_sha")
    if not re.fullmatch(r"[0-9a-f]{20}", sha) or sha == latest:
        print("LATEST")
        return 0
    art = ""
    for line in open(a.reports + "/history/index.jsonl"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("packet_sha") == sha and d.get("artifact_name"):
            art = d["artifact_name"]
    print(art or "MISSING")
    return 0


if __name__ == "__main__":
    sys.exit(main())
