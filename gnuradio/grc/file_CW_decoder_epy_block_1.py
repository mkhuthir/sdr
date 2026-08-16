import numpy as np
from gnuradio import gr
import pmt
from PyQt5 import QtWidgets, QtCore  # Placed at the top as requested

class text_receiver_block(gr.basic_block):
    def __init__(self, gui_hint=""):
        gr.basic_block.__init__(
            self,
            name='Simple GUI Display',
            in_sig=None,
            out_sig=None
        )
        self.gui_hint = gui_hint

        # Register gray message input port
        port_name = pmt.intern("text_in")
        self.message_port_register_in(port_name)
        self.set_msg_handler(port_name, self.handle_msg)

        # Baseline text variable
        self.current_text = "Waiting for data..."

        # CRITICAL HOOK: Leave this empty during GRC's background parsing thread.
        # GNU Radio's internal canvas layouts can safely evaluate a None object.
        self.qwidget = None

    def start(self):
        """
        Executed by the GNU Radio app engine ONLY when you hit 'Run'.
        At this point, a live Qt layout exists and widgets can spawn safely.
        """
        # Instantiate the label block natively at execution runtime
        self.qwidget = QtWidgets.QLabel(self.current_text)
        self.qwidget.setAlignment(QtCore.Qt.AlignCenter)
        
        return gr.basic_block.start(self)

    def handle_msg(self, msg):
        """
        Receives incoming messages on the message thread and updates the GUI label safely.
        """
        # Convert incoming data to a plain text string
        text_str = pmt.symbol_to_string(msg) if pmt.is_symbol(msg) else str(pmt.to_python(msg))

        # Direct safe thread injection back to the displayed window label
        if self.qwidget is not None:
            QtCore.QMetaObject.invokeMethod(
                self.qwidget, 
                "setText", 
                QtCore.Qt.QueuedConnection, 
                QtCore.Q_ARG(str, text_str)
            )

    def general_work(self, input_items, output_items):
        return 0
