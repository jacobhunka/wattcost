# Volt & Ledger

Calculators for what an EV really costs, in dollars and in carbon. Plain HTML and
JavaScript, no server needed. Every figure comes from a published source.

## Files

```
index.html                  Charging cost calculator (the home page)
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
data/carbon.json            Grid emissions by state (EPA eGRID2023), IPCC source
                            factors, ICCT battery factors, EPA gasoline and tree factors
tools/build_evs_from_epa.py Turns EPA's download into data/evs.json
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
   `tools/`, run `python3 tools/build_evs_from_epa.py`, then delete `tools/vehicles.csv`.
4. **Spot-check** 2 or 3 numbers against the official sites yourself. Don't skip this.
5. **Commit and push.**

## Yearly update

`data/carbon.json` changes rarely. EPA releases a new eGRID about once a year
(check https://www.epa.gov/egrid/summary-data). When it arrives, update the state
CO2e column and the grid-loss figure, and change `updated`. The IPCC and ICCT factors
only change if those studies are revised.
