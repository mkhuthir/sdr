"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt

class blk(gr.sync_block): # other base classes are basic_block, decim_block, interp_block
    def __init__(self, sample_rate=800, wpm=20): # only default arguments here
        """Accepts morse code signal and emits decoded charcters
        Sample rate: Morse signal sample rate in Hz, default is 800Hz
        WPM: Words per minute, default is 20
        """
        gr.sync_block.__init__(
            self,
            name='Morse Decoder GUI',
            in_sig=[np.float32],
            out_sig=None
        )
        self.sample_rate = sample_rate
        self.wpm = wpm
        
        # Register a message output port for text strings
        self.message_port_register_out(gr.pmt.mp("text_out"))
        
        # Morse timing variables
        self.dit_len = int((1.2 / self.wpm) * self.sample_rate)
        self.max_dit = int(self.dit_len * 2.0)
        self.min_space = int(self.dit_len * 2.0)
        self.min_word = int(self.dit_len * 5.0)

        # State tracking
        self.current_state = 0
        self.state_duration = 0
        self.current_char = ""

        self.morse_dict = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2', '...--': '3',
            '....-': '4', '.....': '5', '-....': '6', '--...': '7', '---..': '8',
            '----.': '9', '.-.-.-': '.', '--..--': ',', '..--..': '?', '-....-': '-'
        }
        

    def emit_string(self, text):
        """Broadcast text via PMT message."""
        # Convert standard Python string to a GNU Radio PMT object and publish it
        pmt_msg = pmt.string_to_symbol(text)
        self.message_port_pub(pmt.mp("text_out"), pmt_msg)

    def decode_element(self):
        """Translates accumulated dits/dahs into a character."""
        if self.current_char:
            char = self.morse_dict.get(self.current_char, '[?]')
            self.emit_string(char)
            self.current_char = ""

    def work(self, input_items, output_items):
        in0 = input_items[0]
        
        for sample in in0:
            sample_state = 1 if sample > 0.5 else 0
            
            if sample_state == self.current_state:
                self.state_duration += 1
                
                # Check for word space timeout
                if self.current_state == 0 and self.state_duration > self.min_word:
                    if self.current_char:
                        self.decode_element()
                        self.emit_string(" ")
                    self.state_duration = 0 
            else:
                if self.current_state == 1:
                    if self.state_duration < self.max_dit:
                        self.current_char += "."
                    else:
                        self.current_char += "-"
                else:
                    if self.state_duration >= self.min_space:
                        self.decode_element()
                
                self.current_state = sample_state
                self.state_duration = 1
                
        return len(in0)

