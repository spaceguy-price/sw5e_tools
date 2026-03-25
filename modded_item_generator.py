# Modded item generator

#Author Andrew Price (github: spaceguy-price)
#26.02.2026

import json
import math
import numpy as np
import pandas as pd

class Item:
    def __init__(self, name, itype, stat, price):
        self.name = name
        self.itype = itype
        self.stat = stat
        self.rarity = int
        self.attunement = True
        self.nmods = int
        self.mods = None
        self.mods_description = None
        self.naugments = int
        self.augments = None
        self.augments_description = None
        self.price = price

    def __str__(self):
        return f"{self.name} ({self.itype}) - Rarity: {self.rarity}, Attunement: {self.attunement}, Mods: {self.nmods}, Augments: {self.naugments}"
    
    def __simplejson__(self):
        return {
            "name": self.name,
            "stat": self.stat,
            "mods": self.mods,
            "augment_descriptions": self.augments_description,
            "price": self.price
        }
    
    def __detailedjson__(self):
        return {
            "name": self.name,
            "type": self.itype,
            "stat": self.stat,
            "rarity": self.rarity,
            "attunement": self.attunement,
            "nmods": self.nmods,
            "mods": self.mods,
            "mod_descriptions": self.mods_description,
            "naugments": self.naugments,
            "augments": self.augments,
            "augment_descriptions": self.augments_description,
            "price": self.price
        }
    
    def __stype__(self):
        # Simplified type (e.g., "Simple Blaster" -> "Blaster")
        x = self.itype.split()
        return x[-1]

def roll_item(rng, items):
    #Roll a random item with the type based on a predefined weighting of item types.
    #Inputs:
    #rng: random number generator to use for reproducibility
    #items: dictionary of items to draw from
    #Returns:
    #itype: the rolled item type

    itypes = ["Simple Blaster", "Martial Blaster", "Simple Vibroweapon", "Martial Vibroweapon", "Simple Lightweapon", "Martial Lightweapon", "Light Armor", "Medium Armor", "Heavy Armor", "Shield", "Clothing"]
    weights = np.array([5, 3, 5, 3, 1, 0, 3, 3, 3, 2, 5]) #Weights for the item types; these can be adjusted to increase or decrease the likelihood of certain item types being rolled

    itype = rng.choice(itypes, p=weights/weights.sum(), replace=True)
    eligible_items = [item for item in items if items[item]["Type"] == itype]
    item_name = rng.choice(eligible_items, replace=True)
    item_stat = items[item_name]["Stat"]
    item_cost = items[item_name]["Cost"]
    item = Item(str(item_name), str(itype), str(item_stat), int(item_cost.replace('cr','').replace(',','')))

    return item

def roll_rarity(rng, item):
    #Roll a random item rarity based on a predefined weighting of item rarities.
    #Inputs:
    #rng: random number generator to use for reproducibility
    #Returns:
    #item: the item with the rarity applied

    rarities = ["Standard", "Premium", "Prototype", "Advanced", "Legendary", "Artifact"]
    rarities = list(range(len(rarities))) #Convert rarities to integers for easier handling; the mapping of integers to rarities is based on the order of the rarities in the list
    weights = np.array([20, 8, 1, 0, 0, 0]) #Weights for the item rarities; these can be adjusted to increase or decrease the likelihood of certain item rarities being rolled

    item.rarity = int(rng.choice(rarities, p=weights/weights.sum(), replace=True))

    if item.rarity >= 1:
        if item.itype != "Clothing":
            item.name = f"{item.name} +{item.rarity}"

    return item

