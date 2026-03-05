## Advanced Macro Examples

### Using Linq with Python to cycle through mobiles with a bunch of conditions... 

```python
import clr
import System
clr.AddReference("System.Core")
clr.ImportExtensions(System.Linq)
from Assistant import Engine

mounts = [0x115, 0xb3]

mount = Engine.Mobiles.Where(lambda m: mounts.Contains(m.ID) 
                                        and m.Distance < 10 
					and not InFriendList(m.Serial) 
					and not InIgnoreList(m.Serial)).FirstOrDefault()

if (mount == None):
	ClearIgnoreList()
	SysMessage('No mount found')
	Stop()

SetEnemy(mount.Serial)
IgnoreObject(mount.Serial)
```
## Using the GumpParser the get the text of the entries in a runebook

Gump ID / Element position maybe the shard specific.
```python
from Assistant import Engine

def GetRunebookEntries(serial):
	entries = []
	
	UseObject(serial)
	
	if WaitForGump(0x554b87f3, 5000):
		res,gump = Engine.Gumps.GetGump(0x554b87f3)
		
		y = 60
		
		while y <= 165:
			element = gump.Pages[1].GetElementByXY(145, y)
			if element != None and element.Hue != 0:
				entries.append(element.Text)

			y = y + 5
			
		y = 60

		while y <= 165:
			element = gump.Pages[1].GetElementByXY(305, y)
			if element != None and element.Hue != 0:
				entries.append(element.Text)
				
			y = y + 5
			
	return entries

entries = GetRunebookEntries(0x419cbac8)

for x in range(len(entries)):
	SysMessage(entries[x])
```
## Using import clr to reference a custom .NET dll
```python
import clr
clr.AddReferenceToFileAndPath(Engine.StartupPath + "\BODParser.dll")
from Assistant import Engine
from BODParser import *

def GetReward(serial):

	item = Engine.Items.GetItem(serial)
	if (item == None):
		return "Unknown"
	bod = BulkOrderDeed.Parse(item)
	
	if (bod != None):
		return bod.Reward.ToString()
	

SetAlias('ash60', 0x441e0654)
SetAlias('ash30', 0x41255f89)
SetAlias('empty', 0x4081d5e2)
SetAlias('putbook', 0x44501e97)

WaitForProperties('empty', 5000)
if CountType(0x2258) == 0 and Property('empty', 'Deeds In Book') > 0:
	UseObject('empty')
	WaitForGump(0x54f555df, 5000)
	for i in range(5):
		ReplyGump(0x54f555df, 5)
		WaitForGump(0x54f555df, 1000)	

while FindType(0x2258, -1, 'backpack'):
	reward = GetReward(GetAlias('found'))

	if (reward == "ASH30"):
		MoveItem('found', 'ash30')
	elif (reward == "ASH60"):
		MoveItem('found', 'ash60')
	else:
		MoveItem('found', 'putbook')
```

## Add a packet wait entry to play a sound when trade window is opened

```py
from Assistant import Engine
from ClassicAssist.UO.Network.PacketFilter import *
           
pwe = Engine.PacketWaitEntries.Add(PacketFilterInfo(0x6F), PacketDirection.Incoming, True)

pwe.Lock.WaitOne()

while True:
    PlaySound("Bike Horn.wav")
    Pause(1000)
```

### Faster Run

```py
from Assistant import Engine
from ClassicAssist.UO import UOMath
from ClassicAssist.UO.Data import Direction

def DirectionTo(alias):
    mobile = Engine.Mobiles.GetMobile(GetAlias(alias))
    
    if mobile == None:
        return Direction.Invalid

    return UOMath.MapDirection( Engine.Player.X, Engine.Player.Y, mobile.X, mobile.Y )
    
def FRun(dir):
    if dir == Direction.Invalid:
        return
    Engine.Move(dir, True)    
    
while Distance('enemy') > 1:    
    FRun(DirectionTo('enemy'))
    Pause(100)
```

### Get backpack items with name filter
```py
import clr
import System
clr.AddReference('System.Core')
clr.ImportExtensions(System.Linq)
from Assistant import Engine

def GetBackpackItems(filter = None):
	if Engine.Player == None:
		return []
	
	if Engine.Player.Backpack.Container == None:
		UseObject('backpack')
		WaitForContents('backpack', 5000)
		
	items = Engine.Player.Backpack.Container.SelectEntities(lambda i: filter == None or i.Name.ToLower().Contains(filter))
	
	if (items == None):
		return []
		
	return items.Select(lambda i: i.Serial)
		
for x in GetBackpackItems('rune'):
	SysMessage(hex(x))
```