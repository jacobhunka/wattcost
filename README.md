# Volt & Ledger

Calculators for what an EV really costs, in dollars and in carbon. Plain HTML and
JavaScript, no server needed. Every figure comes from a published source.

## Files

```
index.html                  Charging cost calculator (the home page)
finder.html                 EV finder: weighted match for first-time buyers
carbon.html                 Carbon payback calculator
how-we-calculate.html       Formulas, sources, and what each estimate leaves out
about.html                  Who runs the site and how it makes money
contact.html                Contact details
privacy.html                Privacy policy
terms.html                  Terms of use
affiliate-disclosure.html   How affiliate links work here
404.html                    Shown when a page isn't found
assets/site.css             All styling for every page
assets/favicon.svg          Browser tab icon
data/rates.json             Electricity price, all 50 states + DC (EIA, June 2026)
data/gas.json               Gas prices (EIA, week of Sep 7, 2026)
data/evs.json               Every EV the EPA has rated: 1,572 trims, 1998-2027
data/evs-extra.json         Cars EPA hasn't published yet (empty right now)
data/models.json            EV finder's shopping list: EPA facts filled in
                            automatically, the rest filled in BY YOU (see below)
data/guidance.json          Winter range loss (AAA + Recurrent), incentive status,
                            home-charging guidance, all with sources
data/carbon.json            Grid emissions by state (EPA eGRID2023), IPCC source
                            factors, ICCT battery factors, EPA gasoline and tree factors
tools/build_evs_from_epa.py Turns EPA's download into data/evs.json
tools/build_models_from_epa.py  Turns EPA's download into data/models.json
tools/fetch_nhtsa.py        Fills recall and complaint counts from NHTSA's free API
admin.html                  Local-only editor for filling in model data (not for readers)
robots.txt                  Tells search engines they may index the site
sitemap.xml                 List of pages for search engines
```

Keep this structure. All links are relative, so the site works at
yourusername.github.io/wattcost/, at a domain root, or on a custom domain.

## BEFORE YOU PUBLISH

Search every file for `[FILL IN]` and replace it. Those spots need YOUR information:
your name, your email, your host, your dates.

Also:

1. **robots.txt and sitemap.xml**: replace `REPLACE-WITH-YOUR-DOMAIN.com` with your domain.
2. **index.html**: the home charger section is a placeholder with fake prices.
   Delete that whole `<section class="block">` until you have real products and real
   affiliate links. Never publish invented prices.
3. **privacy.html and terms.html** are starting templates, not legal advice. Read them
   line by line and make them true for your site.
4. **The name.** "Volt & Ledger" passed only a quick search. Check it at
   tmsearch.uspto.gov and check the domain before buying anything with the name on it.
5. **Write real articles** before applying to AdSense. Calculators plus policy pages
   is a thin site on its own.
6. **Check data/guidance.json once a year.** It holds the federal incentive status
   (currently: expired) and the winter range figures. Tax rules change; the file records
   what was checked and when.

## Filling in the EV finder (data/models.json)

EPA publishes range, efficiency, body style and drive type, and the build script fills
those in for all 331 current models automatically. EPA publishes NO price, NO DC
fast-charging speed, NO seat count, and nothing about physical buttons. Those are on you.

The finder works anyway: a car with blank fields still appears, ranked on its EPA data,
but shows "not checked yet" in amber and scores neutral on whatever is missing. Filters
never exclude a car for a value you haven't entered. So nothing is guessed, and nothing
is silently hidden either. Every model you fill in makes the results sharper.

For each car you want to appear, open data/models.json and fill in:

```
"starting_price_usd": 35000,        from the manufacturer's own build-and-price page
"dc_peak_kw": 150,                  manufacturer's peak DC fast-charging speed
"dc_10_80_minutes": 43,             if the manufacturer publishes it, else leave null
"controls": "mixed",                "buttons", "mixed", or "touchscreen"
"controls_note": "climate knobs, volume knob, rest on screen",
"seats": 5,
"cargo_cu_ft": 26.4,                behind the rear seats
"tow_rating_lbs": 1500,             0 if the maker says it can't tow
"heat_pump": true,                  matters a lot in cold climates
"port": "NACS",                     or "CCS"
"reliability_score": 4,             1 to 5, YOUR call after reading the sources
"reliability_source": "Consumer Reports Feb 2026 predicted reliability + 2 NHTSA recalls",
"reliability_url": "https://www.nhtsa.gov/recalls",
"source_url": "https://www.chevrolet.com/electric/equinox-ev",
"checked": "2026-09-12"
```

