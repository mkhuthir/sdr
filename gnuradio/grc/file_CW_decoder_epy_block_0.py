"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr

# Changed to gr.basic_block to handle mismatched input and output rates
class blk(gr.basic_block): 
    def __init__(self, sample_rate=800, wpm=20):
        """Accepts morse code signal and emits decoded streaming bytes (Integer 8)"""
        gr.basic_block.__init__(
            self,
            name='Morse Decoder GUI',
            in_sig=[np.float32],
            out_sig=[np.int8]  # FIX: Set to np.int8 to turn your output port PURPLE
        )
        self.sample_rate = sample_rate
        self.wpm = wpm
        
        # Morse timing variables
        self.dit_len = int((1.2 / self.wpm) * self.sample_rate)
        self.max_dit = int(self.dit_len * 2.0)
        self.min_space = int(self.dit_len * 2.0)
        self.min_word = int(self.dit_len * 5.0)

        # State tracking
        self.current_state = 0
        self.state_duration = 0
        self.current_char = ""
        self.output_queue = []  # Buffer to store decoded characters before outputting

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

    def decode_element(self):
        """Translates accumulated dits/dahs into a character byte."""
        if self.current_char:
            char = self.morse_dict.get(self.current_char, '*')
            self.output_queue.append(ord(char))
            self.current_char = ""

    def general_work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]
        
        # 1. Process all incoming high-speed audio samples
        for sample in in0:
            sample_state = 1 if sample > 0.5 else 0
            
            if sample_state == self.current_state:
                self.state_duration += 1
                
                # Check for word space timeout
                if self.current_state == 0 and self.state_duration == self.min_word:
                    if self.current_char:
                        self.decode_element()
                    self.output_queue.append(ord(" "))
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

        # 2. Tell the scheduler how many input samples we processed
        self.consume(0, len(in0))

        # 3. Write decoded text bytes out to the purple port buffer
        n_output = min(len(out0), len(self.output_queue))
        if n_output > 0:
            for i in range(n_output):
                out0[i] = self.output_queue.pop(0)
            return n_output
        else:
            return 0
