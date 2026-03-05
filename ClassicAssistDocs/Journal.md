# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Journal  
### ClearJournal  
  
Method Signature:  
  
**Void ClearJournal(System.String)**  
  
#### Parameters  
* buffer: String value - See description for usage. (Optional)  
  
Description:  
  
**Clear all journal texts.**  
  
Example:  
  
```python  
ClearJournal()  
```  
  
### InJournal  
  
Method Signature:  
  
**Boolean InJournal(System.String, System.String, Int32, Int32, System.String)**  
  
#### Parameters  
* text: String value - See description for usage.  
* author: String value - See description for usage. (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
* timeout: Timeout specified in milliseconds. (Optional)  
* buffer: String value - See description for usage. (Optional)  
  
Description:  
  
**Check for a text in journal, optional source name.**  
  
Example:  
  
```python  
if InJournal("town guards", "system"):  
```  
  
### WaitForJournal  
  
Method Signature:  
  
**Boolean WaitForJournal(System.String, Int32, System.String, Int32)**  
  
#### Parameters  
* text: String value - See description for usage.  
* timeout: Timeout specified in milliseconds.  
* author: String value - See description for usage. (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
  
Description:  
  
**Wait the given timeout for the journal text to appear.**  
  
Example:  
  
```python  
if WaitForJournal("town guards", 5000, "system"):  
```  
  
### WaitForJournal  
  
Method Signature:  
  
**System.ValueTuple`2[System.Nullable`1[System.Int32],System.String] WaitForJournal(System.Collections.Generic.IEnumerable`1[System.String], Int32, System.String)**  
  
#### Parameters  
* entries: An array of strings.  
* timeout: Timeout specified in milliseconds.  
* author: String value - See description for usage. (Optional)  
  
Description:  
  
**Wait up the given timeout for one of any of provided array of string to appear in journal**  
  
Example:  
  
```python  
(idx, text) = WaitForJournal(['sex', 'drugs'], 5000)

if idx != None:
 print "Found text '{}' at index {}".format(text, idx)
else:
 print 'None of them were found :('  
```  
  



