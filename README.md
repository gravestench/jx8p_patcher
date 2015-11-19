# jx8p_patcher
A patch generation and manipulation utility for the Roland JX-8P

I use mido and pygame, and you'll see me using it in the example file.

For some reason, portmidi acts strange in my environment and I can only get mido to open ports after I do a `pygame.midi.init()`

Anyways, if you know what you're doing, any midi backend which can send sysex bulk dumps should work.
