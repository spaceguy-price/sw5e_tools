# SW5E Command Line Tools
Author: spaceguy-price
26.03.2026

This repo contains the script I used to scrape the sw5e.com website for item and mod descriptions, 
as well as a simple item generator script to generate already modded items.
Ensure that you have the necessary python libraries installed, update the paths in modd_item_generator.py, then simply run
```bash
python modded_item_generator.py
```
in your command line. Additionally I include the sw5e_item_scraper.py script I wrote to download item and mod descriptions
from sw5e. I don't include usage instructions here, but feel free to adapt and use it as well.

## Python libraries
- json (format used for saving 
- numpy (standard linear algebra)
- pandas (dataframe library)
- openpyxl (format used to export data to an excel file)

## modded_item_generator.py logic
- The mod file and item file are loaded
- A random item is rolled (low chance for lightweapons)
- A random rarity is assigned (currently weighted to 0/+1 with a tiny chance for +2)
- Random mods are rolled and installed
- The price is calculated (base price + 1d100*rarity_modifier/mod)*global_price_multiplier
- Modded items are saved to simple.json, detailed.json and simple.xlsx

## Known Bugs
- *Shields do not roll mods.*
Unfortunately, the sw5e.com website grouped shield mods and armor mods with the same identifier "armor".
To properly identify shield mods will require parsing the mod descriptions.
- *Augment description error.*
Augment descriptions keep defaulting to wisdom in detail.json. Simple descriptions appear to be fine.

## TODO
- Improve shield mod parsing
- Fix augment descriptions
- Implement argparse for command line inputs (no need to modify python files)
- Allow user selection of item and mod rarity weighting