Rules that keep this defensible:

- **Use the manufacturer's page for specs.** One search for a single car's starting
  price returned three different numbers from three sites. Go to the source.
- **Don't copy Consumer Reports or J.D. Power ratings into the file.** Those ratings are
  their property. Read them, form your own 1-to-5 view, and write what it's based on in
  `reliability_source` with a link. Free federal complaint and recall records are at
  https://www.nhtsa.gov/recalls
- **Record the date.** Prices change; `checked` tells readers how stale a figure is.
- **Start with 10 to 15 popular models.** That's enough for the finder to give real
  answers, and it's a couple of hours of work rather than a month.

Re-running `python3 tools/build_models_from_epa.py` keeps everything you've typed and
only refreshes the EPA fields.

### The easy way: admin.html

Don't hand-edit the JSON. Use the editor instead:

1. Start the local server: `python3 -m http.server --bind 127.0.0.1`
2. Open `http://127.0.0.1:8000/admin.html`
3. Search for a car, click it, type what the manufacturer's spec page says.
4. Click **Download models.json** and replace `data/models.json` with the file.
5. Commit and push.

The editor never uploads anything. A coloured dot shows each car's state: grey for
not started, amber for partly done, green for complete. The counter at the top right
tracks your progress, and the "Show" menu filters to what still needs work.

`admin.html` ships with the site but is excluded in robots.txt and left out of the
sitemap. If you'd rather it never reach the server at all, delete it before pushing
and keep a local copy.

### Recall and complaint counts

Run `python3 tools/fetch_nhtsa.py` to pull recall and complaint counts from NHTSA's
free public API (no key needed). Useful flags:

```
python3 tools/fetch_nhtsa.py --make Hyundai     # one make
python3 tools/fetch_nhtsa.py --limit 20         # first 20 unchecked models
python3 tools/fetch_nhtsa.py --refresh          # re-check ones already done
```

The counts then appear in admin.html beside the reliability field, with links to the
NHTSA pages. The script deliberately does NOT set reliability_score: counts are not a
rating, because a car that sold 200,000 units collects more complaints than one that
sold 5,000 however well it was built. Read the counts, read the recall summaries, then
set the 1-to-5 score yourself and write down what it was based on.

If a lookup finds nothing, EPA and NHTSA probably spell the model differently. Set the
"NHTSA model name" field in admin.html for that car and run the script again.

## Preview on your computer

Double-clicking `index.html` shows a yellow "data didn't load" box. That's normal.
Instead:

1. Open Terminal in this folder.
2. Run: `python3 -m http.server --bind 127.0.0.1`
3. Visit `http://127.0.0.1:8000`

Press Control + C to stop the server when you're done.

## Publish with GitHub Desktop

1. Copy the CONTENTS of this folder (not the folder itself) into your `wattcost` repo
   folder, replacing the old files. `index.html` must sit at the top level.
2. In GitHub Desktop, type a summary, click Commit to main, then Push origin.
3. The live site updates in about a minute at https://jacobhunka.github.io/wattcost/

## Monthly update (about 15 minutes)

1. **Electricity rates.** Ask AI to pull the latest EIA Table 5.6.A residential rates
   into `data/rates.json`, keeping the format. Update `data_month` and `updated`.
2. **Gas prices.** Same from the EIA Gasoline and Diesel Fuel Update into `data/gas.json`.
3. **EVs.** Download `vehicles.csv.zip` from fueleconomy.gov, unzip `vehicles.csv` into
   `tools/`, run `python3 tools/build_evs_from_epa.py` AND
   `python3 tools/build_models_from_epa.py`, then delete `tools/vehicles.csv`.
   Re-check a few prices in models.json while you're there; prices go stale fastest.
4. **Spot-check** 2 or 3 numbers against the official sites yourself. Don't skip this.
5. **Commit and push.**

## Yearly update

`data/models.json            EV finder's shopping list: EPA facts filled in
                            automatically, the rest filled in BY YOU (see below)
data/guidance.json          Winter range loss (AAA + Recurrent), incentive status,
                            home-charging guidance, all with sources
data/carbon.json` changes rarely. EPA releases a new eGRID about once a year
(check https://www.epa.gov/egrid/summary-data). When it arrives, update the state
CO2e column and the grid-loss figure, and change `updated`. The IPCC and ICCT factors
only change if those studies are revised.
