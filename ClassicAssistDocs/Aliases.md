# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Aliases  
### FindAlias  
  
Method Signature:  
  
**Boolean FindAlias(System.String)**  
  
#### Parameters  
* aliasname: Alias name.  
  
Description:  
  
**Returns true if alias serial can be found on screen, false if not.**  
  
Example:  
  
```python  
if FindAlias("mount"):  
```  
  
### GetAlias  
  
Method Signature:  
  
**Int32 GetAlias(System.String)**  
  
#### Parameters  
* aliasname: Alias name.  
  
Description:  
  
**Gets the value of the given alias name.**  
  
Example:  
  
```python  
GetAlias("mount")  
```  
  
### GetPlayerAlias  
  
Method Signature:  
  
**Int32 GetPlayerAlias(System.String)**  
  
#### Parameters  
* aliasname: Alias name.  
  
Description:  
  
**Gets the value of the given alias name, for the current player.**  
  
Example:  
  
```python  
GetPlayerAlias("mount")  
```  
  
### PromptAlias  
  
Method Signature:  
  
**Int32 PromptAlias(System.String)**  
  
#### Parameters  
* aliasname: Alias name.  
  
Description:  
  
**Prompt with an in-game target cursor to supply value for given alias name.**  
  
Example:  
  
```python  
PromptAlias("mount")  
```  
  
### PromptMacroAlias  
  
Method Signature:  
  
**Int32 PromptMacroAlias(System.String)**  
  
#### Parameters  
* aliasname: Alias name.  
  
Description:  
  
**Prompt with an in-game target cursor to supply value for given alias name, alias is valid only in the current macro.**  
  
Example:  
  
```python  
PromptMacroAlias("mount")  
```  
  
### PromptPlayerAlias  
  
Method Signature:  
  
**Int32 PromptPlayerAlias(System.String)**  
  
#### Parameters  
* aliasname: Alias name.  
  
Description:  
  
**Prompt with an in-game target cursor to supply value for given alias name, for the current player.**  
  
Example:  
  
```python  
PromptPlayerAlias("mount")  
```  
  
### SetAlias  
  
Method Signature:  
  
**Void SetAlias(System.String, System.Object)**  
  
#### Parameters  
* aliasname: Alias name.  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Sets the value of the given alias name.**  
  
Example:  
  
```python  
SetAlias("mount", 0x40000001)  
```  
  
### SetMacroAlias  
  
Method Signature:  
  
**Void SetMacroAlias(System.String, System.Object)**  
  
#### Parameters  
* aliasname: Alias name.  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Sets the value of the given alias name, alias is valid only in the current macro.**  
  
Example:  
  
```python  
SetMacroAlias("mount", 0x40000001)  
```  
  
### SetPlayerAlias  
  
Method Signature:  
  
**Void SetPlayerAlias(System.String, System.Object)**  
  
#### Parameters  
* aliasname: Alias name.  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Sets the value of the given alias name, for the current player.**  
  
Example:  
  
```python  
SetPlayerAlias("mount", 0x40000001)  
```  
  
### UnsetAlias  
  
Method Signature:  
  
**Void UnsetAlias(System.String)**  
  
#### Parameters  
* aliasname: Alias name.  
  
Description:  
  
**Removes the alias name given.**  
  
Example:  
  
```python  
UnsetAlias("mount")  
```  
  
### UnsetPlayerAlias  
  
Method Signature:  
  
**Void UnsetPlayerAlias(System.String)**  
  
#### Parameters  
* aliasname: Alias name.  
  
Description:  
  
**Removes the alias name given, for the current player.**  
  
Example:  
  
```python  
UnsetPlayerAlias("mount")  
```  
  



