#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: CW Decoder
# Author: Muthanna Alwahash
# Copyright: (c) 2026
# Description: CW Decoder
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import Qt
from gnuradio import qtgui
import display
import sip
from PyQt5 import QtCore
from gnuradio import analog
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
import file_CW_decoder_epy_block_0 as epy_block_0  # embedded python block
import threading
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation




class file_CW_decoder(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "CW Decoder", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("CW Decoder")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "file_CW_decoder")

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
        self.samp_rate_CW = samp_rate_CW = 800
        self.samp_rate = samp_rate = 125000
        self.tune_freq = tune_freq = 7047713
        self.thresh_low = thresh_low = 0.05
        self.thresh_high = thresh_high = 0.1
        self.sig_gain = sig_gain = 2
        self.fft_y_min = fft_y_min = -110
        self.fft_y_max = fft_y_max = -50
        self.fft_size = fft_size = 1024
        self.center_freq = center_freq = 7075e3
        self.CW_wpm = CW_wpm = 20
        self.CW_LPF = CW_LPF = firdes.low_pass(1.0, samp_rate, samp_rate_CW/2, 10e3, window.WIN_HAMMING, 6.76)
        self.AGC_gain = AGC_gain = 2

        ##################################################
        # Blocks
        ##################################################

        self._tune_freq_range = qtgui.Range(center_freq-samp_rate/2, center_freq+samp_rate/2, 1, 7047713, 10)
        self._tune_freq_win = qtgui.RangeWidget(self._tune_freq_range, self.set_tune_freq, "Tune Freq", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._tune_freq_win, 1, 150, 1, 50)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(150, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._thresh_low_range = qtgui.Range(0.00, 0.50, 0.01, 0.05, 10)
        self._thresh_low_win = qtgui.RangeWidget(self._thresh_low_range, self.set_thresh_low, "Threshold Low", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._thresh_low_win, 4, 150, 1, 50)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(150, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._thresh_high_range = qtgui.Range(0.02, 2, 0.01, 0.1, 10)
        self._thresh_high_win = qtgui.RangeWidget(self._thresh_high_range, self.set_thresh_high, "Threshold High", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._thresh_high_win, 5, 150, 1, 50)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(150, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._sig_gain_range = qtgui.Range(1, 100, 1, 2, 10)
        self._sig_gain_win = qtgui.RangeWidget(self._sig_gain_range, self.set_sig_gain, "Sig. Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._sig_gain_win, 2, 150, 1, 50)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(150, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._AGC_gain_range = qtgui.Range(1, 100, 1, 2, 10)
        self._AGC_gain_win = qtgui.RangeWidget(self._AGC_gain_range, self.set_AGC_gain, "AGC Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._AGC_gain_win, 3, 150, 1, 50)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(150, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.show_text_0 = display.show_text('Decoded Text', 225, 3)
        self._show_text_0_win = sip.wrapinstance(self.show_text_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._show_text_0_win, 8, 1, 1, 200)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 201):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=samp_rate_CW,
                decimation=samp_rate,
                taps=[],
                fractional_bw=0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_c(
            fft_size, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(True)
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

        self.qtgui_waterfall_sink_x_0.set_intensity_range(fft_y_min, fft_y_max)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 1, 8, 5, 142)
        for r in range(1, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(8, 150):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            (samp_rate_CW*2), #size
            samp_rate_CW, #samp_rate
            "CW Signal", #name
            4, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(0, 6)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal', 'Demod', 'Threshold High', 'Threshold Low', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'cyan', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(4):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 7, 0, 1, 200)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_c(
            (int(fft_size/4)), #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            tune_freq, #fc
            samp_rate_CW, #bw
            "Selected Signal", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0.set_y_axis(fft_y_min, fft_y_max)
        self.qtgui_freq_sink_x_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0.enable_grid(True)
        self.qtgui_freq_sink_x_0_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0_0.set_fft_window_normalized(False)

        self.qtgui_freq_sink_x_0_0.disable_legend()


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["green", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_win, 0, 150, 1, 50)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(150, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            fft_size, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            center_freq, #fc
            samp_rate, #bw
            "Baseband", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(fft_y_min, fft_y_max)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)

        self.qtgui_freq_sink_x_0.disable_legend()


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["green", "red", "green", "black", "cyan",
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 0, 0, 1, 150)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 150):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(1, CW_LPF, (tune_freq-center_freq), samp_rate)
        self.epy_block_0 = epy_block_0.blk(sample_rate=samp_rate_CW, wpm=CW_wpm)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/mkhuthir/rfdata/wav/CW/SDRuno_20200908_233405Z_7075kHz_CW.wav', True)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_threshold_ff_0 = blocks.threshold_ff(thresh_low, thresh_high, 0)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(sig_gain)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.analog_const_source_x_1 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, thresh_high)
        self.analog_const_source_x_0 = analog.sig_source_f(0, analog.GR_CONST_WAVE, 0, 0, thresh_low)
        self.analog_agc_xx_0 = analog.agc_ff((samp_rate_CW/80), 1, AGC_gain, 100000)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_agc_xx_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.analog_agc_xx_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.analog_const_source_x_0, 0), (self.qtgui_time_sink_x_0, 3))
        self.connect((self.analog_const_source_x_1, 0), (self.qtgui_time_sink_x_0, 2))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_throttle2_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_wavfile_source_0, 1), (self.blocks_float_to_complex_0, 1))
        self.connect((self.epy_block_0, 0), (self.show_text_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.qtgui_freq_sink_x_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "file_CW_decoder")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate_CW(self):
        return self.samp_rate_CW

    def set_samp_rate_CW(self, samp_rate_CW):
        self.samp_rate_CW = samp_rate_CW
        self.set_CW_LPF(firdes.low_pass(1.0, self.samp_rate, self.samp_rate_CW/2, 10e3, window.WIN_HAMMING, 6.76))
        self.analog_agc_xx_0.set_rate((self.samp_rate_CW/80))
        self.epy_block_0.sample_rate = self.samp_rate_CW
        self.qtgui_freq_sink_x_0_0.set_frequency_range(self.tune_freq, self.samp_rate_CW)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate_CW)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_CW_LPF(firdes.low_pass(1.0, self.samp_rate, self.samp_rate_CW/2, 10e3, window.WIN_HAMMING, 6.76))
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.center_freq, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.center_freq, self.samp_rate)

    def get_tune_freq(self):
        return self.tune_freq

    def set_tune_freq(self, tune_freq):
        self.tune_freq = tune_freq
        self.freq_xlating_fir_filter_xxx_0.set_center_freq((self.tune_freq-self.center_freq))
        self.qtgui_freq_sink_x_0_0.set_frequency_range(self.tune_freq, self.samp_rate_CW)

    def get_thresh_low(self):
        return self.thresh_low

    def set_thresh_low(self, thresh_low):
        self.thresh_low = thresh_low
        self.analog_const_source_x_0.set_offset(self.thresh_low)
        self.blocks_threshold_ff_0.set_lo(self.thresh_low)

    def get_thresh_high(self):
        return self.thresh_high

    def set_thresh_high(self, thresh_high):
        self.thresh_high = thresh_high
        self.analog_const_source_x_1.set_offset(self.thresh_high)
        self.blocks_threshold_ff_0.set_hi(self.thresh_high)

    def get_sig_gain(self):
        return self.sig_gain

    def set_sig_gain(self, sig_gain):
        self.sig_gain = sig_gain
        self.blocks_multiply_const_vxx_0.set_k(self.sig_gain)

    def get_fft_y_min(self):
        return self.fft_y_min

    def set_fft_y_min(self, fft_y_min):
        self.fft_y_min = fft_y_min
        self.qtgui_freq_sink_x_0.set_y_axis(self.fft_y_min, self.fft_y_max)
        self.qtgui_freq_sink_x_0_0.set_y_axis(self.fft_y_min, self.fft_y_max)
        self.qtgui_waterfall_sink_x_0.set_intensity_range(self.fft_y_min, self.fft_y_max)

    def get_fft_y_max(self):
        return self.fft_y_max

    def set_fft_y_max(self, fft_y_max):
        self.fft_y_max = fft_y_max
        self.qtgui_freq_sink_x_0.set_y_axis(self.fft_y_min, self.fft_y_max)
        self.qtgui_freq_sink_x_0_0.set_y_axis(self.fft_y_min, self.fft_y_max)
        self.qtgui_waterfall_sink_x_0.set_intensity_range(self.fft_y_min, self.fft_y_max)

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.freq_xlating_fir_filter_xxx_0.set_center_freq((self.tune_freq-self.center_freq))
        self.qtgui_freq_sink_x_0.set_frequency_range(self.center_freq, self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(self.center_freq, self.samp_rate)

    def get_CW_wpm(self):
        return self.CW_wpm

    def set_CW_wpm(self, CW_wpm):
        self.CW_wpm = CW_wpm
        self.epy_block_0.wpm = self.CW_wpm

    def get_CW_LPF(self):
        return self.CW_LPF

    def set_CW_LPF(self, CW_LPF):
        self.CW_LPF = CW_LPF
        self.freq_xlating_fir_filter_xxx_0.set_taps(self.CW_LPF)

    def get_AGC_gain(self):
        return self.AGC_gain

    def set_AGC_gain(self, AGC_gain):
        self.AGC_gain = AGC_gain
        self.analog_agc_xx_0.set_gain(self.AGC_gain)




def main(top_block_cls=file_CW_decoder, options=None):

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
