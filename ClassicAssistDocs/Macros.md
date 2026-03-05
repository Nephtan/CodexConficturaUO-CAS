# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Macros  
### IsRunning  
  
Method Signature:  
  
**Boolean IsRunning(System.String)**  
  
#### Parameters  
* name: Macro name.  
  
Description:  
  
**Returns True if the specified macro name is currently running**  
  
Example:  
  
```python  
if IsRunning('macro'):  
```  
  
### PlayCUOMacro  
  
Method Signature:  
  
**Void PlayCUOMacro(System.String)**  
  
#### Parameters  
* name: Macro name.  
  
Description:  
  
**Plays the specified CUO macro name**  
  
Example:  
  
```python  
PlayCUOMacro('Paperdoll')  
```  
  
### PlayMacro  
  
Method Signature:  
  
**Void PlayMacro(System.String, System.Object[])**  
  
#### Parameters  
* name: Macro name.  
* args: Comma seperated list of parameters.  
  
Description:  
  
**Plays the given macro name.**  
  
Example:  
  
```python  
# Play another macro

PlayMacro("beep")

# Play another macro passing parameters to it

PlayMacro("beep", 1, "moo")

# In the played macro, args[0] will be 1 and args[1] will be "moo"  
```  
  
### Replay  
  
Method Signature:  
  
**Void Replay(System.Object[])**  
  
#### Parameters  
* args: Comma seperated list of parameters.  
  
Description:  
  
**Replay the current macro**  
  
Example:  
  
```python  
Replay()  
```  
  
### Stop  
  
Method Signature:  
  
**Void Stop(System.String)**  
  
#### Parameters  
* name: Macro name. (Optional)  
  
Description:  
  
**Stops the current macro.**  
  
Example:  
  
```python  
# Stop the current macro
Stop()
# Stop a macro by name
Stop("Background Macro")  
```  
  
### StopAll  
  
Method Signature:  
  
**Void StopAll()**  
  
Description:  
  
**Stops all running macros including background macros.**  
  
Example:  
  
```python  
StopAll()  
```  
  



