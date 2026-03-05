# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Properties  
### Property  
  
Method Signature:  
  
**Boolean Property(System.Object, System.String)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* value: String value - See description for usage.  
  
Description:  
  
**Returns true if the given text appears in the items item properties.**  
  
Example:  
  
```python  
if Property("item", "Defense Chance Increase"):  
```  
  
### PropertyValue  
  
Method Signature:  
  
**T PropertyValue[T](System.Object, System.String, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* property: String value - See description for usage.  
* argument: Integer value - See description for usage. (Optional)  
  
Description:  
  
**Returns the argument value of the given property name. Optional argument index.**  
  
Example:  
  
```python  
val = PropertyValue[int]("backpack", "Contents")  
```  
  
### WaitForProperties  
  
Method Signature:  
  
**Boolean WaitForProperties(System.Object, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* timeout: Timeout specified in milliseconds.  
  
Description:  
  
**Wait for item properties to be received for specified item.**  
  
Example:  
  
```python  
WaitForProperties("backpack", 5000)  
```  
  



