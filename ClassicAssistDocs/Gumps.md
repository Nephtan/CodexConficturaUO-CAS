# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Gumps  
### CloseGump  
  
Method Signature:  
  
**Void CloseGump(Int32)**  
  
#### Parameters  
* serial: An entity serial such as 0xf00ff00f.  
  
Description:  
  
**Close a specified gump serial**  
  
Example:  
  
```python  
CloseGump(0x454ddef)  
```  
  
### ConfirmPrompt  
  
Method Signature:  
  
**Boolean ConfirmPrompt(System.String, Boolean)**  
  
Description:  
  
**Displays an ingame prompt with the specified message, returns True if Okay was pressed, False if not.**  
  
Example:  
  
```python  
res = ConfirmPrompt("Play macro?")

if res:
 PlayMacro("Macro")  
```  
  
### GumpExists  
  
Method Signature:  
  
**Boolean GumpExists(UInt32)**  
  
Description:  
  
**Checks if a gump id exists or not.**  
  
Example:  
  
```python  
if GumpExists(0xff):  
```  
  
### InGump  
  
Method Signature:  
  
**Boolean InGump(UInt32, System.String)**  
  
#### Parameters  
* gumpid: An entity serial in integer or hex format, or an alias string such as "self".  
* text: String value - See description for usage.  
  
Description:  
  
**Check for a text in gump.**  
  
Example:  
  
```python  
if InGump(0xf00f, "lethal darts"):  
```  
  
### ItemArrayGump  
  
Method Signature:  
  
**Int32[] ItemArrayGump(System.Collections.Generic.IList`1[System.Object], Boolean, Int32, Int32, Boolean)**  
  
Description:  
  
**Displays a gump with the selected serials / aliases in a grid, similar to the UOSteam loot grid, returns array of serials selected**  
  
Example:  
  
```python  
from Assistant import Engine

#single select, specified items
result = ItemArrayGump([0x462d3373, 0x462d6029])

if result.Length == 0:
 print 'Nothing was selected'
else:
 print 'Serial {} was selected'.format(result[0])

#showing backpack items, multi select, at coords 200, 200
items = Engine.Player.Backpack.Container.GetItems()
results = ItemArrayGump(items, True, 200, 200)

if results.Length == 0:
 print 'Nothing was selected'
else:
 print '{} item(s) were selected'.format(results.Length)
 
 for serial in results:
  print 'Serial {} was selected'.format(serial)
  
```  
  
### MessagePrompt  
  
Method Signature:  
  
**System.ValueTuple`2[System.Boolean,System.String] MessagePrompt(System.String, System.String, Boolean)**  
  
#### Parameters  
* message: String value - See description for usage.  
* initialtext: String value - See description for usage. (Optional)  
* closable: True/False value, see description for usage. (Optional)  
  
Description:  
  
**Displays an ingame gump prompting for a message**  
  
Example:  
  
```python  
res, name = MessagePrompt("Enter Name?", "Whiskers")

if res:
 Rename(0xc1b, name)  
```  
  
### OpenGuildGump  
  
Method Signature:  
  
**Void OpenGuildGump()**  
  
Description:  
  
**Opens the Guild gump**  
  
Example:  
  
```python  
OpenGuildGump()  
```  
  
### OpenHelpGump  
  
Method Signature:  
  
**Void OpenHelpGump()**  
  
Description:  
  
**Opens the Help gump**  
  
Example:  
  
```python  
OpenHelpGump()  
```  
  
### OpenQuestsGump  
  
Method Signature:  
  
**Void OpenQuestsGump()**  
  
Description:  
  
**Opens the Quests gump**  
  
Example:  
  
```python  
OpenQuestsGump()  
```  
  
### OpenVirtueGump  
  
Method Signature:  
  
**Void OpenVirtueGump(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Opens the Virtue gump of the given serial/alias (defaults to current player)**  
  
Example:  
  
```python  
OpenVirtueGump("enemy")  
```  
  
### ReplyGump  
  
Method Signature:  
  
**Void ReplyGump(UInt32, Int32, Int32[], System.Collections.Generic.Dictionary`2[System.Int32,System.String])**  
  
#### Parameters  
* gumpid: ItemID / Graphic such as  0x3db.  
* buttonid: Gump button ID.  
* switches: Integer value - See description for usage. (Optional)  
* textentries: Not specified - See description for usage. (Optional)  
  
Description:  
  
**Sends a button reply to server gump, parameters are gumpID and buttonID.**  
  
Example:  
  
```python  
ReplyGump(0xff, 0)  
```  
  
### SelectionPrompt  
  
Method Signature:  
  
**System.ValueTuple`2[System.Boolean,System.Int32] SelectionPrompt(System.Collections.Generic.IEnumerable`1[System.String], System.String, Boolean)**  
  
#### Parameters  
* options: An array of strings.  
* message: String value - See description for usage. (Optional)  
* closable: True/False value, see description for usage. (Optional)  
  
Description:  
  
**Produces an in-game gump to choose from a list of options

Returns a tuple with a boolean signifying whether the OK button was pressed, and the index of the entry selected**  
  
Example:  
  
```python  
res, index = SelectionPrompt(['Sex', 'Drugs', 'Rock and Roll'])

if res:
 print 'Option {} was selected'.format(index)
else:
 print 'Cancel was pressed'  
```  
  
### WaitForGump  
  
Method Signature:  
  
**Boolean WaitForGump(UInt32, Int32)**  
  
#### Parameters  
* gumpid: ItemID / Graphic such as  0x3db. (Optional)  
* timeout: Timeout specified in milliseconds. (Optional)  
  
Description:  
  
**Pauses until incoming gump packet is received, optional paramters of gump ID and timeout**  
  
Example:  
  
```python  
WaitForGump(0xff, 5000)  
```  
  