def roll_mods(rng, item, mods):
    #Roll random mods to apply to an item based on the item's type and rarity.
    #Inputs:
    #rng: random number generator to use for reproducibility
    #item: the item to roll mods for
    #mods: dictionary of mods to apply to the items
    #Returns:
    #item: item with the rolled mods applied

    if item.itype in ["Shield"]:
        item.nmods = 0 #Unfortunately, the shield mods are grouped under armor at https://sw5e.com/loot/enhancedItems, and thus more complex means of extracting shield mods will be required.
    else:
        max_mods = math.ceil((item.rarity+1)/2)+3 #Max mods is based on the item rarity
        item.nmods = int(rng.integers(1, max_mods+1)) #Roll the number of mods to apply to the item; always at least 1 mod, and the calculation is +1 above sw5e wretched hives to increase the number of mods applied to higher rarity items
    max_augments = math.ceil((item.rarity+1)/2) #Max augments is based on the item rarity; this is a more generous calculation than sw5e raw
    pool = list(range(0, max_augments+1))
    pool.append(0)
    pool.append(0)
    item.naugments = int(rng.choice(pool)) #Number of augments

    eligible_mods = []
    eligible_augments = []
    rarities = ["Standard", "Premium", "Prototype", "Advanced", "Legendary", "Artifact"]
    for mod in mods:
        if mods[mod]["subtype"] == item.__stype__():
            for i, rarity in enumerate(rarities):
                if mods[mod]["rarity"] == rarity and i <= item.rarity:
                    eligible_mods.append(mod)
                    break
        elif mods[mod]["subtype"] == "Augment":
            for i, rarity in enumerate(rarities):
                if mods[mod]["rarity"] == rarity and i <= item.rarity:
                    eligible_augments.append(mod)
                    break

    mod_rarities = []
    item.mods = rng.choice(eligible_mods, size=item.nmods, replace=False).tolist() #Roll the mods to apply to the item; no duplicates
    if item.nmods > 0:
        item.mods_description = [mods[mod]["description"] for mod in item.mods]
        mod_rarities = [mods[mod]["rarity"] for mod in item.mods] 
    item.augments = rng.choice(eligible_augments, size=item.naugments, replace=False).tolist() #Roll the augments to apply to the item; no duplicates
    modified_descriptions = []

    # Basic stat augments increase 1 and lower a random other attribute; this code randomizes the other attribute
    if item.naugments > 0:
        for augment in item.augments:
            if "(chosen by the GM)" in mods[augment]["description"]:
                attributes = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
                for i, attribute in enumerate(attributes):
                    if mods[augment]["description"].find(attribute) != -1:
                        attributes.remove(attribute)
                        lowered_attribute = rng.choice(attributes)
                        mods[augment]["description"] = f"Your {attribute} increases by 1, your {lowered_attribute} decreases by 1."
            modified_descriptions.append(mods[augment]["description"])

    item.augments_description = modified_descriptions

    return item, mod_rarities

def calculate_price(rng, item, mod_rarities, global_price_multiplier=1):
    #Calculate the price of the item based on its rarity, number of mods, and number of augments
    #Inputs:
    #rng: random number generator to use for reproducibility
    #item: the item to calculate the price for
    #mod_rarities: the rarities of the mods applied to the item
    #global_price_multiplier: a multiplier to apply to the final price of the item; this can be used to adjust the overall price level of the generated items
    #Returns:
    #price: the calculated price of the item

    rarities = ["Standard", "Premium", "Prototype", "Advanced", "Legendary", "Artifact"]
    price_modifiers = [10,50,250,1000,5000,25000] #https://sw5e.com/rules/wh/enhancedItems

    num_mods = item.nmods #+ item.naugments #TODO include number of augments in the price calculation
    
    #Start with base price and bump it to its rarity tier
    if item.rarity != 0:
        price = item.price + 100*price_modifiers[item.rarity-1]
    else:
        price = item.price

    # Add mod prices
    if num_mods > 0:
        for mod_rarity in mod_rarities:
            for i, rarity in enumerate(rarities):
                if mod_rarity == rarity:
                    price += max(rng.integers(1,100),rng.integers(1,100))*price_modifiers[i]/2 #Mods cost half price
                break
    
    item.price = int(price*global_price_multiplier)

    return item

def generate(number_items, items, mods, global_price_multiplier=1):
    #Inputs:
    #number_items: number of items to generate
    #items: dictionary of items to draw from
    #mods: dictionary of mods to apply to the items
    #global_price_multiplier: a multiplier to apply to the final price of the item; this can be used to adjust the overall price level of the generated items
    #Outputs:
    #generated_items: dictionary of generated items with mods applied

    generated_items = []

    for i in range(number_items):
        rng = np.random.default_rng(seed=None)
        item = roll_item(rng, items)
        item = roll_rarity(rng, item)
        item, mod_rarities = roll_mods(rng, item, mods)
        item = calculate_price(rng, item, mod_rarities, global_price_multiplier=global_price_multiplier)
        generated_items.append(item)

    return generated_items

if __name__ == "__main__":
    #-----Inputs-----
    number_items = 15 #Number of items to gernate
    global_price_multiplier = 0.75 #A multiplier to apply to the final price of the item; this can be used to adjust the overall price level of the generated items; 1 is RAW pricing
    item_file = "sw5e_items.json" #File to save the generated items to
    mods_file = "sw5e_mods.json" #File to read the mods from
    save_file_prefix = "generated_items/" #Path and prefix for where to save the outputs to
    #----------------

    #Generate the items
    items = json.load(open(item_file, "r")) #Load the scraped items
    mods = json.load(open(mods_file, "r")) #Load the mods
    generated_items = generate(number_items, items, mods,global_price_multiplier=global_price_multiplier)
    print(f"Generated {len(generated_items)} items.")

    simplejson = []
    detailedjson = []
    for item in generated_items:
        simplejson.append(item.__simplejson__())
        detailedjson.append(item.__detailedjson__())

    with open(save_file_prefix+"simple.json", "w", encoding="utf8") as f:
        json.dump(simplejson, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(generated_items)} items to {save_file_prefix+'simple.json'}")
    with open(save_file_prefix+"detailed.json", "w", encoding="utf8") as f:
        json.dump(detailedjson, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(generated_items)} items to {save_file_prefix+'detailed.json'}")
    df = pd.json_normalize(simplejson)
    df.to_excel(save_file_prefix+"simple.xlsx", index=False)

    print("Done.")