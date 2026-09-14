"""
Fill recall and complaint counts into data/models.json from NHTSA's free public API.

WHAT THIS DOES
  For every model in data/models.json it asks NHTSA two questions:
    - how many safety recalls does this year/make/model have?
    - how many owner complaints have been filed against it?
  and writes the counts, the lookup URLs, and today's date into each entry.

WHAT IT DOES NOT DO
  It does not set reliability_score. Counts are not a reliability rating: a car
  that sold 200,000 units collects more complaints than one that sold 5,000,
  however well it was built, and NHTSA does not publish sales figures to correct
  for that. Read the counts, read the recall summaries, then set the 1-to-5
  score yourself in admin.html and write down what it was based on.

HOW TO USE
  From the site folder:
      python3 tools/fetch_nhtsa.py            # every model (slow: ~2 requests each)
      python3 tools/fetch_nhtsa.py --make Hyundai
      python3 tools/fetch_nhtsa.py --only 2026-hyundai-ioniq-5-rwd
      python3 tools/fetch_nhtsa.py --limit 20

  No API key is needed. Be polite: there is a pause between requests.

NAME MATCHING
  EPA and NHTSA name cars differently ("Ioniq 5 RWD" vs "IONIQ 5"). The script
  strips drive and trim words to guess NHTSA's name. When a guess returns
  nothing, it records nhtsa_lookup_failed so you can set "nhtsa_model" by hand
  in admin.html and run it again.

No API key. Source: https://www.nhtsa.gov/nhtsa-datasets-and-apis
"""
import argparse, json, os, re, sys, time
from datetime import date
from urllib.parse import quote
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
MODELS = os.path.join(SITE, "data", "models.json")

RECALLS = "https://api.nhtsa.gov/recalls/recallsByVehicle?make={make}&model={model}&modelYear={year}"
COMPLAINTS = "https://api.nhtsa.gov/complaints/complaintsByVehicle?make={make}&model={model}&modelYear={year}"
PAUSE_SECONDS = 0.5

TRIM_WORDS = {
    "rwd", "awd", "fwd", "4wd", "2wd", "long", "standard", "extended", "performance", "dual",
    "tri", "quad", "single", "max", "large", "range", "quattro", "with", "inch", "wheels",
    "plus", "premium", "limited", "touring", "pure", "gt-line", "gt", "xrt", "woodland",
    "motor", "pack", "sr", "lr",
}


def nhtsa_name(model):
    """Best guess at the name NHTSA files this car under.

    NHTSA lists the base model ("IONIQ 5"), EPA lists the version
    ("Ioniq 5 Standard range"). Keep everything up to the first trim word.
    """
    cleaned = re.sub(r"\(.*?\)", " ", model)                                  # drop "(22in)"
    cleaned = re.sub(r"\b[0-9]{3}/[0-9]{2}[A-Za-z][0-9]{2}\b", " ", cleaned)   # drop tyre sizes
    cleaned = re.sub(r"\bwith\s*[0-9]+", " with ", cleaned)                    # "with19" -> "with"
    kept = []
    for word in re.sub(r"\s+", " ", cleaned).strip().split():
        if word.lower().strip(".,") in TRIM_WORDS:
            break
        kept.append(word)
    return " ".join(kept) or model.split()[0]


def get_json(url):
    req = Request(url, headers={"User-Agent": "Volt-and-Ledger/1.0 (site data build script)"})
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def count_for(url_template, make, model, year):
    """Returns (count, url) or (None, url) if the lookup failed."""
    url = url_template.format(make=quote(make), model=quote(model), year=year)
    try:
        data = get_json(url)
    except (HTTPError, URLError, ValueError, TimeoutError) as e:
        print(f"    lookup failed ({e})")
        return None, url
    results = data.get("results")
    return (len(results) if isinstance(results, list) else None), url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--make", help="only this make, e.g. Hyundai")
    ap.add_argument("--only", help="only this model id")
    ap.add_argument("--limit", type=int, help="stop after this many models")
    ap.add_argument("--refresh", action="store_true", help="re-check models already done")
    args = ap.parse_args()

    if not os.path.exists(MODELS):
        sys.exit(f"Can't find {MODELS}. Run tools/build_models_from_epa.py first.")
    payload = json.load(open(MODELS))
    models = payload["models"]

    todo = []
    for m in models:
        if args.only and m["id"] != args.only:
            continue
        if args.make and m["make"].lower() != args.make.lower():
            continue
        if m.get("nhtsa_checked") and not args.refresh:
            continue
        todo.append(m)
    if args.limit:
        todo = todo[: args.limit]

    if not todo:
        print("Nothing to do. Use --refresh to re-check models already done.")
        return

    print(f"Checking {len(todo)} models against NHTSA. About {len(todo) * 2} requests.\n")
    done = failed = 0
    try:
        for i, m in enumerate(todo, 1):
            name = m.get("nhtsa_model") or nhtsa_name(m["model"])
            print(f"[{i}/{len(todo)}] {m['year']} {m['make']} {m['model']}  ->  NHTSA: {name}")
            recalls, recall_url = count_for(RECALLS, m["make"], name, m["year"])
            time.sleep(PAUSE_SECONDS)
            complaints, complaint_url = count_for(COMPLAINTS, m["make"], name, m["year"])
            time.sleep(PAUSE_SECONDS)

            if recalls is None and complaints is None:
                m["nhtsa_lookup_failed"] = True
                failed += 1
                print("    no result. Set \"nhtsa_model\" for this car in admin.html and run again.")
                continue

            m.pop("nhtsa_lookup_failed", None)
            m["nhtsa_model_used"] = name
            m["nhtsa_recalls"] = recalls
            m["nhtsa_complaints"] = complaints
            m["nhtsa_recall_url"] = recall_url
            m["nhtsa_complaint_url"] = complaint_url
            m["nhtsa_checked"] = date.today().isoformat()
            done += 1
            print(f"    {recalls} recalls, {complaints} complaints")
    except KeyboardInterrupt:
        print("\nStopped. Saving what was collected so far.")

    payload["nhtsa_note"] = (
        "Recall and complaint counts from NHTSA's free public API. Counts are not a "
        "reliability rating: popular models collect more complaints regardless of build "
        "quality, and NHTSA publishes no sales figures to correct for it. "
        "Source: https://www.nhtsa.gov/nhtsa-datasets-and-apis")
    json.dump(payload, open(MODELS, "w"), indent=2)
    print(f"\nSaved. {done} updated, {failed} with no match.")
    if failed:
        print("For the failures, open admin.html, set the NHTSA model name by hand, and run again.")


if __name__ == "__main__":
    main()
