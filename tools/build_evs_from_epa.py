"""
Build data/evs.json from EPA's official vehicle download.

HOW TO USE (about 2 minutes, once a month):
  1. In your browser, download https://www.fueleconomy.gov/feg/epadata/vehicles.csv.zip
  2. Unzip it. Put vehicles.csv in this tools/ folder.
  3. In Terminal, from the wattcost-calculator folder, run:
         python3 tools/build_evs_from_epa.py
  4. Read the summary it prints. Spot-check 2 or 3 cars on fueleconomy.gov.

Keeps every battery-electric vehicle EPA has rated (fuelType1 = "Electricity"),
all model years. Merges in data/evs-extra.json for cars EPA hasn't published yet.
"""
import csv, json, os, sys
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
CSV_PATH = os.path.join(HERE, "vehicles.csv")
EXTRA_PATH = os.path.join(SITE, "data", "evs-extra.json")
OUT_PATH = os.path.join(SITE, "data", "evs.json")
MIN_YEAR = 0   # 0 = keep every model year. Set to e.g. 2020 to drop older cars.

def num(value):
    try:
        n = float(value)
        return int(n) if n.is_integer() else n
    except (TypeError, ValueError):
        return None

if not os.path.exists(CSV_PATH):
    sys.exit(f"Can't find {CSV_PATH}\nDownload and unzip EPA's vehicles.csv into the tools/ folder first.")

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

needed = {"id", "year", "make", "model", "fuelType1", "combE", "comb08", "range", "evMotor"}
missing = needed - set(rows[0].keys())
if missing:
    sys.exit(f"EPA's file is missing expected columns: {sorted(missing)}. The format may have changed; nothing was written.")

vehicles, skipped_no_rating = [], 0
for r in rows:
    year = num(r["year"])
    if r["fuelType1"] != "Electricity" or not year or year < MIN_YEAR:
        continue
    kwh = num(r["combE"])
    if not kwh or kwh <= 0:
        skipped_no_rating += 1
        continue
    vehicles.append({
        "id": f"epa-{r['id']}",
        "year": year, "make": r["make"].strip(), "model": r["model"].strip(),
        "kwh_per_100mi": round(float(kwh), 1),          # EPA's precise value; the page rounds for display
        "mpge": num(r["comb08"]), "range_mi": num(r["range"]) or None,
        "epa_id": num(r["id"]), "motor": r["evMotor"].strip() or None,
    })

if not vehicles:
    sys.exit("Found 0 electric vehicles. The file or its format may be wrong; nothing was written.")

# EPA sometimes lists two versions under the exact same name. Keep both and label them apart.
groups = defaultdict(list)
for v in vehicles:
    groups[(v["year"], v["make"], v["model"])].append(v)
renamed = 0
for key, vs in groups.items():
    if len(vs) < 2:
        continue
    ranges = [v["range_mi"] for v in vs]
    use_range = len(set(ranges)) == len(ranges) and None not in ranges
    for v in vs:
        v["model"] += f" ({v['range_mi']} mi range)" if use_range else f" ({v['motor'] or 'EPA #' + str(v['epa_id'])})"
        renamed += 1

for v in vehicles:
    v.pop("motor")
    v["source"] = "EPA"

seen = {(v["year"], v["make"], v["model"].split(" (")[0]) for v in vehicles} | {(v["year"], v["make"], v["model"]) for v in vehicles}
added_extras = 0
if os.path.exists(EXTRA_PATH):
    for x in json.load(open(EXTRA_PATH)).get("vehicles", []):
        if (x["year"], x["make"], x["model"]) in seen:
            print(f"  NOTE: EPA now lists {x['year']} {x['make']} {x['model']}. Remove it from evs-extra.json.")
            continue
        first_word = x["model"].split()[0]
        close = [v["model"] for v in vehicles if v.get("source") == "EPA" and v["year"] == x["year"]
                 and v["make"] == x["make"] and v["model"].split()[0] == first_word]
        if close:
            print(f"  WARNING: {x['year']} {x['make']} {x['model']} (from evs-extra.json) may now be in EPA's file as: {', '.join(close)}")
            print(f"           If so, remove it from evs-extra.json so it isn't listed twice.")
        vehicles.append(x); added_extras += 1

vehicles.sort(key=lambda v: (-v["year"], v["make"].lower(), v["model"].lower()))
payload = {
    "updated": date.today().isoformat(),
    "unit": "kWh per 100 miles, EPA combined city/highway (measured at the wall, so charging losses are included)",
    "source": "U.S. EPA / DOE fueleconomy.gov",
    "source_url": "https://www.fueleconomy.gov/feg/ws/",
    "vehicles": vehicles,
}
with open(OUT_PATH, "w") as f:
    json.dump(payload, f, separators=(",", ":"))   # compact = faster page load

years = sorted({v["year"] for v in vehicles})
print(f"Wrote {len(vehicles)} vehicles to data/evs.json ({os.path.getsize(OUT_PATH)//1024} KB)")
print(f"  {len(vehicles) - added_extras} from EPA, {added_extras} from evs-extra.json")
print(f"  Model years {years[0]} to {years[-1]}, {len({v['make'] for v in vehicles})} makes")
if renamed:
    print(f"  {renamed} same-name EPA listings labeled apart (e.g. by range)")
if skipped_no_rating:
    print(f"  Skipped {skipped_no_rating} EVs with no efficiency rating")
print("Next: spot-check 2 or 3 of these on fueleconomy.gov:")
for v in vehicles[:: max(1, len(vehicles) // 3)][:3]:
    print(f"  {v['year']} {v['make']} {v['model']}: {v['kwh_per_100mi']} kWh/100 mi")
