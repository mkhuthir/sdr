#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: FIR Filter types
# Author: Muthanna Alwahash
# Copyright: (c) 2026
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import sip
import threading



class FIR_types(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "FIR Filter types", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("FIR Filter types")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "FIR_types")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.transition = transition = 1000
        self.sps = sps = 2
        self.samp_rate = samp_rate = 32000
        self.cutoff_low = cutoff_low = 6000
        self.cutoff_high = cutoff_high = 10000
        self.bp_low = bp_low = 6000
        self.bp_high = bp_high = 10000
        self.sym_rate = sym_rate = samp_rate/sps
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(1.0, samp_rate,samp_rate/sps, 0.35, (11*sps))
        self.lp_taps = lp_taps = firdes.low_pass(1.0, samp_rate, cutoff_high, transition, window.WIN_HAMMING, 6.76)
        self.hp_taps = hp_taps = firdes.high_pass(1.0, samp_rate, cutoff_low,transition, window.WIN_HAMMING, 6.76)
        self.br_taps = br_taps = firdes.band_reject(1.0, samp_rate, bp_low,bp_high, transition, window.WIN_HAMMING, 6.76)
        self.bp_taps = bp_taps = firdes.band_pass(1.0, samp_rate, bp_low, bp_high, transition, window.WIN_HAMMING, 6.76)

        ##################################################
        # Blocks
        ##################################################

        self.rrc_filter = filter.fir_filter_fff(1, rrc_taps)
        self.rrc_filter.declare_sample_delay(0)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_f(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            5,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(0.1)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_0.set_plot_pos_half(not False)

        labels = ['Low-pass', 'High-pass', 'Band-pass', 'Band-reject', 'RRC',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "magenta",
            "dark green", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [0.9, 0.9, 0.9, 0.9, 0.9,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(5):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.lp_filter = filter.fir_filter_fff(1, lp_taps)
        self.lp_filter.declare_sample_delay(0)
        self.hp_filter = filter.fir_filter_fff(1, hp_taps)
        self.hp_filter.declare_sample_delay(0)
        self.br_filter = filter.fir_filter_fff(1, br_taps)
        self.br_filter.declare_sample_delay(0)
        self.bp_filter = filter.fir_filter_fff(1, bp_taps)
        self.bp_filter.declare_sample_delay(0)
        self.analog_fastnoise_source_x_0 = analog.fastnoise_source_f(analog.GR_GAUSSIAN, 1, 0, 8192)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.bp_filter, 0))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.br_filter, 0))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.hp_filter, 0))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.lp_filter, 0))
        self.connect((self.analog_fastnoise_source_x_0, 0), (self.rrc_filter, 0))
        self.connect((self.bp_filter, 0), (self.qtgui_freq_sink_x_0, 2))
        self.connect((self.br_filter, 0), (self.qtgui_freq_sink_x_0, 3))
        self.connect((self.hp_filter, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.lp_filter, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.rrc_filter, 0), (self.qtgui_freq_sink_x_0, 4))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "FIR_types")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_transition(self):
        return self.transition

    def set_transition(self, transition):
        self.transition = transition
        self.set_bp_taps(firdes.band_pass(1.0, self.samp_rate, self.bp_low, self.bp_high, self.transition, window.WIN_HAMMING, 6.76))
        self.set_br_taps(firdes.band_reject(1.0, self.samp_rate, self.bp_low, self.bp_high, self.transition, window.WIN_HAMMING, 6.76))
        self.set_hp_taps(firdes.high_pass(1.0, self.samp_rate, self.cutoff_low, self.transition, window.WIN_HAMMING, 6.76))
        self.set_lp_taps(firdes.low_pass(1.0, self.samp_rate, self.cutoff_high, self.transition, window.WIN_HAMMING, 6.76))

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_rrc_taps(firdes.root_raised_cosine(1.0, self.samp_rate, self.samp_rate/self.sps, 0.35, (11*self.sps)))
        self.set_sym_rate(self.samp_rate/self.sps)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_bp_taps(firdes.band_pass(1.0, self.samp_rate, self.bp_low, self.bp_high, self.transition, window.WIN_HAMMING, 6.76))
        self.set_br_taps(firdes.band_reject(1.0, self.samp_rate, self.bp_low, self.bp_high, self.transition, window.WIN_HAMMING, 6.76))
        self.set_hp_taps(firdes.high_pass(1.0, self.samp_rate, self.cutoff_low, self.transition, window.WIN_HAMMING, 6.76))
        self.set_lp_taps(firdes.low_pass(1.0, self.samp_rate, self.cutoff_high, self.transition, window.WIN_HAMMING, 6.76))
        self.set_rrc_taps(firdes.root_raised_cosine(1.0, self.samp_rate, self.samp_rate/self.sps, 0.35, (11*self.sps)))
        self.set_sym_rate(self.samp_rate/self.sps)
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_cutoff_low(self):
        return self.cutoff_low

    def set_cutoff_low(self, cutoff_low):
        self.cutoff_low = cutoff_low
        self.set_hp_taps(firdes.high_pass(1.0, self.samp_rate, self.cutoff_low, self.transition, window.WIN_HAMMING, 6.76))

    def get_cutoff_high(self):
        return self.cutoff_high

    def set_cutoff_high(self, cutoff_high):
        self.cutoff_high = cutoff_high
        self.set_lp_taps(firdes.low_pass(1.0, self.samp_rate, self.cutoff_high, self.transition, window.WIN_HAMMING, 6.76))

    def get_bp_low(self):
        return self.bp_low

    def set_bp_low(self, bp_low):
        self.bp_low = bp_low
        self.set_bp_taps(firdes.band_pass(1.0, self.samp_rate, self.bp_low, self.bp_high, self.transition, window.WIN_HAMMING, 6.76))
        self.set_br_taps(firdes.band_reject(1.0, self.samp_rate, self.bp_low, self.bp_high, self.transition, window.WIN_HAMMING, 6.76))

    def get_bp_high(self):
        return self.bp_high

    def set_bp_high(self, bp_high):
        self.bp_high = bp_high
        self.set_bp_taps(firdes.band_pass(1.0, self.samp_rate, self.bp_low, self.bp_high, self.transition, window.WIN_HAMMING, 6.76))
        self.set_br_taps(firdes.band_reject(1.0, self.samp_rate, self.bp_low, self.bp_high, self.transition, window.WIN_HAMMING, 6.76))

    def get_sym_rate(self):
        return self.sym_rate

    def set_sym_rate(self, sym_rate):
        self.sym_rate = sym_rate

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.rrc_filter.set_taps(self.rrc_taps)

    def get_lp_taps(self):
        return self.lp_taps

    def set_lp_taps(self, lp_taps):
        self.lp_taps = lp_taps
        self.lp_filter.set_taps(self.lp_taps)

    def get_hp_taps(self):
        return self.hp_taps

    def set_hp_taps(self, hp_taps):
        self.hp_taps = hp_taps
        self.hp_filter.set_taps(self.hp_taps)

    def get_br_taps(self):
        return self.br_taps

    def set_br_taps(self, br_taps):
        self.br_taps = br_taps
        self.br_filter.set_taps(self.br_taps)

    def get_bp_taps(self):
        return self.bp_taps

    def set_bp_taps(self, bp_taps):
        self.bp_taps = bp_taps
        self.bp_filter.set_taps(self.bp_taps)




def main(top_block_cls=FIR_types, options=None):

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
