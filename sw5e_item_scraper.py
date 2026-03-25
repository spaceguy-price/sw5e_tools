#Author: Andrew Price (github: spaceguy-price)
#25.02.2026

# Requires python, json package and playwright package
# To install playright, in your terminal:
# pip install playwright

import json
from playwright.sync_api import sync_playwright

def scrape(URL):

    # Dictionary to hold the item data
    items = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False) #Launching with a head allows us to set filters using the sw5e.com GUI
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_selector("table")
        print("Webpage opened.")
        print("\n Set your filters and row count in the opened browser.")
        input("When you are ready, press ENTER here to start scraping.")

        # Count all the items and click them to open descriptions rows (td)
        tr_rows = page.locator("table tbody tr")
        tr_count = tr_rows.count()
        print("Total clickable rows:", tr_count)
        for i in range(tr_count):
            row = tr_rows.nth(i)
            row.click()

        # Count all descriptions and confirm there are sufficient descriptions for each item
        # This code assumes every row is clickable or not clickable, if it is heterogenous a more complex scraper is needed
        td_rows = page.locator("table tbody td.pt-3")
        td_count = td_rows.count()
        print("Description rows:", td_count)
        if tr_count != td_count and td_count != 0:
            raise Exception(f"Number of description rows ({td_count}) does not match the number of items ({tr_count}). It seems that not all of the items have descriptions.")

        # Extract item data
        for i in range(tr_count):
            # Extract the relevant column information for each item
            tr_row = tr_rows.nth(i)
            cols = tr_row.locator("td")
            td_count = cols.count()

            name = cols.nth(0).inner_text().strip()
            type = cols.nth(1).inner_text().strip()
            subtype = cols.nth(2).inner_text().strip()
            rarity = cols.nth(3).inner_text().strip()
            attunement = cols.nth(5).inner_text().strip()
            print(f"Scraping {i}: {name}")

            items[name] = {
                    "type": type,
                    "subtype": subtype,
                    "rarity": rarity,
                    "attunement": attunement
                }
            
            # Extract the item description (which is in a separate row opened by row.click)
            if td_count != 0:
                td_row = td_rows.nth(i)
                text = td_row.locator("p").all_inner_texts()
                description = "\n\n".join(text)
                items[name]["description"] = description

        browser.close()

    return items

def save(items, save_loc):

    with open(save_loc, "w", encoding="utf8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(items)} items to {save_loc}")


if __name__ == "__main__":
    # Currently formatted for the enhanced item table. Other tables will have different columns and may require different page.locator() calls
    URL = "https://sw5e.com/loot/enhancedItems"
    save_loc = r"C:\Users\upekh\Andrew\Tabletop\item_generator\sw5e_enhanced_items.json"

    items = scrape(URL)
    save(items, save_loc)
    print("DONE")