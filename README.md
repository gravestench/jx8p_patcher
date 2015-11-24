# jx8p_patcher
A patch generation and manipulation utility for the Roland JX-8P

I use mido and pygame, and you'll see me using it in these examples.



# Get your midi I/O ready
```
import mido
from pygame import midi as midi
midi.init()

mo=mido.open_output("Bitstream 3X")
mi=mido.open_input("Bitstream 3X")
```

For some reason, portmidi acts strange in my environment and I can only get mido to open ports after I do `pygame.midi.init()`

# import the patcher
```
import jx8p_patcher as jx8p
```
This module has stuff for working with the jx8p sysex files and will create objects which represent a JX-8P patch

# make patch instances
```
p1=jx8p.Patch(r"C:\some\path\to\HOT.syx")
p2=jx8p.Patch(r"C:\some\path\to\COLD.syx")
# You send a patch to a mido output port like this:
# mo.send(jx8p.message(p))
```
# Interpolation example
This will probably be built into the module as time goes on, but for now, this is how I do interpolation.
```
def cclerp(patch1, patch2):
  while True:
    m = mi.receive() # `mi` is a mido input port
    if m.type == 'control_change':
      p=jx8p.lerp2(patch1, patch2, m.value)
      mo.send(jx8p.message(p))
```

# randomized patch generation
```
import random
def rp():
  p = jx8p.Patch()
  for param in p.parameters:
    param.value = random.randint(0,128)
  return p
```

# Lerping two random sysex files from a directory
```
import os, random
def rsyx(dirpath):
  filepaths=os.listdir(dirpath)
  syxfiles=[s for s in filepaths if "SYX" in s]
  return dirpath + '\\' + rand.choice(syxfiles)

my_sysex_folder = r"C:\sysex\dir"
p1=jx8p.Patch(rsyx(my_sysex_dir))
p2=jx8p.Patch(rsyx(my_sysex_dir))

cclerp(p1, p2)
```
