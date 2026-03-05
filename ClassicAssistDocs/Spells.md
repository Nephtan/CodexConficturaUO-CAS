# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Spells  
### Cast  
  
Method Signature:  
  
**Void Cast(System.String)**  
  
#### Parameters  
* name: Spell name.  
  
Description:  
  
**Cast the given named spell and automatically target given object.**  
  
Example:  
  
```python  
Cast("Recall", "runebook")  
```  
  
### Cast  
  
Method Signature:  
  
**Boolean Cast(System.String, System.Object)**  
  
#### Parameters  
* name: Spell name.  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Cast the given named spell and automatically target given object.**  
  
Example:  
  
```python  
Cast("Recall", "runebook")  
```  
  
### InterruptSpell  
  
Method Signature:  
  
**Void InterruptSpell()**  
  
Description:  
  
**Attempts to interrupt spell by lifting an item briefly.**  
  
Example:  
  
```python  
InterruptSpell()  
```  
  



