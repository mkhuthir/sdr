#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: NFM_rcv
# Author: Barry Duggan
# Description: NB FM receiver
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
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
from gnuradio import limesuiteng
import sip
import threading



class NFM_rcv(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "NFM_rcv", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("NFM_rcv")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "NFM_rcv")

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
        self.samp_rate_audio_sink = samp_rate_audio_sink = 48000
        self.samp_rate = samp_rate = 2e6
        self.LO_freq = LO_freq = 155.321
        self.volume = volume = 0.05
        self.sq_lvl = sq_lvl = -50
        self.samp_rate_audio_band = samp_rate_audio_band = int(samp_rate_audio_sink*5)
        self.gain = gain = 25
        self.freq_tune = freq_tune = LO_freq*1e6
        self.channel_filter = channel_filter = firdes.complex_band_pass(1.0, samp_rate, -3000, 3000, 200, window.WIN_HAMMING, 6.76)

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(0, 1.00, 0.05, 0.05, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._volume_win, 1, 0, 1, 50)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 50):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._sq_lvl_range = qtgui.Range(-100, 0, 5, -50, 200)
        self._sq_lvl_win = qtgui.RangeWidget(self._sq_lvl_range, self.set_sq_lvl, "Squelch", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._sq_lvl_win, 3, 0, 1, 50)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 50):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._gain_range = qtgui.Range(0, 49.6, 1, 25, 200)
        self._gain_win = qtgui.RangeWidget(self._gain_range, self.set_gain, "RF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._gain_win, 2, 0, 1, 50)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 50):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._LO_freq_range = qtgui.Range(100, 200, 0.1, 155.321, 200)
        self._LO_freq_win = qtgui.RangeWidget(self._LO_freq_range, self.set_LO_freq, "LO Freq.", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._LO_freq_win, 0, 0, 1, 50)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 50):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq_tune, #fc
            samp_rate_audio_band, #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(False)

        self.qtgui_waterfall_sink_x_0.disable_legend()


        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-180, -10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 10, 2, 4, 48)
        for r in range(10, 14):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 50):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq_tune, #fc
            samp_rate_audio_band, #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-180), (-10))
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)

        self.qtgui_freq_sink_x_0.disable_legend()


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 4, 0, 6, 50)
        for r in range(4, 10):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 50):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.limesuiteng_sdrdevice_source_0 = limesuiteng.sdrdevice_source('', '', 0, [0], "complex32f_t", "complex16_t", samp_rate, 0)
        self.limesuiteng_sdrdevice_source_0.set_lo_frequency(LO_freq*1e6)
        self.limesuiteng_sdrdevice_source_0.set_gfir_bandwidth(0)
        self.limesuiteng_sdrdevice_source_0.set_antenna('auto')
        if 0 == 1:
          self.limesuiteng_sdrdevice_source_0.set_gain(0, 30+0)
          self.limesuiteng_sdrdevice_source_0.set_gain(2, 0)
          self.limesuiteng_sdrdevice_source_0.set_gain(3, 12+-3)
        else:
          self.limesuiteng_sdrdevice_source_0.set_gain_generic(gain)
        self.limesuiteng_sdrdevice_source_0.set_nco_frequency(0)
        self.limesuiteng_sdrdevice_source_0.set_lpf_bandwidth(20e6) # Rx LPF range depends on TIA gain
        self.limesuiteng_sdrdevice_source_0.set_calibration_enable(1)
        self.fft_filter_xxx_0_0 = filter.fft_filter_ccc((int(samp_rate/samp_rate_audio_band)), channel_filter, 1)
        self.fft_filter_xxx_0_0.declare_sample_delay(0)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(volume)
        self.audio_sink_0 = audio.sink(48000, '', False)
        self.analog_simple_squelch_cc_0 = analog.simple_squelch_cc(sq_lvl, 1)
        self.analog_nbfm_rx_0 = analog.nbfm_rx(
        	audio_rate=samp_rate_audio_sink,
        	quad_rate=samp_rate_audio_band,
        	tau=(75e-6),
        	max_dev=5e3,
          )


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_nbfm_rx_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.analog_simple_squelch_cc_0, 0), (self.analog_nbfm_rx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.audio_sink_0, 0))
        self.connect((self.fft_filter_xxx_0_0, 0), (self.analog_simple_squelch_cc_0, 0))
        self.connect((self.fft_filter_xxx_0_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.fft_filter_xxx_0_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.limesuiteng_sdrdevice_source_0, 0), (self.fft_filter_xxx_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "NFM_rcv")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate_audio_sink(self):
        return self.samp_rate_audio_sink

    def set_samp_rate_audio_sink(self, samp_rate_audio_sink):
        self.samp_rate_audio_sink = samp_rate_audio_sink
        self.set_samp_rate_audio_band(int(self.samp_rate_audio_sink*5))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_channel_filter(firdes.complex_band_pass(1.0, self.samp_rate, -3000, 3000, 200, window.WIN_HAMMING, 6.76))

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        self.set_freq_tune(self.LO_freq*1e6)
        self.limesuiteng_sdrdevice_source_0.set_lo_frequency(self.LO_freq*1e6)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_0_0.set_k(self.volume)

    def get_sq_lvl(self):
        return self.sq_lvl

    def set_sq_lvl(self, sq_lvl):
        self.sq_lvl = sq_lvl
        self.analog_simple_squelch_cc_0.set_threshold(self.sq_lvl)

    def get_samp_rate_audio_band(self):
        return self.samp_rate_audio_band

    def set_samp_rate_audio_band(self, samp_rate_audio_band):
        self.samp_rate_audio_band = samp_rate_audio_band
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_tune, self.samp_rate_audio_band)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.freq_tune, self.samp_rate_audio_band)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.limesuiteng_sdrdevice_source_0.set_gain_generic(self.gain)

    def get_freq_tune(self):
        return self.freq_tune

    def set_freq_tune(self, freq_tune):
        self.freq_tune = freq_tune
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_tune, self.samp_rate_audio_band)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.freq_tune, self.samp_rate_audio_band)

    def get_channel_filter(self):
        return self.channel_filter

    def set_channel_filter(self, channel_filter):
        self.channel_filter = channel_filter
        self.fft_filter_xxx_0_0.set_taps(self.channel_filter)




def main(top_block_cls=NFM_rcv, options=None):

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
