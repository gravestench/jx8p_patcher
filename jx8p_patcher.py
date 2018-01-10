"""
AUTHOR: Dylan Knuth
DATE: 2015

This is a patch management utility for the Roland JX-8P Analog Polyphonic Synthesizer.

This module is only meant for reading, manipulating, and creating SYSEX files for the JX-8P.

This script does NOT attempt to connect to your midi interfaces. However, mido can do that if you want.

I mainly created this program to implement patch interpolation (morphing from one patch to another),
as well as a patch randomizer.
"""

import mido

class Patch:
  """
  This class represents a synthesizer patch, and you can pass this bastard a
  a .syx file path when you instantiate it. you can do all kinds of cool shit
  with it from here.

  If you dont pass a file, it will create a blank patch which has no parameter\
  values (meaning that you can't use it to send patches from).
  """
  
  def __init__(self, sysex_definition_path=None, sysex_file_path=None):
    """
    Initialize blank (empty) patch state

    we will load a sysex file if the sysex_file_path is passed

    The parameter implementation is super ugly, and i have lots of copypasta
    I'd like to re-implement the way that 
    """
    self.load_sysex_definition(sysex_definition_path)

    if sysex_file_path != None:
      self.load_file(sysex_file_path)

  def load_file(self, jx8p_sysex_file_path=None, dbg=False):
    """
    Given a path to a .syx file, this function will parse and return a patch object
    """
    print 'loading', jx8p_sysex_file_path
    
    if jx8p_sysex_file_path==None:
      print('give me a patch, dummy.')
      return 1
    syx = mido.read_syx_file(jx8p_sysex_file_path)[0].bytes() # yields an array of bytes
    
    if syx[0] != 0xF0:
      print 'INVALID SYX: MALFORMED HEADER'
    if syx[1] != self.MANUFACTURER_ID:
      print 'INVALID SYX: MANUFACTURER_ID NOT PRESENT'
    
    # PROCESS AS `PROGRAM` MESSAGE
    if syx[2] == 0x34:
      print 'SYSEX JX8P `PROGRAM` OPCODE NOT YET IMPLEMENTED'
    
    # PROCESS AS `ALL-PARAMETERS` MESSAGE
    #   APR messages are 67 bytes in total
    #   (there may be more messages in the syx file, i havent dealt with that yet)
    if syx[2] == 0x35 and len(syx) == 67:
      print 'PROCESSING APR MESSAGE'
      # The sysex header is 7 bytes long
      # the parameters follow the header, in sequential order
      parameter_values = syx[7:-1]
      index=0
      while (index<len(parameter_values)):
        if self.parameters[index] != None: # some parameters are undefined
          self.parameters[index].value = parameter_values[index]
        index+=1
    
    # PROCESS AS `INDIVIDUAL-PARAMETERS` MESSAGE
    # `IPR` messages are used when 1 or several parameters, but not all, are changed.
    # However, this message type could send all parameters, but i think it's purpose 
    # was to reduce traffic on the midi ports. Instead of parameter data coming 
    # sequentially (as the `APR` message does), the parameters are represented as 
    # pairs of bytes, where the first byte says which parameter and the second byte
    # is the data associated with the parameter
    #
    # I plan on making real-time interpolation smarter by only sending parameters which 
    # have been changed since the last step, instead of sending all parameters every single step
    if syx[2] == 0x36:
      print 'SYSEX JX8P `INDIVIDUAL PARAMETERS` OPCODE NOT YET IMPLEMENTED'
    
    if syx[-1] != 0xF7:
      print 'INVALID SYX: MALFORMED TAIL'

    if dbg==True:
      self.info()
    return self

