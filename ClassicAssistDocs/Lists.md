# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Lists  
### ClearList  
  
Method Signature:  
  
**Void ClearList(System.String)**  
  
#### Parameters  
* listname: List name.  
  
Description:  
  
**Clear a list by name.**  
  
Example:  
  
```python  
ClearList("list")  
```  
  
### CreateList  
  
Method Signature:  
  
**Void CreateList(System.String)**  
  
#### Parameters  
* listname: List name.  
  
Description:  
  
**Create list with given name, if list already exists, it is overwritten.**  
  
Example:  
  
```python  
CreateList("list")  
```  
  
### GetList  
  
Method Signature:  
  
**System.Object[] GetList(System.String)**  
  
#### Parameters  
* listname: List name.  
  
Description:  
  
**Returns array of all entries in the list, for use with for loop etc.**  
  
Example:  
  
```python  
GetList("list")  
```  
  
### InList  
  
Method Signature:  
  
**Boolean InList(System.String, System.Object)**  
  
#### Parameters  
* listname: List name.  
* value: Integer value - See description for usage.  
  
Description:  
  
**Checks whether a list contains a given element.**  
  
Example:  
  
```python  
if InList("shmoo", 1):  
```  
  
### List  
  
Method Signature:  
  
**Int32 List(System.String)**  
  
#### Parameters  
* listname: List name.  
  
Description:  
  
**Returns the number of entries in the list.**  
  
Example:  
  
```python  
if List("list") < 5:  
```  
  
### ListExists  
  
Method Signature:  
  
**Boolean ListExists(System.String)**  
  
#### Parameters  
* listname: List name.  
  
Description:  
  
**Returns true if list exist, or false if not.**  
  
Example:  
  
```python  
if ListExists("list"):  
```  
  
### PopList  
  
Method Signature:  
  
**Int32 PopList(System.String, System.Object)**  
  
#### Parameters  
* listname: List name.  
* elementvalue: Element value to remove from list, or 'front' to remove the first item, or 'back' to remove last entry, default 'back'. (Optional)  
  
Description:  
  
**Remove elements from a list, returns the number of elements removed**  
  
Example:  
  
```python  
CreateList("hippies")
PushList("hippies", 1)
PushList("hippies", 2)
PushList("hippies", 3)

PopList("hippies", "front") # Removes 1
PopList("hippies", "back") # Removes 3
PopList("hippies", "2") # Removes any 2's that exist in the list


for x in GetList("hippies"):
 print x # Never reached because list is empty
  
```  
  
### PushList  
  
Method Signature:  
  
**Void PushList(System.String, System.Object)**  
  
#### Parameters  
* listname: List name.  
* value: Integer value - See description for usage.  
  
Description:  
  
**Pushes a value to the end of the list, will create list if it doesn't exist.**  
  
Example:  
  
```python  
PushList("list", 1)  
```  
  
### RemoveList  
  
Method Signature:  
  
**Void RemoveList(System.String)**  
  
#### Parameters  
* listname: List name.  
  
Description:  
  
**Removes the list with the given name.**  
  
Example:  
  
```python  
RemoveList("list")  
```  
  



