import subprocess, sys, orjson, pickle, collections
repo, out = sys.argv[1], sys.argv[2]
names = subprocess.run(["git","-C",repo,"ls-tree","-r","--name-only","HEAD","data/kalshi/capture"],capture_output=True,text=True).stdout.split()
qs = sorted(n for n in names if n.endswith(".quotes.jsonl"))
p = subprocess.Popen(["git","-C",repo,"cat-file","--batch"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
T = {}
runs = collections.Counter()
nrows = 0
def f(x):
    try: return float(x) if x not in (None,"") else None
    except: return None
for i,n in enumerate(qs):
    p.stdin.write(("HEAD:"+n+"\n").encode()); p.stdin.flush()
    hdr = p.stdout.readline().split()
    size = int(hdr[2]); data = p.stdout.read(size); p.stdout.read(1)
    runs[n.split("/")[3]] += 1
    for line in data.splitlines():
        if not line: continue
        try: r = orjson.loads(line)
        except Exception: continue
        nrows += 1
        t = r.get("ticker")
        a = T.get(t)
        if a is None:
            a = T[t] = {k: r.get(k) for k in ("series_ticker","event_ticker","family","period","stat","team","player_name","player_kalshi_id","threshold","operator","game_id","kickoff_utc","close_time")}
            a.update(n=0,npre=0,nexec_pre=0,nboth=0,first=r.get("observed_at"),last=None,last_pre=None,last_pre_q=None,status=None,result=None,maxvol=0.0)
        a["n"] += 1
        ya, na = f(r.get("yes_ask_dollars")), f(r.get("no_ask_dollars"))
        both = ya is not None and na is not None and 0 < ya < 1 and 0 < na < 1
        if both: a["nboth"] += 1
        if r.get("pregame"):
            a["npre"] += 1
            if both: a["nexec_pre"] += 1
            a["last_pre"] = r.get("observed_at"); a["last_pre_q"] = (ya, na, f(r.get("yes_bid_dollars")), f(r.get("no_bid_dollars")), r.get("minutes_to_kickoff"))
        a["last"] = r.get("observed_at"); a["status"] = r.get("status")
        if r.get("result"): a["result"] = r.get("result")
        v = f(r.get("volume_fp")); 
        if v and v > a["maxvol"]: a["maxvol"] = v
        if r.get("game_id") and not a["game_id"]: a["game_id"] = r.get("game_id")
    if i % 200 == 0: print(i, len(qs), nrows, len(T), flush=True)
pickle.dump({"T":T,"runs":runs,"nrows":nrows,"nfiles":len(qs)}, open(out,"wb"))
print("done", nrows, len(T))
