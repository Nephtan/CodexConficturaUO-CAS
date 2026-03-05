# ClassicAssist Macro Commands  
Generated on 11/6/2025 1:30:34 AM  
Version: 4.500.1+caef4152379b9d2d54089cfe4fb7fe02fa3f2184  
  
## Skills  
### SetSkill  
  
Method Signature:  
  
**Void SetSkill(System.String, System.String)**  
  
#### Parameters  
* skill: Skill name.  
* status: Lock Status - "up", "down", or "locked". See Also: [LockStatus](#LockStatus)  
  
Description:  
  
**Sets the lock state of the given skill, up, down or locked.**  
  
Example:  
  
```python  
SetSkill("hiding", "locked")  
```  
  
### SetStatus  
  
Method Signature:  
  
**Void SetStatus(System.String, System.String)**  
  
#### Parameters  
* stat: String value - See description for usage. See Also: [StatType](#StatType)  
* lockstatus: Lock Status - "up", "down", or "locked". See Also: [LockStatus](#LockStatus)  
  
Description:  
  
**Sets the lock state of the given stat, up, down or locked.**  
  
Example:  
  
```python  
SetStatus('str', 'locked')  
```  
  
### Skill  
  
Method Signature:  
  
**Double Skill(System.String, Boolean)**  
  
#### Parameters  
* name: Skill name.  
* baseskill: Not specified - See description for usage. (Optional)  
  
Description:  
  
**Returns the value of the given skill name.**  
  
Example:  
  
```python  
if Skill("hiding") < 100:  
```  
  
### SkillCap  
  
Method Signature:  
  
**Double SkillCap(System.String)**  
  
#### Parameters  
* name: Skill name.  
  
Description:  
  
**Returns the skill cap for the specified skill**  
  
Example:  
  
```python  
if SkillCap("Blacksmithy") == 120:  
```  
  
### SkillDelta  
  
Method Signature:  
  
**Double SkillDelta(System.String)**  
  
#### Parameters  
* name: Skill name.  
  
Description:  
  
**Returns the skill value delta since last reset**  
  
Example:  
  
```python  
if SkillDelta('Hiding') > 0.5:
    Stop()  
```  
  
### SkillState  
  
Method Signature:  
  
**System.String SkillState(System.String)**  
  
#### Parameters  
* name: Skill name.  
  
Description:  
  
**Returns the lock status of the given skill, up, down, or locked.**  
  
Example:  
  
```python  
if SkillState("hiding') == "locked":  
```  
  
### UseLastSkill  
  
Method Signature:  
  
**Void UseLastSkill()**  
  
Description:  
  
**Uses the last invoked skill**  
  
Example:  
  
```python  
UseLastSkill()  
```  
  
### UseSkill  
  
Method Signature:  
  
**Void UseSkill(System.String)**  
  
#### Parameters  
* skill: Skill name.  
  
Description:  
  
**Invokes the given skill name.**  
  
Example:  
  
```python  
UseSkill("Hiding")  
```  
  



## Types  
### LockStatus  
* Up  
* Down  
* Locked  
  
### StatType  
* Str  
* Dex  
* Int  
  
