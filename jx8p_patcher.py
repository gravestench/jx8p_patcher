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
  This class represents a JX-8P patch, and you can pass this bastard a
  a .syx file path when you instantiate it. you can do all kinds of cool shit
  with it from here.

  If you dont pass a file, it will create a blank patch which has no parameter\
  values (meaning that you can't use it to send patches from).
  """
  
  def __init__(self, jx8p_sysex_file_path=None):
    """
    Initialize blank (empty) patch state

    we will load a sysex file if the filepath is passed

    The parameter implementation is super ugly, and i have lots of copypasta
    I'd like to re-implement the way that 
    """
    self.PATCH_PARAMETER_COUNT=59
    self.SYSEX_ROLAND_ID = 0x41
    self.parameters = [[None]]*self.PATCH_PARAMETER_COUNT

    # The patch parameters come straight from the manual
    # even the undefined parameters are here. I may be able to store values there, even if
    # The JX-8P doesn't do anything with them (which could be handy for storing bitmasks
    # which identify which parameters should or should not be altered during
    # patch interpolation or patch randomization/mutation, or even step-sequencer/arpeggiator
    # step values). I'll play with this later and see if it works.
    #
    # The following just declares parameters without values. you can load a .syx file later,
    # or you can set values explicitly by doing something like:
    #
    #     for parameter in patch.parameters:
    #       parameter.value = x
    #
    # I know, I know, this code is fucking ugly as balls. I'll change it later.
    # Parameter 20 is the fucking worst...
    self.parameters[0] = Parameter('Character 1', [Parameter_state(127,'ASCII'), ord('B')])
    self.parameters[1] = Parameter('Character 2', [Parameter_state(127,'ASCII'), ord('L')])
    self.parameters[2] = Parameter('Character 3', [Parameter_state(127,'ASCII'), ord('A')])
    self.parameters[3] = Parameter('Character 4', [Parameter_state(127,'ASCII'), ord('N')])
    self.parameters[4] = Parameter('Character 5', [Parameter_state(127,'ASCII'), ord('K')])
    self.parameters[5] = Parameter('Character 6', [Parameter_state(127,'ASCII'), ord('P')])
    self.parameters[6] = Parameter('Character 7', [Parameter_state(127,'ASCII'), ord('A')])
    self.parameters[7] = Parameter('Character 8', [Parameter_state(127,'ASCII'), ord('T')])
    self.parameters[8] = Parameter('Character 9', [Parameter_state(127,'ASCII'), ord('C')])
    self.parameters[9] = Parameter('Character 10', [Parameter_state(127,'ASCII'), ord('H')])
  
    self.parameters[10] = Parameter() # NOT DEFINED

    self.parameters[11] = Parameter('DCO-1 RANGE', [Parameter_state(31,'16\''),Parameter_state(63,'8\''),Parameter_state(95,'4\''),Parameter_state(127,'2\'')])
    self.parameters[12] = Parameter('DCO-1 WAVEFORM', [Parameter_state(31,'Noise'),Parameter_state(63,'Sawtooth'),Parameter_state(95,'Pulse'),Parameter_state(127,'Square')])
    self.parameters[13] = Parameter('DCO-1 TUNE', [Parameter_state(5,'-12 Semitone'),Parameter_state(10,'-11 Semitone'),Parameter_state(15,'-10 Semitone'),Parameter_state(20,'-9 Semitone'),Parameter_state(25,'-8 Semitone'),Parameter_state(30,'-7 Semitone'),Parameter_state(35,'-6 Semitone'),Parameter_state(40,'-5 Semitone'),Parameter_state(45,'-4 Semitone'),Parameter_state(50,'-3 Semitone'),Parameter_state(55,'-2 Semitone'),Parameter_state(60,'-1 Semitone'),Parameter_state(66,'+0'),Parameter_state(71,'+1 Semitone'),Parameter_state(76,'+2 Semitone'),Parameter_state(81,'+3 Semitone'),Parameter_state(86,'+4 Semitone'),Parameter_state(91,'+5 Semitone'),Parameter_state(96,'+6 Semitone'),Parameter_state(101,'+7 Semitone'),Parameter_state(106,'+8 Semitone'),Parameter_state(111,'+9 Semitone'),Parameter_state(116,'+10 Semitone'),Parameter_state(121,'+11 Semitone'),Parameter_state(127,'+12 Semitone')])
    self.parameters[14] = Parameter('DCO-1 LFO MOD DEPTH', [Parameter_state(127, 'VALUE')])
    self.parameters[15] = Parameter('DCO-1 ENV MOD DEPTH', [Parameter_state(127, 'VALUE')])
  
    self.parameters[16] = Parameter('DCO-2 RANGE', [Parameter_state(31,'16\''),Parameter_state(63,'8\''),Parameter_state(95,'4\''),Parameter_state(127,'2\'')])
    self.parameters[17] = Parameter('DCO-2 WAVEFORM', [Parameter_state(31,'Noise'),Parameter_state(63,'Sawtooth'),Parameter_state(95,'Pulse'),Parameter_state(127,'Square')])
    self.parameters[18] = Parameter('DCO-2 CROSSMOD', [Parameter_state(31,'OFF'),Parameter_state(63,'Sync 1'),Parameter_state(95,'Sync 2'),Parameter_state(127,'XMOD')])
    self.parameters[19] = Parameter('DCO-2 TUNE', [Parameter_state(5,'-12 Semitone'),Parameter_state(10,'-11 Semitone'),Parameter_state(15,'-10 Semitone'),Parameter_state(20,'-9 Semitone'),Parameter_state(25,'-8 Semitone'),Parameter_state(30,'-7 Semitone'),Parameter_state(35,'-6 Semitone'),Parameter_state(40,'-5 Semitone'),Parameter_state(45,'-4 Semitone'),Parameter_state(50,'-3 Semitone'),Parameter_state(55,'-2 Semitone'),Parameter_state(60,'-1 Semitone'),Parameter_state(66,'+0'),Parameter_state(71,'+1 Semitone'),Parameter_state(76,'+2 Semitone'),Parameter_state(81,'+3 Semitone'),Parameter_state(86,'+4 Semitone'),Parameter_state(91,'+5 Semitone'),Parameter_state(96,'+6 Semitone'),Parameter_state(101,'+7 Semitone'),Parameter_state(106,'+8 Semitone'),Parameter_state(111,'+9 Semitone'),Parameter_state(116,'+10 Semitone'),Parameter_state(121,'+11 Semitone'),Parameter_state(127,'+12 Semitone')])
    self.parameters[20] = Parameter('DCO-2 FINE TUNE', [Parameter_state(1, '-50'), Parameter_state(2, '-49'), Parameter_state(3, '-48'), Parameter_state(5, '-47'), Parameter_state(6, '-46'), Parameter_state(7, '-45'), Parameter_state(8, '-44'), Parameter_state(10, '-43'), Parameter_state(11, '-42'), Parameter_state(12, '-41'), Parameter_state(13, '-40'), Parameter_state(15, '-39'), Parameter_state(16, '-38'), Parameter_state(17, '-37'), Parameter_state(18, '-36'), Parameter_state(20, '-35'), Parameter_state(21, '-34'), Parameter_state(22, '-33'), Parameter_state(23, '-32'), Parameter_state(25, '-31'), Parameter_state(26, '-30'), Parameter_state(27, '-29'), Parameter_state(28, '-28'), Parameter_state(30, '-27'), Parameter_state(31, '-26'), Parameter_state(32, '-25'), Parameter_state(33, '-24'), Parameter_state(35, '-23'), Parameter_state(36, '-22'), Parameter_state(37, '-21'), Parameter_state(38, '-20'), Parameter_state(40, '-19'), Parameter_state(41, '-18'), Parameter_state(42, '-17'), Parameter_state(44, '-16'), Parameter_state(45, '-15'), Parameter_state(46, '-14'), Parameter_state(47, '-13'), Parameter_state(49, '-12'), Parameter_state(50, '-11'), Parameter_state(51, '-10'), Parameter_state(52, '-9'), Parameter_state(54, '-8'), Parameter_state(55, '-7'), Parameter_state(56, '-6'), Parameter_state(57, '-5'), Parameter_state(59, '-4'), Parameter_state(60, '-3'), Parameter_state(61, '-2'), Parameter_state(62, '-1'), Parameter_state(64, '+0'), Parameter_state(65, '+1'), Parameter_state(66, '+2'), Parameter_state(67, '+3'), Parameter_state(69, '+4'), Parameter_state(70, '+5'), Parameter_state(71, '+6'), Parameter_state(72, '+7'), Parameter_state(73, '+8'), Parameter_state(74, '+8'), Parameter_state(75, '+9'), Parameter_state(76, '+10'), Parameter_state(77, '+11'), Parameter_state(79, '+12'), Parameter_state(80, '+13'), Parameter_state(81, '+14'), Parameter_state(82, '+15'), Parameter_state(84, '+16'), Parameter_state(85, '+17'), Parameter_state(86, '+18'), Parameter_state(88, '+19'), Parameter_state(89, '+20'), Parameter_state(90, '+21'), Parameter_state(91, '+22'), Parameter_state(93, '+23'), Parameter_state(94, '+24'), Parameter_state(95, '+25'), Parameter_state(96, '+26'), Parameter_state(98, '+27'), Parameter_state(99, '+28'), Parameter_state(100, '+29'), Parameter_state(101, '+30'), Parameter_state(103, '+31'), Parameter_state(104, '+32'), Parameter_state(105, '+33'), Parameter_state(106, '+34'), Parameter_state(108, '+35'), Parameter_state(109, '+36'), Parameter_state(110, '+37'), Parameter_state(111, '+38'), Parameter_state(113, '+39'), Parameter_state(114, '+40'), Parameter_state(115, '+41'), Parameter_state(116, '+42'), Parameter_state(118, '+43'), Parameter_state(119, '+44'), Parameter_state(120, '+45'), Parameter_state(121, '+46'), Parameter_state(123, '+47'), Parameter_state(124, '+48'), Parameter_state(125, '+49'), Parameter_state(127, '+50')])
    self.parameters[21] = Parameter('DCO-2 LFO MOD DEPTH', [Parameter_state(127, 'VALUE')])
    self.parameters[22] = Parameter('DCO-2 ENV MOD DEPTH', [Parameter_state(127, 'VALUE')])
    
    self.parameters[23] = Parameter() # NOT DEFINED
    self.parameters[24] = Parameter() # NOT DEFINED
    self.parameters[25] = Parameter() # NOT DEFINED
    
    self.parameters[26] = Parameter('DCO DYNAMICS', [Parameter_state(31,'Off'),Parameter_state(63,'1'),Parameter_state(95,'2'),Parameter_state(127,'3')])
    self.parameters[27] = Parameter('DCO ENV MODE', [Parameter_state(31,'ENV-2 INVERTED'),Parameter_state(63,'ENV-2 NORMAL'),Parameter_state(95,'ENV-1 INVERTED'),Parameter_state(127,'ENV-1 NORMAL')])
  
    self.parameters[28] = Parameter('MIXER DCO-1', [Parameter_state(127, 'VALUE')])
    self.parameters[29] = Parameter('MIXER DCO-2', [Parameter_state(127, 'VALUE')])
    self.parameters[30] = Parameter('MIXER ENV MOD DEPTH', [Parameter_state(127, 'VALUE')])
    self.parameters[31] = Parameter('MIXER DYNAMICS', [Parameter_state(31,'Off'),Parameter_state(63,'1'),Parameter_state(95,'2'),Parameter_state(127,'3')])
    self.parameters[32] = Parameter('MIXER ENV MODE', [Parameter_state(31,'ENV-2 INVERTED'),Parameter_state(63,'ENV-2 NORMAL'),Parameter_state(95,'ENV-1 INVERTED'),Parameter_state(127,'ENV-1 NORMAL')])
  
    self.parameters[33] = Parameter('HPF CUTOFF FREQ', [Parameter_state(31,'0'),Parameter_state(63,'1'),Parameter_state(95,'2'),Parameter_state(127,'3')])
    self.parameters[34] = Parameter('VCF CUTTOF FREQ', [Parameter_state(127, 'VALUE')])
    self.parameters[35] = Parameter('VCF RESONANCE', [Parameter_state(127, 'VALUE')])
    self.parameters[36] = Parameter('VCF LFO MOD DEPTH', [Parameter_state(127, 'VALUE')])
    self.parameters[37] = Parameter('VCF ENV MOD DEPTH', [Parameter_state(127, 'VALUE')])
    self.parameters[38] = Parameter('VCF KEY FOLLOW', [Parameter_state(127, 'VALUE')])
    self.parameters[39] = Parameter('VCF DYNAMICS', [Parameter_state(31,'Off'),Parameter_state(63,'1'),Parameter_state(95,'2'),Parameter_state(127,'3')])
    self.parameters[40] = Parameter('VCF ENV MODE', [Parameter_state(31,'ENV-2 INVERTED'),Parameter_state(63,'ENV-2 NORMAL'),Parameter_state(95,'ENV-1 INVERTED'),Parameter_state(127,'ENV-1 NORMAL')])
  
    self.parameters[41] = Parameter('VCA LEVEL', [Parameter_state(127, 'VALUE')])
    self.parameters[42] = Parameter('VCA DYNAMICS', [Parameter_state(31,'Off'),Parameter_state(63,'1'),Parameter_state(95,'2'),Parameter_state(127,'3')])
  
    self.parameters[43] = Parameter('CHORUS', [Parameter_state(31,'Off'),Parameter_state(63,'1'),Parameter_state(127,'2')])

    self.parameters[44] = Parameter('LFO WAVEFORM', [Parameter_state(31,'RANDOM'),Parameter_state(63,'SQUARE'),Parameter_state(127,'TRIANGLE')])
    self.parameters[45] = Parameter('LFO DELAY TIME', [Parameter_state(127, 'VALUE')])
    self.parameters[46] = Parameter('LFO RATE', [Parameter_state(127, 'VALUE')])

    self.parameters[47] = Parameter('ENV-1 ATTACK', [Parameter_state(127, 'VALUE')])
    self.parameters[48] = Parameter('ENV-1 DECAY', [Parameter_state(127, 'VALUE')])
    self.parameters[49] = Parameter('ENV-1 SUSTAIN', [Parameter_state(127, 'VALUE')])
    self.parameters[50] = Parameter('ENV-1 RELEASE', [Parameter_state(127, 'VALUE')])
    self.parameters[51] = Parameter('ENV-1 KEY FOLLOW', [Parameter_state(31,'OFF'),Parameter_state(63,'1'),Parameter_state(95,'2'),Parameter_state(127,'3')])
  
    self.parameters[52] = Parameter('ENV-2 ATTACK', [Parameter_state(127, 'VALUE')])
    self.parameters[53] = Parameter('ENV-2 DECAY', [Parameter_state(127, 'VALUE')])
    self.parameters[54] = Parameter('ENV-2 SUSTAIN', [Parameter_state(127, 'VALUE')])
    self.parameters[55] = Parameter('ENV-2 RELEASE', [Parameter_state(127, 'VALUE')])
    self.parameters[56] = Parameter('ENV-2 KEY FOLLOW', [Parameter_state(31,'OFF'),Parameter_state(63,'1'),Parameter_state(95,'2'),Parameter_state(127,'3')])
  
    self.parameters[57] = Parameter() # NOT DEFINED
  
    self.parameters[58] = Parameter('VCA ENV MODE', [Parameter_state(63,'GATE'),Parameter_state(127,'ENV-2 NORMAL')])

    if jx8p_sysex_file_path != None:
      self.load_file(jx8p_sysex_file_path)

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
    if syx[1] != self.SYSEX_ROLAND_ID:
      print 'INVALID SYX: ROLAND ID NOT PRESENT'
    
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
  if step == 0:
    return p1
  elif step == 127:
    return p2
  for index in range(0,len(p1.parameters)):
    # pdb.set_trace()
    if p.parameters[index] != None:
      lerp_vals=[p1.parameters[index].value, p2.parameters[index].value]
      p.parameters[index].value = int(step/float(128)*abs(lerp_vals[0]-lerp_vals[1])+min(lerp_vals)) # Transformation
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