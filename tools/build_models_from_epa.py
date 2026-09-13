"""
Build data/models.json (the EV finder's shopping list) from EPA's vehicles.csv.

WHAT THIS DOES
  Groups current model-year EVs by make + model (not every trim), and fills in the
  facts EPA publishes: range, efficiency, body type, drive options, AC charge time.

WHAT IT CANNOT DO
  EPA publishes no price, no DC fast-charging speed, no reliability rating, and
  nothing about whether a car has physical buttons. Those four fields are created
  as null and YOU fill them in by hand from the manufacturer's spec page.
  The finder only ranks cars whose fields are filled, so a blank never becomes a
  guess shown to a reader.

HOW TO USE
  1. Put EPA's vehicles.csv in this tools/ folder (see build_evs_from_epa.py).
  2. From the site folder, run:  python3 tools/build_models_from_epa.py
  3. Open data/models.json and fill in the null fields. Keep any you already filled:
     the script merges your existing file rather than overwriting your work.
"""
import csv, json, os, sys
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
CSV_PATH = os.path.join(HERE, "vehicles.csv")
OUT_PATH = os.path.join(SITE, "data", "models.json")
MIN_YEAR = date.today().year          # current model year and newer

BODY = {
    "Two Seaters": "Sports car", "Minicompact Cars": "Small car", "Subcompact Cars": "Small car",
    "Compact Cars": "Small car", "Midsize Cars": "Sedan", "Large Cars": "Sedan",
    "Small Station Wagons": "Wagon", "Midsize Station Wagons": "Wagon",
    "Small Sport Utility Vehicle 2WD": "Small SUV", "Small Sport Utility Vehicle 4WD": "Small SUV",
    "Standard Sport Utility Vehicle 2WD": "Large SUV", "Standard Sport Utility Vehicle 4WD": "Large SUV",
    "Standard Pickup Trucks 2WD": "Pickup", "Standard Pickup Trucks 4WD": "Pickup",
    "Small Pickup Trucks 2WD": "Pickup", "Small Pickup Trucks 4WD": "Pickup",
}
DRIVE = {
    "Front-Wheel Drive": "FWD", "Rear-Wheel Drive": "RWD", "All-Wheel Drive": "AWD",
    "4-Wheel Drive": "AWD", "Part-time 4-Wheel Drive": "AWD", "4-Wheel or All-Wheel Drive": "AWD",
}
MANUAL_FIELDS = {
    "starting_price_usd": None,      # manufacturer's starting MSRP, excluding destination
    "dc_peak_kw": None,              # manufacturer's peak DC fast-charging speed
    "dc_10_80_minutes": None,        # manufacturer's 10-80% fast-charge time, if published
    "controls": None,                # "buttons", "mixed", or "touchscreen"
    "controls_note": None,           # what you saw, e.g. "physical climate knobs, volume knob"
    "seats": None,                   # number of seats
    "cargo_cu_ft": None,             # cargo behind the rear seats
    "tow_rating_lbs": None,          # 0 if the maker says it can't tow
    "port": None,                    # "NACS" or "CCS"
    "heat_pump": None,               # true/false: matters a lot in cold winters
    "reliability_score": None,       # 1 (poor) to 5 (excellent), YOUR rating after reading the sources
    "reliability_source": None,      # what you based it on, e.g. "Consumer Reports Feb 2026 + 3 NHTSA recalls"
    "reliability_url": None,         # link readers can follow
    "source_url": None,              # the manufacturer page the specs came from
    "checked": None,                 # date you last verified it, e.g. "2026-09-12"
}

def num(v):
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (TypeError, ValueError):
        return None

if not os.path.exists(CSV_PATH):
    sys.exit(f"Can't find {CSV_PATH}\nDownload and unzip EPA's vehicles.csv into the tools/ folder first.")

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

needed = {"year", "make", "model", "fuelType1", "combE", "range", "VClass", "drive", "charge240"}
missing = needed - set(rows[0].keys())
if missing:
    sys.exit(f"EPA's file is missing expected columns: {sorted(missing)}. Nothing was written.")

groups = defaultdict(list)
for r in rows:
    y = num(r["year"])
    if r["fuelType1"] != "Electricity" or not y or y < MIN_YEAR:
        continue
    if not num(r["combE"]):
        continue
    groups[(y, r["make"].strip(), r["model"].split("(")[0].strip())].append(r)

models, unmapped = [], set()
for (y, make, model), rs in groups.items():
    ranges = [num(r["range"]) for r in rs if num(r["range"])]
    effs = [num(r["combE"]) for r in rs if num(r["combE"])]
    bodies, drives = set(), set()
    for r in rs:
        b = BODY.get(r["VClass"])
        if b: bodies.add(b)
        else: unmapped.add(r["VClass"])
        d = DRIVE.get(r["drive"])
        if d: drives.add(d)
    charge = [num(r["charge240"]) for r in rs if num(r["charge240"])]
    item = {
        "id": f"{y}-{make}-{model}".lower().replace(" ", "-").replace("/", "-"),
        "year": y, "make": make, "model": model, "trims": len(rs),
        "range_min_mi": min(ranges) if ranges else None,
        "range_max_mi": max(ranges) if ranges else None,
        "kwh_per_100mi_best": min(effs) if effs else None,
        "body": sorted(bodies), "drive": sorted(drives),
        "ac_charge_hours_240v": min(charge) if charge else None,
        "epa_source": "EPA fueleconomy.gov vehicles.csv",
    }
    item.update(MANUAL_FIELDS)
    models.append(item)

# keep any manual values already filled in
if os.path.exists(OUT_PATH):
    old = {m["id"]: m for m in json.load(open(OUT_PATH)).get("models", [])}
    kept = 0
    for m in models:
        prev = old.get(m["id"])
        if not prev:
            continue
        for f in MANUAL_FIELDS:
            if prev.get(f) is not None:
                m[f] = prev[f]; kept += 1
    print(f"Kept {kept} manually entered values from the existing file.")

models.sort(key=lambda m: (m["make"].lower(), m["model"].lower()))
json.dump({
    "updated": date.today().isoformat(),
    "model_years": f"{MIN_YEAR} and newer",
    "epa_source_url": "https://www.fueleconomy.gov/feg/ws/",
    "manual_fields": list(MANUAL_FIELDS),
    "manual_note": "EPA publishes no price, DC charging speed, control layout or reliability rating. Fill these in from the manufacturer's own spec page and record the URL and date. The finder skips any model with missing fields rather than guessing.",
    "models": models,
}, open(OUT_PATH, "w"), indent=2)

REQUIRED = ["starting_price_usd", "dc_peak_kw", "controls", "seats", "reliability_score"]  # a car missing these still appears, but scores neutral on them
complete = sum(1 for m in models if all(m[f] is not None for f in REQUIRED))
print(f"Wrote {len(models)} models to data/models.json")
print(f"  {complete} have every hand-checked field filled in")
print(f"  {len(models) - complete} are missing at least one of: {', '.join(REQUIRED)}")
print("  (Models still appear in the finder; blank fields are shown as 'not checked yet' and score neutral.)")
if unmapped:
    print(f"  NOTE: unmapped EPA body classes (add them to BODY in this script): {sorted(unmapped)}")
