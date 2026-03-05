# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Main  
### BringClientWindowToFront  
  
Method Signature:  
  
**Void BringClientWindowToFront()**  
  
Description:  
  
**Bring client window to front**  
  
Example:  
  
```python  
BringClientWindowToFront()  
```  
  
### DisplayQuestPointer  
  
Method Signature:  
  
**Void DisplayQuestPointer(Int32, Int32, Boolean)**  
  
#### Parameters  
* x: X Coordinate.  
* y: Y Coordinate.  
* enabled: True/False value, see description for usage. (Optional)  
  
Description:  
  
**Display quest arrow pointer to specified coordinates**  
  
Example:  
  
```python  
# add pointer
DisplayQuestPointer(1000, 1000, True)
Pause(2000)
# remove pointer
DisplayQuestPointer(1000, 1000, False)  
```  
  
### HideEntity  
  
Method Signature:  
  
**Void HideEntity(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Remove an item/mobile from the screen**  
  
Example:  
  
```python  
ClearIgnoreList()
# Hide all corpses on screen
while FindType(0x2006):
 HideEntity('found')
 IgnoreObject('found')  
```  
  
### Hotkeys  
  
Method Signature:  
  
**Void Hotkeys(System.String)**  
  
#### Parameters  
* onoff: "on" or "off". (Optional)  
  
Description:  
  
**Enable and disable hotkeys.**  
  
Example:  
  
```python  
Hotkeys()  
```  
  
### Info  
  
Method Signature:  
  
**Void Info(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Show object inspector for supplied serial / alias, will prompt for target if no parameter given.**  
  
Example:  
  
```python  
Info("self")  
```  
  
### InvokeVirtue  
  
Method Signature:  
  
**Void InvokeVirtue(System.String)**  
  
#### Parameters  
* virtue: String value - See description for usage. See Also: [Virtues](#Virtues)  
  
Description:  
  
**Use a virtue by name.**  
  
Example:  
  
```python  
InvokeVirtue("Honor")  
```  
  
### Logout  
  
Method Signature:  
  
**Void Logout()**  
  
Description:  
  
**Disconnects from the server and returns to the login screen**  
  
Example:  
  
```python  
Logout()  
```  
  
### MessageBox  
  
Method Signature:  
  
**Void MessageBox(System.String, System.String)**  
  
#### Parameters  
* title: String value - See description for usage.  
* body: String value - See description for usage.  
  
Description:  
  
**Show a simple message box with a custom title and body.**  
  
Example:  
  
```python  
MessageBox("title", "message")  
```  
  
### OpenECV  
  
Method Signature:  
  
**Void OpenECV(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Open entity collection viewer for specified container serial/alias**  
  
Example:  
  
```python  
OpenECV('backpack')  
```  
  
### Pause  
  
Method Signature:  
  
**Void Pause(Int32)**  
  
#### Parameters  
* milliseconds: Timeout specified in milliseconds.  
  
Description:  
  
**Pauses execution for the given amount in milliseconds.**  
  
Example:  
  
```python  
Pause(1000)  
```  
  
### Playing  
  
Method Signature:  
  
**Boolean Playing()**  
  
Description:  
  
**Returns true if there is a macro, use in background macros.**  
  
Example:  
  
```python  
if Playing():  
```  
  
### Playing  
  
Method Signature:  
  
**Boolean Playing(System.String)**  
  
#### Parameters  
* macroname: Macro name.  
  
Description:  
  
**Returns true if there is a macro, use in background macros.**  
  
Example:  
  
```python  
if Playing():  
```  
  
### PlaySound  
  
Method Signature:  
  
**Void PlaySound(System.Object, Boolean)**  
  
Description:  
  
**Play sound by id or system .wav file.**  
  
Example:  
  
```python  
PlaySound("Bike Horn.wav")  
```  
  
### Quit  
  
Method Signature:  
  
**Void Quit()**  
  
Description:  
  
**Closes the client**  
  
Example:  
  
```python  
Quit()  
```  
  
### Resync  
  
Method Signature:  
  
**Void Resync()**  
  
Description:  
  
**Sends Resync request to server.**  
  
Example:  
  
```python  
Resync()  
```  
  
### SetAutologin  
  
Method Signature:  
  
**Void SetAutologin(Boolean, System.String, Int32, Int32)**  
  
Description:  
  
**Configures autologin settings**  
  
Example:  
  
```python  
SetAutologin(False)  
```  
  
### SetQuietMode  
  
Method Signature:  
  
**Void SetQuietMode(Boolean)**  
  
#### Parameters  
* onoff: "on" or "off".  
  
Description:  
  
**Set quiet mode True/False, True reduces the number of messages macro commands emit.**  
  
Example:  
  
```python  
SetQuietMode(True)  
```  
  
### Snapshot  
  
Method Signature:  
  
**System.ValueTuple`2[System.Boolean,System.String] Snapshot(Int32, System.Nullable`1[System.Boolean], System.String)**  
  
#### Parameters  
* delay: Integer value - See description for usage. (Optional)  
* fullscreen: True/False value, see description for usage. (Optional)  
* filename: String value - See description for usage. (Optional)  
  
Description:  
  
**Take a screenshot of the window**  
  
Example:  
  
```python  
# Just the game client area, no delay, default filename
Snapshot()

# Fullscreen snapshot, 3 second delay, default filename
Snapshot(3000, True)

# Client area snapshot, no delay, custom filename
Snapshot(0, False, "screenshot.png")  
```  
  
### SysMessage  
  
Method Signature:  
  
**Void SysMessage(System.String, Int32)**  
  
#### Parameters  
* text: String value - See description for usage.  
* hue: Item Hue or -1 for any. (Optional)  
  
Description:  
  
**Send a text message.**  
  
Example:  
  
```python  
# default hue
SysMessage("Hello")
# specifying hue
SysMessage("Hello", 35)  
```  
  
### WarMode  
  
Method Signature:  
  
**Void WarMode(System.String)**  
  
#### Parameters  
* onoff: "on" or "off". (Optional)  
  
Description:  
  
**Sets war mode status, parameter on, off, or toggle, defaults to toggle if no parameter given.**  
  
Example:  
  
```python  
WarMode("on")  
```  
  



## Types  
### Virtues  
* None  
* Honor  
* Sacrafice  
* Valor  
* Compassion  
* Honesty  
* Humility  
* Justice  
* Spirituality  
  
