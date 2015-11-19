import pygame, mido
from pygame import midi as midi
import random as rand
import os

# for some reason, mido can't connect in my environment unless
# i use pygame (to initialize portmidi...?)
midi.init()

# This is my midi controller, which has din-midi and usb-midi
# the jx8p is connected to this controller
mo=mido.open_output("Bitstream 3X")
mi=mido.open_input("Bitstream 3X")

# This is my jx8p patcher
import jx8p_patcher as jx8p

# I have a bunch of .syx files for the jx8p
# here is an example of loading a .syx file as a patch
p1=jx8p.Patch(r"C:\Users\Dylan\Downloads\jx8p.syx\jcb\dryrhodes.syx")
p2=jx8p.Patch(r"C:\Users\Dylan\Downloads\jx8p.syx\jcb\celeste1.syx")
# You send a patch to a mido output port like this:
# mo.send(jx8p.message(p))

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
    param.value = rand.randint(0,128)
  return p

def rsyx(dirpath):
  filepaths=os.listdir(dirpath)
  syxfiles=[s for s in filepaths if "SYX" in s]
  return dirpath + '\\' + rand.choice(syxfiles)

def print_incoming(input_port):
  while True:
    m=input_port.receive()
    print m
