# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## World Map  
### AddMapMarker  
  
Method Signature:  
  
**Void AddMapMarker(System.String, Int32, Int32, Int32, Int32, System.String)**  
  
#### Parameters  
* name: String representing a name, ie "Snoopy".  
* x: X Coordinate.  
* y: Y Coordinate.  
* facet: Integer value - See description for usage.  
* zoomlevel: Integer value - See description for usage. (Optional)  
* iconname: String value - See description for usage. (Optional)  
  
Description:  
  
**Adds a marker on the world map**  
  
Example:  
  
```python  
AddMapMarker("Treasure", 1000, 1000, 0)  
```  
  
### ClearMapMarkers  
  
Method Signature:  
  
**Void ClearMapMarkers()**  
  
Description:  
  
**Clears all map markers**  
  
Example:  
  
```python  
ClearMapMarkers()  
```  
  
### RemoveMapMarker  
  
Method Signature:  
  
**Void RemoveMapMarker(System.String)**  
  
#### Parameters  
* name: String value - See description for usage.  
  
Description:  
  
**Removes all map markers with the specified name from the world map**  
  
Example:  
  
```python  
RemoveMapMarker("Treasure")  
```  
  