def load_sysex_definition(self, sysex_definition_path=None, dbg=False):
    """
    Given a path to a text file containing definition of sysex parameters, populate the Patch object with the sysex definition
    """

    print 'using', sysex_definition_path, 'sysex definition file'

    if sysex_definition_path==None:
        print('without your help, I do not understand sysex!')
        return 1

    with(f=open(sysex_definition_path)):
        f_lines = f.readlines()

        self.MANUFACTURER_ID = None
        self.PATCH_PARAMETER_COUNT = None
        self.parameters = [[None]]*self.PATCH_PARAMETER_COUNT

        for line in f_lines:
            if line.startswith('MANUFACTURER_ID='):
                line.strip(' ')
                line.strip('\n')
                self.MANUFACTURER_ID = int(line[16:])

            elif line.startswith('PATCH_PARAMETER_COUNT='):
                line.strip(' ')
                line.strip('\n')
                self.PATCH_PARAMETER_COUNT = int(line[22:])

            elif line.startswith('{'):
                line.strip('\n')

                PARAM_NUMBER = int(line[1:5])
                line = line[6:]

                line_array = line.split('[')

                PARAM_NAME = line_array[0].strip("'")
                PARAM_NAME = PARAM_NAME[:-1]

                line_array[1] = line_array[1].split(']')
                PARAM_DEFAULT = line_array[1][1].strip("'")
                PARAM_DEFAULT = PARAM_DEFAULT[1:]
                if not PARAM_DEFAULT.isdigit():
                    PARAM_DEFAULT = ord(PARAM_DEFAULT)

                LIMIT_ARRAY = line_array[1][0].split(")")
                for value in LIMIT_ARRAY:
                    value = value[1:]
                    value = value.strip("(")
                    value = value.split(",")
                    value[0] = int(value[0])

                    value = Parameter_state(value[0], value[1])

                self.parameters[PARAM_NUMBER] = Parameter(PARAM_NAME, LIMIT_ARRAY, PARAM_DEFAULT)
    if dbg == True:
        print self.parameters
  
  def name(self):
    """
    Returns the patch name as a string (taken from parameters 0-9) 
    """
    return ''.join(chr(b) for b in self.bytes()[0:9])

  def info(self):
    """
    Prints a human-readable version of the patch parameters.

    Parameters with states that represent something other than an integer
    will print a friendly version of the parameter state.
    
    For instance, if DCO-1 waveform `Sawtooth` will be printed instead of `47`
    """
    
    # EXAMPLE:
    #
    # >>> p2=jx8p.Patch(r".\jx8p.syx\jcb\celeste1.syx")
    # loading C:\jx8p.syx\jcb\celeste1.syx
    # PROCESSING APR MESSAGE
    #
    # >>> p2.info()
    #
    # PATCH NAME: CELESTE 1
    # DCO-1 RANGE --> 4'
    # DCO-1 WAVEFORM --> Sawtooth
    # DCO-1 TUNE --> -12 Semitone
    # DCO-1 LFO MOD DEPTH --> 2
    # DCO-1 ENV MOD DEPTH --> 0
    # DCO-2 RANGE --> 2'
    # DCO-2 WAVEFORM --> Sawtooth
    # DCO-2 CROSSMOD --> OFF
    # DCO-2 TUNE --> -5 Semitone
    # DCO-2 FINE TUNE --> +0
    # DCO-2 LFO MOD DEPTH --> 0
    # DCO-2 ENV MOD DEPTH --> 0
    # DCO DYNAMICS --> Off
    # DCO ENV MODE --> ENV-2 NORMAL
    # MIXER DCO-1 --> 32
    # MIXER DCO-2 --> 0
    # MIXER ENV MOD DEPTH --> 127
    # MIXER DYNAMICS --> 1
    # MIXER ENV MODE --> ENV-1 NORMAL
    # HPF CUTOFF FREQ --> 0
    # VCF CUTTOF FREQ --> 51
    # VCF RESONANCE --> 0
    # VCF LFO MOD DEPTH --> 0
    # VCF ENV MOD DEPTH --> 28
    # VCF KEY FOLLOW --> 119
    # VCF DYNAMICS --> 1
    # VCF ENV MODE --> ENV-1 NORMAL
    # VCA LEVEL --> 125
    # VCA DYNAMICS --> 1
    # CHORUS --> 2
    # LFO WAVEFORM --> TRIANGLE
    # LFO DELAY TIME --> 2
    # LFO RATE --> 97
    # ENV-1 ATTACK --> 0
    # ENV-1 DECAY --> 22
    # ENV-1 SUSTAIN --> 0
    # ENV-1 RELEASE --> 69
    # ENV-1 KEY FOLLOW --> 1
    # ENV-2 ATTACK --> 30
    # ENV-2 DECAY --> 69
    # ENV-2 SUSTAIN --> 0
    # ENV-2 RELEASE --> 62
    # ENV-2 KEY FOLLOW --> 1
    # VCA ENV MODE --> ENV-2 NORMAL

    print '\nPATCH NAME:', ''.join(chr(b.value) for b in self.parameters[:10]) 
    for prm in self.parameters[11:]:
      if prm.states != []:
        # `parameter.get_state()` will return `[value, description]`
        # if the parmeter description is friendlier than `VALUE`, we will display
        # the friendly description, instead of an integer
        if prm.get_state()[1] == 'VALUE':
          print prm.name, '-->', prm.get_state()[0]
        else:
          print prm.name, '-->', prm.get_state()[1]

  def bytes(self):
    """
    Returns the parameter values as an array of bytes
    
    NOTE: This doesnt return a complete sysex message, just the parameter values
          You still need to prepend the sysex header, and append the sysex footer.
    """
    bytes=[]
    for p in self.parameters:
      v = p.value
      bytes.append(v)
    return bytes

