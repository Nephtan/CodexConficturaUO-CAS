# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Timers  
### CreateTimer  
  
Method Signature:  
  
**Void CreateTimer(System.String)**  
  
#### Parameters  
* name: Timer name.  
  
Description:  
  
**Create a new named timer.**  
  
Example:  
  
```python  
CreateTimer("shmoo")  
```  
  
### RemoveTimer  
  
Method Signature:  
  
**Void RemoveTimer(System.String)**  
  
#### Parameters  
* name: Timer name.  
  
Description:  
  
**Removes the named timer.**  
  
Example:  
  
```python  
RemoveTimer("shmoo")  
```  
  
### SetTimer  
  
Method Signature:  
  
**Void SetTimer(System.String, Int32)**  
  
#### Parameters  
* name: An entity serial in integer or hex format, or an alias string such as "self".  
* milliseconds: Integer value - See description for usage. (Optional)  
  
Description:  
  
**Set a timer value and create in case it does not exist.**  
  
Example:  
  
```python  
SetTimer("shmoo", 0)  
```  
  
### Timer  
  
Method Signature:  
  
**Int64 Timer(System.String)**  
  
#### Parameters  
* name: Timer name.  
  
Description:  
  
**Check for a named timer value.**  
  
Example:  
  
```python  
if Timer("shmoo") > 10000:  
```  
  
### TimerExists  
  
Method Signature:  
  
**Boolean TimerExists(System.String)**  
  
#### Parameters  
* name: Timer name.  
  
Description:  
  
**Returns true if the timer exists.**  
  
Example:  
  
```python  
if TimerExists("shmoo"):  
```  
  
### TimerMsg  
  
Method Signature:  
  
**Void TimerMsg(System.String)**  
  
#### Parameters  
* name: Timer name.  
  
Description:  
  
**Outputs the elapsed timer value as a SystemMessage**  
  
Example:  
  
```python  
TimerMsg("shmoo")  
```  
  



