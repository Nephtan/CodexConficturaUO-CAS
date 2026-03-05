# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Actions  
### Attack  
  
Method Signature:  
  
**Void Attack(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Attack mobile (parameter can be serial or alias).**  
  
Example:  
  
```python  
Attack("last")  
```  
  
### BandageSelf  
  
Method Signature:  
  
**Boolean BandageSelf()**  
  
Description:  
  
**Applies a bandage to the player.**  
  
Example:  
  
```python  
BandageSelf()  
```  
  
### ClearHands  
  
Method Signature:  
  
**Void ClearHands(System.String)**  
  
#### Parameters  
* hand: Hand - "left", "right", or "both". (Optional)  
  
Description:  
  
**Clear hands, "left", "right", or "both"**  
  
Example:  
  
```python  
ClearHands("both")  
```  
  
### ClearUseOnce  
  
Method Signature:  
  
**Void ClearUseOnce()**  
  
Description:  
  
**Clear UseOnce list.**  
  
Example:  
  
```python  
ClearUseOnce()  
```  
  
### ClickObject  
  
Method Signature:  
  
**Void ClickObject(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Single click object (parameter can be serial or alias).**  
  
Example:  
  
```python  
ClickObject("last")  
```  
  
### Contents  
  
Method Signature:  
  
**Int32 Contents(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns the item count for given container.**  
  
Example:  
  
```python  
if Contents("backpack") > 120:  
```  
  
### ContextMenu  
  
Method Signature:  
  
**Void ContextMenu(System.Object, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* entry: Context menu entry index number.  
  
Description:  
  
**Request a context menu option.**  
  
Example:  
  
```python  
ContextMenu(0x00aabbcc, 1)  
```  
  
### EquipItem  
  
Method Signature:  
  
**Void EquipItem(System.Object, System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* layer: String representing a layer, such as "OneHanded" or "Talisman" etc. See Also: [Layer](#Layer)  
  
Description:  
  
**Equip a specific item into a given layer. Use object inspector to determine layer value.**  
  
Example:  
  
```python  
EquipItem("axe", "TwoHanded")  
```  
  
### EquipLastWeapon  
  
Method Signature:  
  
**Void EquipLastWeapon()**  
  
Description:  
  
**Send quick switch weapon packet (probably not supported on pre-AoS servers.**  
  
Example:  
  
```python  
EquipLastWeapon()  
```  
  
### EquipType  
  
Method Signature:  
  
**Void EquipType(Int32, System.Object)**  
  
#### Parameters  
* id: ItemID / Graphic such as  0x3db.  
* layer: String representing a layer, such as "OneHanded" or "Talisman" etc. See Also: [Layer](#Layer)  
  
Description:  
  
**Equip a specific type into a given layer. Use object inspector to determine layer value.**  
  
Example:  
  
```python  
EquipType(0xff, "TwoHanded")  
```  
  
### Feed  
  
Method Signature:  
  
**Void Feed(System.Object, Int32, Int32, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* graphic: ItemID / Graphic such as  0x3db.  
* amount: Integer representing an amount, ie 10. (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
  
Description:  
  
**Feed a given alias or serial with graphic.**  
  
Example:  
  
```python  
Feed("mount", 0xff)  
```  
  
### FindLayer  
  
Method Signature:  
  
**Boolean FindLayer(System.Object, System.Object)**  
  
#### Parameters  
* layer: String representing a layer, such as "OneHanded" or "Talisman" etc. See Also: [Layer](#Layer)  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Returns true and updates found alias if an item exists in the specified layer, option serial/alias for mobile to check.**  
  
Example:  
  
```python  
if FindLayer("OneHanded"):  
```  
  
### InRegion  
  
Method Signature:  
  
**Boolean InRegion(System.String, System.Object)**  
  
#### Parameters  
* attribute: String value - See description for usage. See Also: [RegionAttributes](#RegionAttributes)  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if the region of the target has the specified attribute.**  
  
Example:  
  
```python  
if InRegion("Guarded", "self")  
```  
  
### Ping  
  
Method Signature:  
  
**Int64 Ping()**  
  
Description:  
  
**Retrieve an approximated ping with server. -1 on failure.**  
  
Example:  
  
```python  
Ping()  
```  
  
### Rename  
  
Method Signature:  
  
**Void Rename(System.Object, System.String)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* name: String representing a name, ie "Snoopy".  
  
Description:  
  
**Sends rename request.**  
  
Example:  
  
```python  
Rename("mount", "Snoopy")  
```  
  
### ShowNames  
  
Method Signature:  
  
**Void ShowNames(System.String)**  
  
#### Parameters  
* showtype: Show type - "mobiles" or "corpses". See Also: [ShowNamesType](#ShowNamesType)  
  
Description:  
  
**Display corpses and/or mobiles names (parameter "mobiles" or "corpses".**  
  
Example:  
  
```python  
ShowNames("corpses")  
```  
  
### ToggleMounted  
  
Method Signature:  
  
**Void ToggleMounted()**  
  
Description:  
  
**Unmounts if mounted, or mounts if unmounted, will prompt for mount if no "mount" alias.**  
  
Example:  
  
```python  
ToggleMounted()  
```  
  
### UseObject  
  
Method Signature:  
  
**Void UseObject(System.Object, Boolean)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* skipqueue: Not specified - See description for usage. (Optional)  
  
Description:  
  
**Sends use (doubleclick) request for given object (parameter can be serial or alias).**  
  
Example:  
  
```python  
UseObject("mount")  
```  
  
### UseOnce  
  
Method Signature:  
  
**Boolean UseOnce(Int32, Int32)**  
  
#### Parameters  
* graphic: ItemID / Graphic such as  0x3db.  
* hue: Item Hue or -1 for any. (Optional)  
  
Description:  
  
**Use a specific item type (graphic) from your backpack, only once**  
  
Example:  
  
```python  
UseOnce(0xff)  
```  
  
### UseTargetedItem  
  
Method Signature:  
  
**Void UseTargetedItem(System.Object, System.Object)**  
  
#### Parameters  
* item: An entity serial in integer or hex format, or an alias string such as "self".  
* target: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Uses specified item and targets target in one action. Requires server support (OSI / ServUO)**  
  
Example:  
  
```python  
UseTargetedItem('bandage', 'pet')  
```  
  
### UseType  
  
Method Signature:  
  
**Void UseType(System.Object, Int32, System.Object, Boolean)**  
  
#### Parameters  
* type: An entity serial in integer or hex format, or an alias string such as "self".  
* hue: Item Hue or -1 for any. (Optional)  
* container: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
* skipqueue: Not specified - See description for usage. (Optional)  
  
Description:  
  
**Sends use (doubleclick) request for given type, optional parameters of hue and container object (defaults to player backpack) (parameters can be serial or alias).**  
  
Example:  
  
```python  
UseType(0xff)  
```  
  
### WaitForContents  
  
Method Signature:  
  
**Boolean WaitForContents(System.Object, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* timeout: Timeout specified in milliseconds. (Optional)  
  
Description:  
  
**Wait for container contents for given container.**  
  
Example:  
  
```python  
WaitForContents("backpack", 5000)  
```  
  
### WaitForContext  
  
Method Signature:  
  
**Boolean WaitForContext(System.Object, Int32, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* entry: Context menu entry index number.  
* timeout: Timeout specified in milliseconds.  
  
Description:  
  
**Request or wait for a context menu option.**  
  
Example:  
  
```python  
# select by index number
WaitForContext('self', 2, 5000)
# select by entry name
WaitForContext('self', "Open Item Insurance Menu", 5000)  
```  
  
### WaitForContext  
  
Method Signature:  
  
**Boolean WaitForContext(System.Object, System.String, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* entryname: String value - See description for usage.  
* timeout: Timeout specified in milliseconds.  
  
Description:  
  
**Request or wait for a context menu option.**  
  
Example:  
  
```python  
# select by index number
WaitForContext('self', 2, 5000)
# select by entry name
WaitForContext('self', "Open Item Insurance Menu", 5000)  
```  
  



## Types  
### Layer  
* Invalid  
* OneHanded  
* TwoHanded  
* Shoes  
* Pants  
* Shirt  
* Helm  
* Gloves  
* Ring  
* Talisman  
* Neck  
* Hair  
* Waist  
* InnerTorso  
* Bracelet  
* Unused_xF  
* FacialHair  
* MiddleTorso  
* Earrings  
* Arms  
* Cloak  
* Backpack  
* OuterTorso  
* OuterLegs  
* InnerLegs  
* Mount  
* ShopBuy  
* ShopResale  
* ShopSell  
* Bank  
* LastValid  
  
### RegionAttributes  
* None  
* Guarded  
* Jail  
* Wilderness  
* Town  
* Dungeon  
* Special  
* Default  
  
### ShowNamesType  
* Mobiles  
* Corpses  
  