class Parameter:
  """
  An object representing a single parameter for the Roland JX-8P.
  It has a name and another object which represents the states of the parameter.
  
  Many instances of this object will be created in the main `Patch` object, as an element 
  inside of a local variable called `parameters`.
  """
  name=None
  states=None
  value=None

  def __init__(self, name=None, states=[], value=None):
    self.name = name
    self.states = states
    self.value = value

  def get_state(self):
    if self.value == None:
      return None
    for state in self.states:
      if self.value <= state.upper_bound:
        return [self.value, state.description]

class Parameter_state:
  """
  An object which represents the various states for a JX-8P parameter.
  A single parameter can have many states (such as waveform type).

  Each parameter state has an upper bound associated with a state name.
  
  For instance, DCO-1 Waveform can be one of 4 waveforms.
  If a value between 0 and 31 is applied to this parameter, then DCO-1
  Waveform will be set to `Noise`. The states are assumed to be in ascending
  order with respect to the upper bound.
  """
  upper_bound = None
  description = None
  def __init__(self, upper=127, desc='Value'):
    self.upper_bound = upper
    self.description = desc

def lerp2(p1, p2, step=0):
  """
  Given two patche abjects and an integer 0-127, this will return a patch interpolation
  jx8p.lerp2(p1, p2, 0) --> p1
  jx8p.lerp2(p1, p2, 127) --> p2

  max interpolation steps is assumed to be 127, since we're doing midi stuff and all data bytes are < 128
  """
  p=Patch()
  scale = step/float(127)
  for index in range(0,len(p1.parameters)):
    # pdb.set_trace()
    if p.parameters[index] != None: # if the parameter is not undefined
      lerp_vals=[p1.parameters[index].value, p2.parameters[index].value]
      difference = lerp_vals[0]-lerp_vals[1]
      p.parameters[index].value = int(round(((1-scale)*lerp_vals[0]) + (scale*lerp_vals[1])))


  return p

def message(p1):
  """
  This function will use the `mido` python midi module
  to generate a midi message (which can later be sent to a `mido` midi output)
  """
  sysex=[0xf0]
  sysex.extend([0x41, 0x35, 0x00, 0x21, 0x20, 0x01])
  sysex.extend(p1.bytes())
  sysex.extend([0xf7])
  return mido.parse_all(sysex)[0]


  if __name__ == '__main__':
    print 's\'all good, homie.'