# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Entity  
### AddFriend  
  
Method Signature:  
  
**Int32 AddFriend(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Adds a mobile to friends list, will display target cursor if no serial/alias supplied.**  
  
Example:  
  
```python  
AddFriend()  
```  
  
### Ally  
  
Method Signature:  
  
**Boolean Ally(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the mobile's notoriety is Ally**  
  
Example:  
  
```python  
if Criminal("mount"):  
```  
  
### AutoColorPick  
  
Method Signature:  
  
**Void AutoColorPick(Int32)**  
  
#### Parameters  
* hue: Item Hue or -1 for any.  
  
Description:  
  
**Setup an automated reply to the incoming dye color gump, allowing you to define dye tubs color.
That command should be added prior to the action that opens the color pick gump.**  
  
Example:  
  
```python  
AutoColorPick(666)
UseObject('dyes')
WaitForTarget(1000)
Target('tub')  
```  
  
### BuffExists  
  
Method Signature:  
  
**Boolean BuffExists(System.String)**  
  
#### Parameters  
* name: Buff name.  
  
Description:  
  
**Check for a specific buff**  
  
Example:  
  
```python  
if BuffExists("Blood Oath"):  
```  
  
### BuffTime  
  
Method Signature:  
  
**Double BuffTime(System.String)**  
  
#### Parameters  
* name: Buff name.  
  
Description:  
  
**Returns milliseconds remaining for given buff name, or 0 if expired/not enabled.**  
  
Example:  
  
```python  
if not BuffExists('Enemy Of One') or BuffTime('Enemy Of One') < 5000:
    Cast('Enemy Of One')
  
```  
  
### ClearIgnoreList  
  
Method Signature:  
  
**Void ClearIgnoreList()**  
  
Description:  
  
**Clears the ignore list.**  
  
Example:  
  
```python  
ClearIgnoreList()  
```  
  
### ClearObjectQueue  
  
Method Signature:  
  
**Void ClearObjectQueue()**  
  
Description:  
  
**Clears all actions in action packet queue**  
  
Example:  
  
```python  
ClearObjectQueue()  
```  
  
### CountType  
  
Method Signature:  
  
**Int32 CountType(Int32, System.Object, Int32)**  
  
#### Parameters  
* graphic: ItemID / Graphic such as  0x3db.  
* source: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
  
Description:  
  
**Amount comparison of item type inside a container.**  
  
Example:  
  
```python  
CountType(0xff, "backpack")  
```  
  
### CountTypeGround  
  
Method Signature:  
  
**Int32 CountTypeGround(Int32, Int32, Int32)**  
  
#### Parameters  
* graphic: ItemID / Graphic such as  0x3db.  
* hue: Item Hue or -1 for any. (Optional)  
* range: Range, ie 10. (Optional)  
  
Description:  
  
**Amount comparison of item or mobile type on the ground.**  
  
Example:  
  
```python  
if CountGround(0xff, 0, 10) < 1:  
```  
  
### Criminal  
  
Method Signature:  
  
**Boolean Criminal(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the mobile's notoriety is Criminal**  
  
Example:  
  
```python  
if Criminal("mount"):  
```  
  
### Dead  
  
Method Signature:  
  
**Boolean Dead(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns true if given mobile is dead, false if not, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
if Dead("self"):  
```  
  
### Dex  
  
Method Signature:  
  
**Int32 Dex()**  
  
Description:  
  
**Returns the dexterity of the player**  
  
Example:  
  
```python  
if Str() < 100:  
```  
  
### DiffHits  
  
Method Signature:  
  
**Int32 DiffHits(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the given mobiles difference between max and current hits, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
if DiffHits("self") > 50:  
```  
  
### DiffHitsPercent  
  
Method Signature:  
  
**Double DiffHitsPercent(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the given mobiles different between max and currents hits as a percentage, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
if DiffHitsPercent("self") > 30: # 70% health  
```  
  
### DiffWeight  
  
Method Signature:  
  
**Int32 DiffWeight()**  
  
Description:  
  
**Returns the difference between max weight and weight.**  
  
Example:  
  
```python  
if DiffWeight() > 50:  
```  
  
### Direction  
  
Method Signature:  
  
**System.String Direction(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the Direction the given alias/serial is facing**  
  
Example:  
  
```python  
if Direction('enemy') == 'West':  
```  
  
### DirectionTo  
  
Method Signature:  
  
**System.String DirectionTo(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns the Direction the entity is in relative to the player.**  
  
Example:  
  
```python  
Run(DirectionTo("enemy"))  
```  
  
### Distance  
  
Method Signature:  
  
**Int32 Distance(Int32, Int32)**  
  
#### Parameters  
* x: X Coordinate.  
* y: Y Coordinate.  
  
Description:  
  
**Returns the distance to the given coordinates.**  
  
Example:  
  
```python  
location = (1000, 1000, 0)

while Distance(location[0], location[1]) > 2:
 Pathfind(location[0], location[1], location[2])
 Pause(1000)  
```  
  
### Distance  
  
Method Signature:  
  
**Int32 Distance(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the distance to the given entity.**  
  
Example:  
  
```python  
if Distance("mount") < 4:  
```  
  
### Enemy  
  
Method Signature:  
  
**Boolean Enemy(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the mobile's notoriety is Enemy**  
  
Example:  
  
```python  
if Criminal("mount"):  
```  
  
### EquipWand  
  
Method Signature:  
  
**Boolean EquipWand(System.String, Int32)**  
  
#### Parameters  
* wandname: Wand name. See Also: [WandTypes](#WandTypes)  
* minimumcharges: Integer value - See description for usage. (Optional)  
  
Description:  
  
**Search for a wand inside your backpack and equip it**  
  
Example:  
  
```python  
#Equip a fireball wand if one can be found in our backpack..
if FindWand("fireball", "backpack", 5):
 #Remove current item in hand
 if FindLayer("OneHanded"):
  ClearHands("left")
 #Equip the wand
 EquipWand("fireball")  
```  
  
### FasterCasting  
  
Method Signature:  
  
**Double FasterCasting()**  
  
Description:  
  
**Return faster casting value.**  
  
Example:  
  
```python  
fc = FasterCasting()  
```  
  
### FasterCastRecovery  
  
Method Signature:  
  
**Double FasterCastRecovery()**  
  
Description:  
  
**Return faster cast recovery value.**  
  
Example:  
  
```python  
fcr = FasterCastRecovery()  
```  
  
### FindObject  
  
Method Signature:  
  
**Boolean FindObject(System.Object, Int32, System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* range: Range, ie 10. (Optional)  
* findlocation: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Searches for entity by serial and sets found alias, defaults to ground if no source given.**  
  
Example:  
  
```python  
# Find on ground
FindObject("mount")

# Find on ground with range
FindObject("mount", 10)

# Find in container, must specify search level or -1
FindObject("weapon", -1, "backpack")    
```  
  
### FindType  
  
Method Signature:  
  
**Boolean FindType(Int32, Int32, System.Object, Int32, Int32)**  
  
#### Parameters  
* graphic: ItemID / Graphic such as  0x3db.  
* range: Range, ie 10. (Optional)  
* findlocation: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
* minimumstackamount: Integer representing an amount, ie 10. (Optional)  
  
Description:  
  
**Searches for entity by graphic ID and sets found alias, defaults to ground if no source given.**  
  
Example:  
  
```python  
# Look for a food item from a list and eat 1 if found.
if not ListExists("food"):
 CreateList("food")
 PushList("food", 0x9b7) #bird
 PushList("food", 0x9d3) #ham
 PushList("food", 0x97d) #cheese
 PushList("food", 0x9d0) #apple
 PushList("food", 0x9eb) #muffin
 PushList("food", 0x97b) #fishsteak
 PushList("food", 0x9c0) #sausage
 PushList("food", 0x9f2) #ribs
 PushList("food", 0x9d1) #grapes
 PushList("food", 0x9d2) #peach

for i in GetList("food"):
 if FindType(i, -1, "backpack"):
  UseObject("found")
  break  
```  
  
### FindWand  
  
Method Signature:  
  
**Boolean FindWand(System.String, System.Object, Int32)**  
  
#### Parameters  
* wandname: Wand name. See Also: [WandTypes](#WandTypes)  
* containersource: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
* minimumcharges: Integer value - See description for usage. (Optional)  
  
Description:  
  
**Search for a wand and set alias "found".**  
  
Example:  
  
```python  
FindWand("fireball", "backpack", 10)  
```  
  
### Followers  
  
Method Signature:  
  
**Int32 Followers()**  
  
Description:  
  
**Returns the number of current followers as per status bar data.**  
  
Example:  
  
```python  
if Followers() < 1:  
```  
  
### Gold  
  
Method Signature:  
  
**Int32 Gold()**  
  
Description:  
  
**Returns the gold value as per status bar data.**  
  
Example:  
  
```python  
if Gold() < 2000:  
```  
  
### Graphic  
  
Method Signature:  
  
**Int32 Graphic(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns Item ID of given object (parameter can be serial or alias).**  
  
Example:  
  
```python  
Graphic("mount")  
```  
  
### Gray  
  
Method Signature:  
  
**Boolean Gray(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the mobile's notoriety is Attackable**  
  
Example:  
  
```python  
if Criminal("mount"):  
```  
  
### Hidden  
  
Method Signature:  
  
**Boolean Hidden(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns true if given mobile is hidden, false if not, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
if Hidden("self"):  
```  
  
### Hits  
  
Method Signature:  
  
**Int32 Hits(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the given mobiles hitpoints, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
hits = Hits("self")  
```  
  
### Hue  
  
Method Signature:  
  
**Int32 Hue(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns Hue of given object (parameter can be serial or alias).**  
  
Example:  
  
```python  
if Hue("mount") == 0:  
```  
  
### IgnoreObject  
  
Method Signature:  
  
**Void IgnoreObject(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Ignores the given object from find commands**  
  
Example:  
  
```python  
IgnoreObject("self")  
```  
  
### InFriendList  
  
Method Signature:  
  
**Boolean InFriendList(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if supplied mobile exists in the friends list.**  
  
Example:  
  
```python  
if InFriendList("last"):  
```  
  
### InIgnoreList  
  
Method Signature:  
  
**Boolean InIgnoreList(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Check whether the given serial / alias exists in the ignore list.**  
  
Example:  
  
```python  
if InIgnoreList("mount"):  
```  
  
### Innocent  
  
Method Signature:  
  
**Boolean Innocent(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the mobile's notoriety is Innocent**  
  
Example:  
  
```python  
if Criminal("mount"):  
```  
  
### InParty  
  
Method Signature:  
  
**Boolean InParty(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Return the true if the given serial/alias is in party with you.**  
  
Example:  
  
```python  
if InParty("friend"):  
```  
  
### InRange  
  
Method Signature:  
  
**Boolean InRange(System.Object, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* distance: Distance.  
  
Description:  
  
**Check for range between your character and another mobile or an item**  
  
Example:  
  
```python  
if InRange("enemy", 10):  
```  
  
### Int  
  
Method Signature:  
  
**Int32 Int()**  
  
Description:  
  
**Returns the intelligence of the player**  
  
Example:  
  
```python  
if Str() < 100:  
```  
  
### Invulnerable  
  
Method Signature:  
  
**Boolean Invulnerable(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the mobile's notoriety is Invulnerable**  
  
Example:  
  
```python  
if Criminal("mount"):  
```  
  
### Luck  
  
Method Signature:  
  
**Int32 Luck()**  
  
Description:  
  
**Returns the luck value as per status bar data.**  
  
Example:  
  
```python  
if Luck() < 800:  
```  
  
### Mana  
  
Method Signature:  
  
**Int32 Mana(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the given mobiles mana, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
if Mana("self") < 25:  
```  
  
### Map  
  
Method Signature:  
  
**Int32 Map()**  
  
Description:  
  
**Returns the current map of the Player**  
  
Example:  
  
```python  
Map()  
```  
  
### MaxFollowers  
  
Method Signature:  
  
**Int32 MaxFollowers()**  
  
Description:  
  
**Returns the number of max followers as per status bar data.**  
  
Example:  
  
```python  
if Followers() == MaxFollowers():  
```  
  
### MaxHits  
  
Method Signature:  
  
**Int32 MaxHits(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the given mobiles max hitpoints, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
hits = MaxHits("self")  
```  
  
### MaxMana  
  
Method Signature:  
  
**Int32 MaxMana(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the given mobiles max mana, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
mana = MaxMana("self")  
```  
  
### MaxStam  
  
Method Signature:  
  
**Int32 MaxStam(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the given mobiles max stamina, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
stam = MaxStam("self")  
```  
  
### MaxWeight  
  
Method Signature:  
  
**Int32 MaxWeight()**  
  
Description:  
  
**Returns the max weight as per status bar data.**  
  
Example:  
  
```python  
if MaxWeight() < 300:  
```  
  
### Mounted  
  
Method Signature:  
  
**Boolean Mounted(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the specified mobile is mounted.**  
  
Example:  
  
```python  
if Mounted("self"):  
```  
  
### MoveItem  
  
Method Signature:  
  
**Void MoveItem(System.Object, System.Object, Int32, Int32, Int32)**  
  
#### Parameters  
* item: An entity serial in integer or hex format, or an alias string such as "self".  
* destination: An entity serial in integer or hex format, or an alias string such as "self".  
* amount: Integer representing an amount, ie 10. (Optional)  
* x: X Coordinate. (Optional)  
* y: Y Coordinate. (Optional)  
  
Description:  
  
**Move item to container (parameters can be serials or aliases).**  
  
Example:  
  
```python  
MoveItem("source", "destination")  
```  
  
### MoveItemOffset  
  
Method Signature:  
  
**Void MoveItemOffset(System.Object, Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* xoffset: X Coordinate offset.  
* yoffset: Y Coordinate offset.  
* zoffset: Z Coordinate offset.  
* amount: Integer representing an amount, ie 10. (Optional)  
  
Description:  
  
**Move the given serial/alias to the specified x,y,z offset of the player, no amount specified or -1 will move the full stack.**  
  
Example:  
  
```python  
MoveItemOffset("trashitem", 0, 1, 0, -1)  
```  
  
### MoveItemXYZ  
  
Method Signature:  
  
**Void MoveItemXYZ(System.Object, Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* item: An entity serial in integer or hex format, or an alias string such as "self".  
* x: X Coordinate.  
* y: Y Coordinate.  
* z: Z Coordinate.  
* amount: Integer representing an amount, ie 10. (Optional)  
  
Description:  
  
**Moves the specified serial/alias to the given coordinates**  
  
Example:  
  
```python  
MoveItemXYZ('found', 0, 0, 0)  
```  
  
### MoveType  
  
Method Signature:  
  
**Void MoveType(Int32, System.Object, System.Object, Int32, Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* id: ItemID / Graphic such as  0x3db.  
* sourcecontainer: An entity serial in integer or hex format, or an alias string such as "self".  
* destinationcontainer: An entity serial in integer or hex format, or an alias string such as "self".  
* x: X Coordinate. (Optional)  
* y: Y Coordinate. (Optional)  
* z: Z Coordinate. (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
* amount: Integer representing an amount, ie 10. (Optional)  
  
Description:  
  
**Move a type from source to destintion.**  
  
Example:  
  
```python  
#To move a type to another container...

MoveType(0x170f, "backpack", "bank")

#Destination can be the ground by specifying destination container to -1 and specifying the coordinates...

MoveType(0x170f, "backpack", -1, 1928, 2526, 0)

#Optional parameters exist for Hue and Amount, to move 10 maximum with the a Hue of 50...
MoveType(0x170f, "backpack", "bank", -1, -1, 0, 50, 10)  
```  
  
### MoveTypeOffset  
  
Method Signature:  
  
**Boolean MoveTypeOffset(Int32, System.Object, Int32, Int32, Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* id: ItemID / Graphic such as  0x3db.  
* findlocation: An entity serial in integer or hex format, or an alias string such as "self".  
* xoffset: X Coordinate offset.  
* yoffset: Y Coordinate offset.  
* zoffset: Z Coordinate offset.  
* amount: Integer representing an amount, ie 10. (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
* range: Distance. (Optional)  
  
Description:  
  
**Move the given type from the specified source container to the specified x,y,z offset of the player, no amount specified or -1 will move the full stack.**  
  
Example:  
  
```python  
MoveTypeOffset(0xf0e, "backpack", 0, 1, 0, -1)  
```  
  
### MoveTypeXYZ  
  
Method Signature:  
  
**Boolean MoveTypeXYZ(Int32, System.Object, Int32, Int32, Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* id: ItemID / Graphic such as  0x3db.  
* findlocation: An entity serial in integer or hex format, or an alias string such as "self".  
* x: X Coordinate.  
* y: Y Coordinate.  
* z: Z Coordinate.  
* amount: Integer representing an amount, ie 10. (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
* range: Distance. (Optional)  
  
Description:  
  
**Move the given type from the specified source container to the specified X, Y, Z, no amount specified or -1 will move the full stack.**  
  
Example:  
  
```python  
MoveTypeXYZ(0xf0e, "backpack", 0, 0, 0, -1)  
```  
  
### Murderer  
  
Method Signature:  
  
**Boolean Murderer(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the mobile's notoriety is Murderer**  
  
Example:  
  
```python  
if Criminal("mount"):  
```  
  
### Name  
  
Method Signature:  
  
**System.String Name(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Return the name of the given mobile.**  
  
Example:  
  
```python  
if Name("self") == "Shmoo":  
```  
  
### Paralyzed  
  
Method Signature:  
  
**Boolean Paralyzed(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the specified mobile is frozen.**  
  
Example:  
  
```python  
if Paralyzed("self"):  
```  
  
### Poisoned  
  
Method Signature:  
  
**Boolean Poisoned(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the specified mobile is poisoned.**  
  
Example:  
  
```python  
if Poisoned("self"):  
```  
  
### Rehue  
  
Method Signature:  
  
**Void Rehue(System.Object, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* hue: Item Hue or -1 for any.  
  
Description:  
  
**Rehue an item/mobile the specified hue value, set to 0 to remove. (Experimental)**  
  
Example:  
  
```python  
Rehue("mount", 1176)  
```  
  
### RemoveFriend  
  
Method Signature:  
  
**Void RemoveFriend(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Removes a mobile from the friends list, will display target cursor if no serial/alias supplied.**  
  
Example:  
  
```python  
RemoveFriend()  
```  
  
### SpecialMoveExists  
  
Method Signature:  
  
**Boolean SpecialMoveExists(System.String)**  
  
#### Parameters  
* name: Special move name.  
  
Description:  
  
**Check for a specific special move**  
  
Example:  
  
```python  
if SpecialMoveExists("Death Strike"):  
```  
  
### Stam  
  
Method Signature:  
  
**Int32 Stam(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns the given mobiles stamina, if parameter is null, then returns the value from the player (parameter can be serial or alias).**  
  
Example:  
  
```python  
if Stam("self") < 25:  
```  
  
### Str  
  
Method Signature:  
  
**Int32 Str()**  
  
Description:  
  
**Returns the strength of the player**  
  
Example:  
  
```python  
if Str() < 100:  
```  
  
### SwingSpeedIncrease  
  
Method Signature:  
  
**Int32 SwingSpeedIncrease()**  
  
Description:  
  
**Return SwingSpeed Increase value.**  
  
Example:  
  
```python  
ssi = SwingSpeedIncrease()  
```  
  
### TithingPoints  
  
Method Signature:  
  
**Int32 TithingPoints()**  
  
Description:  
  
**Returns the current players' tithing points.**  
  
Example:  
  
```python  
if TithingPoints() < 1000:  
```  
  
### UseLayer  
  
Method Signature:  
  
**Boolean UseLayer(System.Object, System.Object)**  
  
#### Parameters  
* layer: String representing a layer, such as "OneHanded" or "Talisman" etc.  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Uses object in the specified layer, optional parameter for mobile**  
  
Example:  
  
```python  
UseLayer("Talisman")  
```  
  
### War  
  
Method Signature:  
  
**Boolean War(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Checks whether a mobile is in war mode.**  
  
Example:  
  
```python  
if War("self"):  
```  
  
### Weight  
  
Method Signature:  
  
**Int32 Weight()**  
  
Description:  
  
**Returns the current weight as as per status bar data.**  
  
Example:  
  
```python  
if Weight() > 300:  
```  
  
### X  
  
Method Signature:  
  
**Int32 X(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns X coordinate of given object (parameter can be serial or alias).**  
  
Example:  
  
```python  
x = X("self")  
```  
  
### Y  
  
Method Signature:  
  
**Int32 Y(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns Y coordinate of given object (parameter can be serial or alias).**  
  
Example:  
  
```python  
y = Y("self")  
```  
  
### YellowHits  
  
Method Signature:  
  
**Boolean YellowHits(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the specified mobile is yellowhits.**  
  
Example:  
  
```python  
if YellowHits("self"):  
```  
  
### Z  
  
Method Signature:  
  
**Int32 Z(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns Z coordinate of given object (parameter can be serial or alias).**  
  
Example:  
  
```python  
y = Y("self")  
```  
  



## Types  
### WandTypes  
* Clumsy  
* Identification  
* Heal  
* Feeblemind  
* Weaken  
* Magic_Arrow  
* Harm  
* Fireball  
* Greater_Heal  
* Lightning  
* Mana_Drain  
  
