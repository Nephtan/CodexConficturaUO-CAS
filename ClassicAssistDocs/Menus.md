# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Menus  
### InMenu  
  
Method Signature:  
  
**Boolean InMenu(Int32, System.String)**  
  
#### Parameters  
* gumpid: ItemID / Graphic such as  0x3db.  
* text: String value - See description for usage.  
  
Description:  
  
**Returns True if the menu title or entry titles contains the given text.**  
  
Example:  
  
```python  
UseSkill('Tracking')
WaitForMenu(0x1d0, 5000)
ReplyMenu(0x1d0, 3, 0x2106, 0)
WaitForMenu(0x1d1, 5000)
if InMenu(0x1d1, 'Omar'):
 HeadMsg('Omar is in range', 'self')
CloseMenu(0x1d1)  
```  
  
### MenuExists  
  
Method Signature:  
  
**Boolean MenuExists(Int32)**  
  
Description:  
  
**Return true if the given menu id exists.**  
  
Example:  
  
```python  
if MenuExists(0x1d1):  
```  
  
### ReplyMenu  
  
Method Signature:  
  
**Void ReplyMenu(Int32, Int32, Int32, Int32)**  
  
#### Parameters  
* gumpid: ItemID / Graphic such as  0x3db.  
* buttonid: Gump button ID.  
* itemid: ItemID / Graphic such as  0x3db. (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
  
Description:  
  
**Sends a button reply to server menu**  
  
Example:  
  
```python  
ReplyMenu(0x1d0, 3, 0x2106, 0)  
```  
  
### WaitForMenu  
  
Method Signature:  
  
**Boolean WaitForMenu(Int32, Int32)**  
  
#### Parameters  
* gumpid: ItemID / Graphic such as  0x3db. (Optional)  
* timeout: Timeout specified in milliseconds. (Optional)  
  
Description:  
  
**Pauses until incoming menu packet is received, optional paramters of gump ID and timeout**  
  
Example:  
  
```python  
UseSkill('Tracking')
WaitForMenu(0x1d0, 5000)
ReplyMenu(0x1d0, 3, 0x2106, 0)
WaitForMenu(0x1d1, 5000)  
```  
  



