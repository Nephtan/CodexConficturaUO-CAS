# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Agents  
### Autoloot  
  
Method Signature:  
  
**Void Autoloot(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Causes autoloot to check a particular container, even when not enabled, and bypassing the corpse type check**  
  
Example:  
  
```python  
Autoloot("found")  
```  
  
### Autolooting  
  
Method Signature:  
  
**Boolean Autolooting()**  
  
Description:  
  
**Returns True if currently checking corpse / autolooting items.**  
  
Example:  
  
```python  
if Autolooting():  
```  
  
### ClearTrapPouch  
  
Method Signature:  
  
**Void ClearTrapPouch()**  
  
Description:  
  
**Clears the items in the trap pouch agent...**  
  
Example:  
  
```python  
ClearTrapPouch()  
```  
  
### Counter  
  
Method Signature:  
  
**Int32 Counter(System.String)**  
  
#### Parameters  
* name: Agent entry name.  
  
Description:  
  
**Returns the count of the given counter agent.**  
  
Example:  
  
```python  
Counter("bm")  
```  
  
### Dress  
  
Method Signature:  
  
**Void Dress(System.String)**  
  
#### Parameters  
* name: Agent entry name. (Optional)  
  
Description:  
  
**Dress all items in the specified dress agent.**  
  
Example:  
  
```python  
Dress("Dress-1")  
```  
  
### DressConfig  
  
Method Signature:  
  
**Void DressConfig()**  
  
Description:  
  
**Adds all equipped items to a temporary list that isn't persisted on client close.**  
  
Example:  
  
```python  
DressConfig()  
```  
  
### Dressing  
  
Method Signature:  
  
**Boolean Dressing()**  
  
Description:  
  
**Returns true if the Dress agent is currently dressing or undressing.**  
  
Example:  
  
```python  
if Dressing():  
```  
  
### Organizer  
  
Method Signature:  
  
**Void Organizer(System.String, System.Object, System.Object)**  
  
#### Parameters  
* name: Agent entry name.  
* sourcecontainer: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
* destinationcontainer: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Executes the named Organizer agent.**  
  
Example:  
  
```python  
Organizer("Organizer-1")  
```  
  
### Organizing  
  
Method Signature:  
  
**Boolean Organizing()**  
  
Description:  
  
**Returns true if currently running an organizer agent, or false if not.**  
  
Example:  
  
```python  
if Organizing():  
```  
  
### SetAutoloot  
  
Method Signature:  
  
**Void SetAutoloot(System.String)**  
  
#### Parameters  
* onoff: "on" or "off". (Optional)  
  
Description:  
  
**Enable/Disable/Toggle the Autoloot agent**  
  
Example:  
  
```python  
SetAutoloot("off")  
```  
  
### SetAutolootContainer  
  
Method Signature:  
  
**Void SetAutolootContainer(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Sets the container for the Autoloot agent to put items into...**  
  
Example:  
  
```python  
SetAutolootContainer("backpack")  
```  
  
### SetOrganizerContainers  
  
Method Signature:  
  
**Void SetOrganizerContainers(System.String, System.Object, System.Object)**  
  
#### Parameters  
* entryname: Agent entry name.  
* sourcecontainer: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
* destinationcontainer: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Set the source and destination for the specified Organizer name**  
  
Example:  
  
```python  
SetOrganizerContainers("Organizer-1", "backpack", "bank")  
```  
  
### SetScavenger  
  
Method Signature:  
  
**Void SetScavenger(System.String)**  
  
#### Parameters  
* onoff: "on" or "off". (Optional)  
  
Description:  
  
**Enable/Disable/Toggle the Scavenger agent**  
  
Example:  
  
```python  
SetScavenger("off")  
```  
  
### SetTrapPouch  
  
Method Signature:  
  
**Void SetTrapPouch(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Adds the specified item to the trap pouch agent item list...**  
  
Example:  
  
```python  
ClearTrapPouch()

if FindType(0xe79, -1, 'backpack'):
    Cast('Magic Trap', 'found')
    SetTrapPouch('found')  
```  
  
### SetVendorBuyAutoBuy  
  
Method Signature:  
  
**Void SetVendorBuyAutoBuy(System.String, System.String)**  
  
#### Parameters  
* listname: List name.  
* onoff: "on" or "off". (Optional)  
  
Description:  
  
**Enables or disables autobuying of the specified vendor buy list name...**  
  
Example:  
  
```python  
# set on
SetVendorBuyAutoBuy("regs", "on")
# set off
SetVendorBuyAutoBuy("regs", "off")
# default will toggle
SetVendorBuyAutoBuy("regs")  
```  
  
### StopDress  
  
Method Signature:  
  
**Void StopDress()**  
  
Description:  
  
**Stops the dress agent is it is currently running**  
  
Example:  
  
```python  
StopDress()  
```  
  
### StopOrganizer  
  
Method Signature:  
  
**Void StopOrganizer()**  
  
Description:  
  
**Stops the organizer agent if currently running**  
  
Example:  
  
```python  
StopOrganizer()  
```  
  
### Undress  
  
Method Signature:  
  
**Void Undress(System.String)**  
  
#### Parameters  
* name: Agent entry name.  
  
Description:  
  
**Undress all items in the specified dress agent.**  
  
Example:  
  
```python  
Undress("Dress-1")  
```  
  
### UseTrapPouch  
  
Method Signature:  
  
**Void UseTrapPouch()**  
  
Description:  
  
**Uses the first item in the Trap Pouch agent list...**  
  
Example:  
  
```python  
UseTrapPouch()  
```  
  



