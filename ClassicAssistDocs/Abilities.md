# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Abilities  
### ActiveAbility  
  
Method Signature:  
  
**Boolean ActiveAbility()**  
  
Description:  
  
**Returns True if either the primary or secondary ability is set**  
  
Example:  
  
```python  
if not ActiveAbility():
 SetAbility("primary", "on")  
```  
  
### ClearAbility  
  
Method Signature:  
  
**Void ClearAbility()**  
  
Description:  
  
**Clear weapon ability.**  
  
Example:  
  
```python  
ClearAbility()  
```  
  
### Fly  
  
Method Signature:  
  
**Void Fly()**  
  
Description:  
  
**(Garoyle) Start flying if not already flying.**  
  
Example:  
  
```python  
Fly()  
```  
  
### Flying  
  
Method Signature:  
  
**Boolean Flying(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
  
Description:  
  
**Returns true if mobile is currently flying.**  
  
Example:  
  
```python  
if Flying("self"):  
```  
  
### Land  
  
Method Signature:  
  
**Void Land()**  
  
Description:  
  
**(Garoyle) Stop flying if currently flying.**  
  
Example:  
  
```python  
Land()  
```  
  
### SetAbility  
  
Method Signature:  
  
**Void SetAbility(System.String, System.String)**  
  
#### Parameters  
* ability: The name of the ability, "primary", "secondary", "stun" or "disarm".  
* onoff: "on" or "off". (Optional)  
  
Description:  
  
**Set weapon ability, parameter "primary" / "secondary".**  
  
Example:  
  
```python  
SetAbility("primary")  
```  
  



