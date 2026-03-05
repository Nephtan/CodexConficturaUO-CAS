# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Target  
### CancelTarget  
  
Method Signature:  
  
**Void CancelTarget()**  
  
Description:  
  
**Cancel an existing cursor/target.**  
  
Example:  
  
```python  
CancelTarget()  
```  
  
### ClearTargetQueue  
  
Method Signature:  
  
**Void ClearTargetQueue()**  
  
Description:  
  
**Clears the target queue when queue last target/target self is enabled.**  
  
Example:  
  
```python  
ClearTargetQueue()  
```  
  
### GetEnemy  
  
Method Signature:  
  
**Boolean GetEnemy(System.Collections.Generic.IEnumerable`1[System.String], System.String, System.String, System.String, Int32)**  
  
#### Parameters  
* notorieties:  . See Also: [TargetNotoriety](#TargetNotoriety)  
* bodytype:  . (Optional) See Also: [TargetBodyType](#TargetBodyType)  
* distance:  . (Optional) See Also: [TargetDistance](#TargetDistance)  
* infliction:  . (Optional) See Also: [TargetInfliction](#TargetInfliction)  
* maxdistance: Distance. (Optional)  
  
Description:  
  
**Get mobile and set enemy alias.**  
  
Example:  
  
```python  
#get murderer
GetEnemy(['Murderer'])
#get closest murderer, any body type
GetEnemy(['Murderer'], 'Any', 'Closest')
#get next any notoriety, humanoid or transformation - unmounted
GetEnemy(['Any'], 'Both', 'Next', 'Unmounted')  
```  
  
### GetFriend  
  
Method Signature:  
  
**Boolean GetFriend(System.Collections.Generic.IEnumerable`1[System.String], System.String, System.String, System.String, Int32)**  
  
