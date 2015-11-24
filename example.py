import pygame, mido
from pygame import midi as midi
import random
import os

import jx8p_patcher as jx8p

rtmidi = mido.Backend('mido.backends.rtmidi')
portmidi = mido.Backend('mido.backends.portmidi')

# This is my midi controller, which has din-midi and usb-midi
# the jx8p is connected to this controller
# mo=portmidi.open_output("Bitstreama 3x")
# mi=portmidi.open_input("Bitstream 3x")

# opening portmidi ports
# my_midi_controller = "LoopBe Internal MIDI"
# mo=portmidi.open_output(my_midi_controller)
# mi=portmidi.open_input(my_midi_controller)

# opening virtual ports
# virtual_name="jx8p_patcher"
# vmo=rtmidi.open_output(virtual_name, virtual=True)
# vmi=rtmidi.open_input(virtual_name, virtual=True)

midi.init() # portmidi doesnt really work on my windows system unless i use pygame.midi.init()

# I have a bunch of .syx files for the jx8p
# here is an example of loading a .syx file as a patch
p1=jx8p.Patch(r"C:\Users\Dylan\Downloads\jx8p.syx\jcb\dryrhodes.syx")
p2=jx8p.Patch(r"C:\Users\Dylan\Downloads\jx8p.syx\jcb\celeste1.syx")
# You send a patch to a mido output port like this:
# mo.send(jx8p.message(patch_instance))

def cclerp(patch1, patch2):
  """
  maps any midi cc to an interpolation
  
  at the moment, this is hardcoded

  Every step actually generates a new patch
  and dispatches it to the midi output i opened
  earlier.

  """
  while True:
    m = mi.receive()
    if m.type == 'control_change':
      p=jx8p.lerp2(patch1, patch2, m.value)
      mo.send(jx8p.message(p))

# this 
def rp():
  """
  returns a randomized JX8P patch object
  """
  p = jx8p.Patch()
  for param in p.parameters:
    param.value = random.randint(0,128)
  return p

def rsyx(dirpath):
  filepaths=os.listdir(dirpath)
  syxfiles=[s for s in filepaths if "SYX" in s]
  return dirpath + '\\' + random.choice(syxfiles)

def print_incoming(input_port):
  while True:
    m=input_port.receive()
    print m

import os, random
def rsyx(dirpath):
  filepaths=os.listdir(dirpath)
  syxfiles=[s for s in filepaths if "SYX" in s]
  return dirpath + '\\' + random.choice(syxfiles)

def rcclerp():
  my_sysex_dir = r"C:\Users\Dylan\Downloads\jx8p.syx\jcb"
  p1=jx8p.Patch(rsyx(my_sysex_dir))
  p2=jx8p.Patch(rsyx(my_sysex_dir))
  cclerp(jx8p.Patch(rsyx(my_sysex_dir)),jx8p.Patch(rsyx(my_sysex_dir)))

def cclerp(patch1, patch2):
  while True:
    m = mi.receive() # `mi` is a mido input port
    print m
    if m.type == 'control_change':
      p=jx8p.lerp2(patch1, patch2, m.value)
      mo.send(jx8p.message(p))

# p1 = jx8p.Patch()
# p2 = jx8p.Patch()

# create patch with all parameters as 127
# for p in p1.parameters:
#   p.value=127

# create patch with all parameters as 0
# for p in p2.parameters:
#   p.value=0

# testing the linear interpolation function
# for i in range(0,128):
#   [p.value for p in jx8p.lerp2(p1,p2,i).parameters][0]
