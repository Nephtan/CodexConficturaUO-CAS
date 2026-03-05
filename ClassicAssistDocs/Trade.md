# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Trade  
### TradeAccept  
  
Method Signature:  
  
**Void TradeAccept()**  
  
Description:  
  
**Accepts the current trade window**  
  
Example:  
  
```python  
TradeAccept()  
```  
  
### TradeClose  
  
Method Signature:  
  
**Void TradeClose()**  
  
Description:  
  
**Closes the current trade window**  
  
Example:  
  
```python  
TradeClose()  
```  
  
### TradeCurrency  
  
Method Signature:  
  
**Void TradeCurrency(Int32, Int32)**  
  
Description:  
  
**Sets the gold and platinum in the trade window (for shards that support it)**  
  
Example:  
  
```python  
TradeCurrency(60000, 1)  
```  
  
### TradeReject  
  
Method Signature:  
  
**Void TradeReject()**  
  
Description:  
  
**Rejects (unticks) the current trade window**  
  
Example:  
  
```python  
TradeReject()  
```  
  
### WaitForTradeWindow  
  
Method Signature:  
  
**Boolean WaitForTradeWindow(Int32)**  
  
#### Parameters  
* timeout: Timeout specified in milliseconds. (Optional)  
  
Description:  
  
**Waits the specified number of milliseconds for trade window action, -1 for infinite**  
  
Example:  
  
```python  
WaitForTradeWindow(5000)  
```  
  