#### Parameters  
* notorieties:  . See Also: [TargetNotoriety](#TargetNotoriety)  
* bodytype:  . (Optional) See Also: [TargetBodyType](#TargetBodyType)  
* distance:  . (Optional) See Also: [TargetDistance](#TargetDistance)  
* infliction:  . (Optional) See Also: [TargetInfliction](#TargetInfliction)  
* maxdistance: Distance. (Optional)  
  
Description:  
  
**Get mobile and set friend alias.**  
  
Example:  
  
```python  
GetFriend(["Murderer"])  
```  
  
### GetFriendListOnly  
  
Method Signature:  
  
**Boolean GetFriendListOnly(System.String, System.String, System.String, Int32)**  
  
#### Parameters  
* distance:  . (Optional) See Also: [TargetDistance](#TargetDistance)  
* targetinfliction:  . (Optional) See Also: [TargetInfliction](#TargetInfliction)  
* bodytype:  . (Optional) See Also: [TargetBodyType](#TargetBodyType)  
* maxdistance: Distance. (Optional)  
  
Description:  
  
**Get friend that only exists in the friends list, parameter distance 'Closest'/'Nearest'/'Next'**  
  
Example:  
  
```python  
GetFriendListOnly("Closest")  
```  
  
### SetEnemy  
  
Method Signature:  
  
**Void SetEnemy(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Sets the enemy to the given serial/alias.**  
  
Example:  
  
```python  
SetEnemy("mount")  
```  
  
### SetFriend  
  
Method Signature:  
  
**Void SetFriend(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Sets the friend to the given serial/alias.**  
  
Example:  
  
```python  
SetFriend("mount")  
```  
  
### SetLastTarget  
  
Method Signature:  
  
**Void SetLastTarget(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Sets the last target to the given serial/alias.**  
  
Example:  
  
```python  
SetLastTarget("mount")  
```  
  
### Target  
  
Method Signature:  
  
**Void Target(System.Object, Boolean, Boolean, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* checkrange: Not specified - See description for usage. (Optional)  
* usequeue: Not specified - See description for usage. (Optional)  
* senderserial: Not specified - See description for usage. (Optional)  
  
Description:  
  
**Targets the given object (parameter can be serial or alias).**  
  
Example:  
  
```python  
Target("self")  
```  
  
### TargetByResource  
  
Method Signature:  
  
**Void TargetByResource(System.Object, System.String)**  
  
#### Parameters  
* toolobj: An entity serial in integer or hex format, or an alias string such as "self".  
* resourcetype: String value - See description for usage. See Also: [TargetResourceType](#TargetResourceType)  
  
Description:  
  
**Uses tool and targets specified resource type (Requires server support (OSI / ServUO))**  
  
Example:  
  
```python  
TargetByResource('pickaxe', 'Ore')  
```  
  
### TargetExists  
  
Method Signature:  
  
**Boolean TargetExists(System.String)**  
  
#### Parameters  
* targetexiststype: Target type - "harmful", "beneficial", or "neutral". (Optional) See Also: [TargetExistsType](#TargetExistsType)  
  
Description:  
  
**Returns true if a target cursor is displayed and the notoriety matches the supplied value, defaults to 'Any', options are 'Any', 'Beneficial', 'Harmful' or 'Neutral'**  
  
Example:  
  
```python  
if TargetExists("Harmful"):  
```  
  
### TargetGround  
  
Method Signature:  
  
**Void TargetGround(System.Object, Int32, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* hue: Item Hue or -1 for any. (Optional)  
* range: Range, ie 10. (Optional)  
  
Description:  
  
**Target the specified type on the ground, optional parameters for hue and distance.**  
  
Example:  
  
```python  
TargetGround(0x190, -1, 10)  
```  
  
### TargetTileOffset  
  
Method Signature:  
  
**Void TargetTileOffset(Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* xoffset: X Coordinate offset.  
* yoffset: Y Coordinate offset.  
* zoffset: Y Coordinate offset.  
* itemid: ItemID / Graphic such as  0x3db. (Optional)  
  
Description:  
  
**Targets the tile at the given offsets relative to the player**  
  
Example:  
  
```python  
#Targets the tile at the current Y coordinate + 1
TargetTileOffset(0, 1, 0)  
```  
  
### TargetTileOffsetResource  
  
Method Signature:  
  
**Void TargetTileOffsetResource(Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* xoffset: X Coordinate offset.  
* yoffset: Y Coordinate offset.  
* zoffset: Y Coordinate offset.  
* itemid: ItemID / Graphic such as  0x3db. (Optional)  
  
Description:  
  
**Targets the tile at the given offsets relative to the player (automatically targeting trees/cave tiles/water if present)**  
  
Example:  
  
```python  
TargetTileOffsetResource(0, -1, 0)  
```  
  
### TargetTileRelative  
  
Method Signature:  
  
**Void TargetTileRelative(System.Object, Int32, Boolean, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* distance: Integer value - See description for usage.  
* reverse: True/False value, see description for usage. (Optional)  
* itemid: ItemID / Graphic such as  0x3db. (Optional)  
  
Description:  
  
**Target tile the given distance relative to the specified alias/serial, optional boolean for reverse mode.**  
  
Example:  
  
```python  
TargetTileRelative("self", 1, False)  
```  
  
### TargetType  
  
Method Signature:  
  
**Void TargetType(System.Object, Int32, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* hue: Item Hue or -1 for any. (Optional)  
* range: Range, ie 10. (Optional)  
  
Description:  
  
**Target specified type in player backpack, optional parameters for hue and search level.**  
  
Example:  
  
```python  
TargetType(0xff, 0, 3)  
```  
  
### TargetXYZ  
  
Method Signature:  
  
**Void TargetXYZ(Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* x: X Coordinate.  
* y: Y Coordinate.  
* z: Z Coordinate.  
* itemid: ItemID / Graphic such as  0x3db. (Optional)  
  
Description:  
  
**Targets the ground at the given coordinates.**  
  
Example:  
  
```python  
TargetXYZ(1000, 1000, 0)  
```  
  
### WaitForTarget  
  
Method Signature:  
  
**Boolean WaitForTarget(Int32)**  
  
#### Parameters  
* timeout: Timeout specified in milliseconds. (Optional)  
  
Description:  
  
**Wait for target packet from server, optional timeout parameter (default 5000 milliseconds).**  
  
Example:  
  
```python  
WaitForTarget(5000)  
```  
  
### WaitForTargetOrFizzle  
  
Method Signature:  
  
**Boolean WaitForTargetOrFizzle(Int32)**  
  
#### Parameters  
* timeout: Timeout specified in milliseconds.  
  
Description:  
  
**Waits the specified timeout for target cursor whilst returning false if the spell is fizzled / uncastable beforehand.**  
  
Example:  
  
```python  
WaitForTargetOrFizzle(5000)  
```  
  
### WaitingForTarget  
  
Method Signature:  
  
**Boolean WaitingForTarget()**  
  
Description:  
  
**Returns true whenever the core is internally waiting for a server target**  
  
Example:  
  
```python  
if WaitingForTarget():  
```  
  



## Types  
### TargetBodyType  
* Any  
* Humanoid  
* Transformation  
* Both  
  
### TargetDistance  
* Next  
* Nearest  
* Closest  
* Previous  
  
### TargetExistsType  
* Any  
* Beneficial  
* Harmful  
* Neutral  
  
### TargetInfliction  
* Any  
* Lowest  
* Poisoned  
* Mortaled  
* Paralyzed  
* Dead  
* Unmounted  
  
### TargetNotoriety  
* None  
* Innocent  
* Criminal  
* Enemy  
* Murderer  
* Friend  
* Gray  
* Any  
  
### TargetResourceType  
* Ore  
* Sand  
* Wood  
* Graves  
* Red_Mushrooms  
  
