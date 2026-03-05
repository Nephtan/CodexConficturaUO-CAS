From version 4.425.15, Autoloot entries can be imported via a CSV file with an "ID" column, an optional "Name" column, and zero or more columns starting with "Property".

![image](https://github.com/Reetus/ClassicAssist/assets/6239195/4f122443-4771-467e-abdc-e5480f96fe02)

For a template, refer to [this spreadsheet](https://docs.google.com/spreadsheets/d/1WdW6wOke8VA9EiqPdDst5SDWT4w5hw_ybB6uC-8j3SM/edit?usp=sharing).

* "ID" is the item ID for autoloot, or use "-1" to match any item. The ID can be in decimal or hexadecimal format.
* "Name" is optional and can be used to specify the name of the autoloot entry.
* Property columns follow the format "ShortNameOperatorValue". If no operator is specified, the default operator is equals (==).

For example:

* "MR2" will add "Mana Regeneration" == "2".
* "DCI>=10" will add "Defense Chance Increase" greater than or equal to (>=) "10".
* "SFRX" will add "Self Repair" not present (X).

![image](https://github.com/Reetus/ClassicAssist/assets/6239195/21659a5c-8f7c-45e9-bd6a-0d8282160281)

Operators (except X) or values for properties that don't contain arguments will have no effect.

![image](https://github.com/Reetus/ClassicAssist/assets/6239195/bec0d572-95c6-42a7-a56e-84b031237eb7)

Using the "Ignore duplicate entries" option will not import entries where a matching entry already exists in the autoloot (ID, Property, Operator and Value matches)

The list of short names for properties is as follows...

| ShortName | Name                    |
|-----------|-------------------------|
| BAL       | Balanced                |
| BRIT      | Brittle                 |
| CF        | Casting Focus           |
| CD        | Cold Damage             |
| CE        | Cold Eater              |
| CR        | Cold Resist             |
| CURSED    | Cursed                  |
| DI        | Damage Increase         |
| DCI       | Defense Chance Increase |
| DB        | Dexterity Bonus         |
| ER        | Energy Resist           |
| EP        | Enhance Potions         |
| FCR       | Faster Cast Recovery    |
| FC        | Faster Casting          |
| FD        | Fire Damage             |
| FE        | Fire Eater              |
| FR        | Fire Resist             |
| GA        | Greater Artifact        |
| HCI       | Hit Chance Increase     |
| HD        | Hit Dispel              |
| HF        | Hit Fatigue             |
| HFB       | Hit Fireball            |
| HLL       | Hit Life Leech          |
| HL        | Hit Lightning           |
| HLA       | Hit Lower Attack        |
| HLD       | Hit Lower Defense       |
| HMD       | Hit Mana Drain          |
| HML       | Hit Mana Leech          |
| HPI       | Hit Point Increase      |
| HPR       | Hit Point Regeneration  |
| HSL       | Hit Stamina Leech       |
| HUE       | Hue                     |
| ID        | ID                      |
| IB        | Intelligence Bonus      |
| KE        | Kinetic Eater           |
| LGA       | Legendary Artifact      |
| LA        | Lesser Artifact         |
| LMI       | Lesser Magic Item       |
| LMC       | Lower Mana Cost         |
| LRC       | Lower Reagent Cost      |
| LR        | Lower Requirements      |
| LUCK      | Luck                    |
| MGA       | Mage Armor              |
| MW        | Mage Weapon             |
| MA        | Major Artifact          |
| MMI       | Major Magic Item        |
| MI        | Mana Increase           |
| MP        | Mana Phase              |
| MR        | Mana Regeneration       |
| MNMI      | Minor Magic Item        |
| NS        | Night Sight             |
| PHD       | Physical Damage         |
| PR        | Physical Resist         |
| PD        | Poison Damage           |
| PE        | Poison Eater            |
| PSR       | Poison Resist           |
| PRIZED    | Prized                  |
| RP        | Reactive Paralyze       |
| RPD       | Reflect Physical Damage |
| SFR       | Self Repair             |
| SOC       | Soul Charge             |
| SC        | Spell Channeling        |
| SDI       | Spell Damage Increase   |
| SW        | Splintering Weapon      |
| SI        | Stamina Increase        |
| SR        | Stamina Regeneration    |
| SB        | Strength Bonus          |
| SSI       | Swing Speed Increase    |
| UBWS      | Use Best Weapon Skill   |
| VELOCITY  | Velocity                |
