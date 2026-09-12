# WattCost

A calculator site for EV and home energy costs. Plain HTML and JavaScript, no server
needed. All figures come from published U.S. government data.

## Files

```
index.html                  Charging cost calculator (the home page)
how-we-calculate.html       Formula, sources, and what the estimate leaves out
about.html                  Who runs the site and how it makes money
contact.html                Contact details
privacy.html                Privacy policy
terms.html                  Terms of use
affiliate-disclosure.html   How affiliate links work here
404.html                    Shown when a page isn't found
assets/site.css             All styling for every page
assets/favicon.svg          Browser tab icon
data/rates.json             Electricity price, all 50 states + DC (EIA)
data/evs.json               Every EV the EPA has rated: 1,572 trims, 1998-2027
data/evs-extra.json         Cars EPA hasn't published yet (empty right now)
data/gas.json               Gas prices (EIA)
tools/build_evs_from_epa.py Turns EPA's download into data/evs.json
robots.txt                  Tells search engines they may index the site
sitemap.xml                 List of pages for search engines
```

Keep this structure. All links are relative, so the site works in a GitHub project
folder (yourname.github.io/wattcost/), at a domain root, or on a custom domain.

## BEFORE YOU PUBLISH

Search every file for `[FILL IN]` and replace it. Those spots need YOUR information:
your name, your email, your host, your dates. Nothing with `[FILL IN]` still in it
should go live.

Also do these:

1. **robots.txt and sitemap.xml**: replace `REPLACE-WITH-YOUR-DOMAIN.com` with your domain.
2. **index.html**: the home charger section is a placeholder with fake prices.
   Delete that whole `<section class="block">` until you have real products and real
   affiliate links. Never publish invented prices.
3. **privacy.html and terms.html**: these are starting templates, not legal advice.
   Read them line by line and make them true for your site.
4. **Write a few real articles** before applying to AdSense. Calculators alone are thin.
   Your own charging data is the content nobody else can copy.

## Preview on your computer

Double-clicking `index.html` shows a yellow "data didn't load" box. That's normal:
browsers won't let a page opened from your computer read other files. Instead:

1. Open Terminal in this folder.
2. Run: `python3 -m http.server --bind 127.0.0.1`
3. Visit `http://127.0.0.1:8000`

Press Control + C to stop the server when you're done.



## Publish on GitHub Pages

1. Make a new repository (for example `wattcost`) and upload the CONTENTS of this
   folder, not the folder itself. `index.html` must sit at the top level of the repo.
2. Settings -> Pages -> Source: "Deploy from a branch", branch `main`, folder `/ (root)`.
3. Your site appears at https://yourusername.github.io/wattcost/
4. Later, add a custom domain under Settings -> Pages -> Custom domain.

Success: your domain loads the calculator, and the car and state menus fill in.

## Monthly update (about 15 minutes)

EIA publishes new state electricity prices near the end of each month.

1. **Electricity rates.** Ask AI to pull the latest EIA Table 5.6.A residential rates
   into `data/rates.json`, keeping the format. Update `data_month` and `updated`.
2. **Gas prices.** Same from the EIA Gasoline and Diesel Fuel Update into `data/gas.json`.
3. **EVs.** Download `vehicles.csv.zip` from fueleconomy.gov, unzip `vehicles.csv` into
   `tools/`, then run `python3 tools/build_evs_from_epa.py`.
   If it prints a WARNING about a car in evs-extra.json, EPA has published that car:
   delete it from evs-extra.json and run again. Delete `tools/vehicles.csv` afterward
   (21 MB, and your website doesn't need it).
4. **Spot-check.** Compare 2 or 3 numbers against the official sites yourself.
   This step is what makes the site trustworthy. Don't skip it.
5. **Publish.** Commit and push.

Success: the "Where these numbers come from" box on the home page shows the new dates.
