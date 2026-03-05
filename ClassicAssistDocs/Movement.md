# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Movement  
### Follow  
  
Method Signature:  
  
**Void Follow(System.Object)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
  
Description:  
  
**Instructs ClassicUO to follow the specified alias/serial, supply no parameter to cancel**  
  
Example:  
  
```python  
if FindObject('enemy'):
 Follow('enemy')
 Attack('enemy')
else:
 Follow() # stop following
Pause(1000)  
```  
  
### Following  
  
Method Signature:  
  
**Boolean Following()**  
  
Description:  
  
**Returns True if currently following a target**  
  
Example:  
  
```python  
if not Following():
 Follow('enemy')  
```  
  
### Pathfind  
  
Method Signature:  
  
**Boolean Pathfind(System.Object, Boolean, Int32)**  
  
#### Parameters  
* obj: An entity serial in integer or hex format, or an alias string such as "self".  
* checkdistance: Not specified - See description for usage. (Optional)  
* desireddistance: Not specified - See description for usage. (Optional)  
  
Description:  
  
**Requests client to pathfind to given coordinates / entity**  
  
Example:  
  
```python  
#Pathfind to coordinates
Pathfind(1438, 1630, 20)

#Pathfind to entity
SetEnemy(0x3c9)
Pathfind('enemy')

# Cancel pathfind in progress
Pathfind(-1)  
```  
  
### Pathfind  
  
Method Signature:  
  
**Boolean Pathfind(Int32, Int32, Int32, Boolean, Int32)**  
  
#### Parameters  
* x: X Coordinate.  
* y: Y Coordinate.  
* z: Z Coordinate.  
* checkdistance: Not specified - See description for usage. (Optional)  
* desireddistance: Not specified - See description for usage. (Optional)  
  
Description:  
  
**Requests client to pathfind to given coordinates / entity**  
  
Example:  
  
```python  
#Pathfind to coordinates
Pathfind(1438, 1630, 20)

#Pathfind to entity
SetEnemy(0x3c9)
Pathfind('enemy')

# Cancel pathfind in progress
Pathfind(-1)  
```  
  
### Pathfinding  
  
Method Signature:  
  
**Boolean Pathfinding()**  
  
Description:  
  
**Returns True if ClassicUO is currently pathfinding**  
  
Example:  
  
```python  
Pathfind('enemy')
Pause(25) # there is a delay between calling Pathfind() and Pathfinding() being True

while Pathfinding():
 Pause(50)
 
HeadMsg("die scum", "self")  
```  
  
### Run  
  
Method Signature:  
  
**Boolean Run(System.String)**  
  
#### Parameters  
* direction: Direction, ie "West". See Also: [Direction](#Direction)  
  
Description:  
  
**Run in the given direction.**  
  
Example:  
  
```python  
Run("east")  
```  
  
### SetForceWalk  
  
Method Signature:  
  
**Void SetForceWalk(Boolean)**  
  
Description:  
  
**Set force walk, True or False**  
  
Example:  
  
```python  
SetForceWalk(True)  
```  
  
### ToggleForceWalk  
  
Method Signature:  
  
**Void ToggleForceWalk()**  
  
Description:  
  
**Toggle Force Walk**  
  
Example:  
  
```python  
ToggleForceWalk()  
```  
  
### Turn  
  
Method Signature:  
  
**Void Turn(System.String)**  
  
#### Parameters  
* direction: Direction, ie "West". See Also: [Direction](#Direction)  
  
Description:  
  
**Turn in the given direction.**  
  
Example:  
  
```python  
Turn("east")  
```  
  
### Walk  
  
Method Signature:  
  
**Boolean Walk(System.String)**  
  
#### Parameters  
* direction: Direction, ie "West".  
  
Description:  
  
**Walk in the given direction.**  
  
Example:  
  
```python  
Walk("east")  
```  
  



## Types  
### Direction  
* North  
* Northeast  
* East  
* Southeast  
* South  
* Southwest  
* West  
* Northwest  
* Invalid  
  
