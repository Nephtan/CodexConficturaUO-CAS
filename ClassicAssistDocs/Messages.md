# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Messages  
### AllyMsg  
  
Method Signature:  
  
**Void AllyMsg(System.String)**  
  
#### Parameters  
* message: String value - See description for usage.  
  
Description:  
  
**Sends given message to alliance chat.**  
  
Example:  
  
```python  
AllyMsg("alert")  
```  
  
### CancelPrompt  
  
Method Signature:  
  
**Void CancelPrompt()**  
  
Description:  
  
**Cancels the current prompt.**  
  
Example:  
  
```python  
CancelPrompt()  
```  
  
### ChatMsg  
  
Method Signature:  
  
**Void ChatMsg(System.String)**  
  
#### Parameters  
* message: String value - See description for usage.  
  
Description:  
  
**Sends a chat message.**  
  
Example:  
  
```python  
ChatMsg("Mary had a little lamb")  
```  
  
### EmoteMsg  
  
Method Signature:  
  
**Void EmoteMsg(System.String)**  
  
#### Parameters  
* message: String value - See description for usage.  
  
Description:  
  
**Emotes the given message**  
  
Example:  
  
```python  
EmoteMsg("hi")  
```  
  
### GetText  
  
Method Signature:  
  
**System.ValueTuple`2[System.Boolean,System.String] GetText(System.String, Int32)**  
  
#### Parameters  
* prompt: String value - See description for usage.  
* timeout: Timeout specified in milliseconds. (Optional)  
  
Description:  
  
**Sends an internal prompt request and returns the text entered**  
  
Example:  
  
```python  
res, name = GetText("Name?", 10000)

if res:
 Rename(0xc1b, name)  
```  
  
### GuildMsg  
  
Method Signature:  
  
**Void GuildMsg(System.String)**  
  
#### Parameters  
* message: String value - See description for usage.  
  
Description:  
  
**Sends given message to guild chat.**  
  
Example:  
  
```python  
GuildMsg("alert")  
```  
  
### HeadMsg  
  
Method Signature:  
  
**Void HeadMsg(System.String, System.Object, Int32)**  
  
#### Parameters  
* message: String value - See description for usage.  
* obj: An entity serial in integer or hex format, or an alias string such as "self". (Optional)  
* hue: Item Hue or -1 for any. (Optional)  
  
Description:  
  
**Displays overhead message above given mobile / item.**  
  
Example:  
  
```python  
HeadMsg("hi", "backpack")  
```  
  
### Msg  
  
Method Signature:  
  
**Void Msg(System.String, Int32)**  
  
#### Parameters  
* message: String value - See description for usage.  
* hue: Item Hue or -1 for any. (Optional)  
  
Description:  
  
**Speaks the given message, Optional hue**  
  
Example:  
  
```python  
Msg("hi")  
```  
  
### PartyMsg  
  
Method Signature:  
  
**Void PartyMsg(System.String)**  
  
#### Parameters  
* message: String value - See description for usage.  
  
Description:  
  
**Sends given message to party chat.**  
  
Example:  
  
```python  
PartyMsg("alert")  
```  
  
### PromptMsg  
  
Method Signature:  
  
**Void PromptMsg(System.String)**  
  
#### Parameters  
* message: String value - See description for usage.  
  
Description:  
  
**Sends the specified message as a prompt response**  
  
Example:  
  
```python  
PromptMsg("hello")  
```  
  
### WaitForPrompt  
  
Method Signature:  
  
**Boolean WaitForPrompt(Int32)**  
  
#### Parameters  
* timeout: Timeout specified in milliseconds.  
  
Description:  
  
**Wait the specified timeout for a prompt packet to be received**  
  
Example:  
  
```python  
WaitForPrompt(5000)  
```  
  
### WhisperMsg  
  
Method Signature:  
  
**Void WhisperMsg(System.String)**  
  
#### Parameters  
* message: String value - See description for usage.  
  
Description:  
  
**Whispers the given message**  
  
Example:  
  
```python  
WhisperMsg("hi")  
```  
  
### YellMsg  
  
Method Signature:  
  
**Void YellMsg(System.String)**  
  
#### Parameters  
* message: String value - See description for usage.  
  
Description:  
  
**Yells the given message**  
  
Example:  
  
```python  
YellMsg("hi")  
```  
  



