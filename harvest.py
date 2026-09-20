import sys, time, re, json, urllib.request, urllib.parse, urllib.error, html

BASE = "https://export.arxiv.org/oai2"
frm, until, out = sys.argv[1], sys.argv[2], sys.argv[3]
log = open(out + ".log", "a")
def L(msg):
    log.write(time.strftime("%H:%M:%S ") + msg + "\n"); log.flush()

rec_re = re.compile(r"<record>(.*?)</record>", re.S)
def field(rec, tag):
    m = re.search(r"<%s>(.*?)</%s>" % (tag, tag), rec, re.S)
    return html.unescape(m.group(1).strip()) if m else None

def fetch(url, tries=12):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "arxiv-math-trend-harvester/0.1 (personal research)"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            ra = e.headers.get("Retry-After")
            wait = int(ra) if ra and ra.isdigit() else min(60, 5 * (i + 1))
            L(f"HTTP {e.code}, retry in {wait}s ({url[-80:]})"); time.sleep(wait)
        except Exception as e:
            wait = min(60, 5 * (i + 1))
            L(f"ERR {e!r}, retry in {wait}s"); time.sleep(wait)
    raise SystemExit("gave up")

params = {"verb": "ListRecords", "set": "math", "metadataPrefix": "arXiv", "from": frm, "until": until}
url = BASE + "?" + urllib.parse.urlencode(params)
n = page = 0
with open(out, "a") as f:
    while True:
        t0 = time.time()
        body = fetch(url)
        recs = rec_re.findall(body)
        for rec in recs:
            if "<header status=\"deleted\"" in rec or "status='deleted'" in rec:
                continue
            aid, created, cats = field(rec, "id"), field(rec, "created"), field(rec, "categories")
            if not aid or not created:
                continue
            f.write(json.dumps({"id": aid, "c": created, "k": cats, "u": field(rec, "updated")}) + "\n")
            n += 1
        f.flush(); page += 1
        m = re.search(r"<resumptionToken[^>]*>([^<]+)</resumptionToken>", body)
        tot = re.search(r'completeListSize="(\d+)"', body)
        L(f"page {page} recs={len(recs)} total={n} listSize={tot.group(1) if tot else '?'} {time.time()-t0:.1f}s")
        if not m or not m.group(1).strip():
            break
        url = BASE + "?" + urllib.parse.urlencode({"verb": "ListRecords", "resumptionToken": html.unescape(m.group(1).strip())})
        time.sleep(1.0)
L("DONE")
print("DONE", n)
