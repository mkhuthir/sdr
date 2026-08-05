#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: LimeSDR Stereo FM receiver and RDS Decoder
# Author: Muthanna Alwahash
# Copyright: (c) 2026
# Description: LimeSDR Stereo FM receiver and RDS Decoder
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import analog
import math
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
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
import rds
import sip
import threading



class LimeSDR_FM_RDS_RX(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "LimeSDR Stereo FM receiver and RDS Decoder", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("LimeSDR Stereo FM receiver and RDS Decoder")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "LimeSDR_FM_RDS_RX")

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
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(1.0, 19000,19000/8, 1.0, 151)
        self.NCO_offset = NCO_offset = 0
        self.LO_freq = LO_freq = 92.6
        self.volume = volume = -6
        self.samp_rate = samp_rate = 1920000
        self.rrc_taps_manchester = rrc_taps_manchester = [rrc_taps[n] - rrc_taps[n+8] for n in range(len(rrc_taps)-8)]
        self.pilot_taps = pilot_taps = firdes.complex_band_pass(1.0, 240000, 18980, 19020, 1000, window.WIN_HAMMING, 6.76)
        self.gain = gain = 25
        self.freq_tune = freq_tune = LO_freq*1e6 +NCO_offset
        self.decimation = decimation = 5
        self.baseband_Y_min = baseband_Y_min = -160
        self.baseband_Y_max = baseband_Y_max = 0
        self.FM_Y_min = FM_Y_min = -160
        self.FM_Y_max = FM_Y_max = 0

        ##################################################
        # Blocks
        ##################################################

        self._volume_range = qtgui.Range(-20, 10, 1, -6, 200)
        self._volume_win = qtgui.RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._volume_win, 2, 0, 1, 100)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 100):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._gain_range = qtgui.Range(0, 49.6, 1, 25, 200)
        self._gain_win = qtgui.RangeWidget(self._gain_range, self.set_gain, "RF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._gain_win, 3, 0, 1, 100)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 100):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._baseband_Y_min_range = qtgui.Range(-200, -70, 10, -160, 200)
        self._baseband_Y_min_win = qtgui.RangeWidget(self._baseband_Y_min_range, self.set_baseband_Y_min, "Min", "slider", float, QtCore.Qt.Vertical)
        self.top_grid_layout.addWidget(self._baseband_Y_min_win, 2, 200, 2, 1)
        for r in range(2, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(200, 201):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._baseband_Y_max_range = qtgui.Range((-60), 10, 10, 0, 200)
        self._baseband_Y_max_win = qtgui.RangeWidget(self._baseband_Y_max_range, self.set_baseband_Y_max, "Max", "slider", int, QtCore.Qt.Vertical)
        self.top_grid_layout.addWidget(self._baseband_Y_max_win, 0, 200, 2, 1)
        for r in range(0, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(200, 201):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._NCO_offset_range = qtgui.Range(-samp_rate/2, samp_rate/2, 100e3, 0, 200)
        self._NCO_offset_win = qtgui.RangeWidget(self._NCO_offset_range, self.set_NCO_offset, "NCO Offset", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._NCO_offset_win, 1, 0, 1, 100)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 100):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._LO_freq_range = qtgui.Range(87, 108, 0.1, 92.6, 200)
        self._LO_freq_win = qtgui.RangeWidget(self._LO_freq_range, self.set_LO_freq, "LO Freq.", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._LO_freq_win, 0, 0, 1, 100)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 100):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._FM_Y_min_range = qtgui.Range(-200, -70, 10, -160, 200)
        self._FM_Y_min_win = qtgui.RangeWidget(self._FM_Y_min_range, self.set_FM_Y_min, "Min", "slider", float, QtCore.Qt.Vertical)
        self.top_grid_layout.addWidget(self._FM_Y_min_win, 7, 200, 2, 1)
        for r in range(7, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(200, 201):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._FM_Y_max_range = qtgui.Range((-60), 10, 10, 0, 200)
        self._FM_Y_max_win = qtgui.RangeWidget(self._FM_Y_max_range, self.set_FM_Y_max, "Max", "slider", int, QtCore.Qt.Vertical)
        self.top_grid_layout.addWidget(self._FM_Y_max_win, 5, 200, 2, 1)
        for r in range(5, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(200, 201):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rds_parser_0 = rds.parser(False, False, 0)
        self.rds_panel_0 = rds.rdsPanel(freq_tune)
        self._rds_panel_0_win = self.rds_panel_0
        self.top_grid_layout.addWidget(self._rds_panel_0_win, 4, 0, 1, 100)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 100):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rds_decoder_0 = rds.decoder(False, False)
        self.rational_resampler_xxx_1 = filter.rational_resampler_ccc(
                interpolation=19000,
                decimation=(samp_rate // decimation // 10),
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=240000,
                decimation=(samp_rate // decimation),
                taps=[],
                fractional_bw=0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_f(
            1024, #size
            window.WIN_HAMMING, #wintype
            0, #fc
            (samp_rate / decimation), #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0.10)
        self.qtgui_waterfall_sink_x_0.enable_grid(True)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(False)

        self.qtgui_waterfall_sink_x_0.disable_legend()

        self.qtgui_waterfall_sink_x_0.set_plot_pos_half(not False)

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

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-100, -10)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 9, 25, 8, 175)
        for r in range(9, 17):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(25, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            (samp_rate / decimation), #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0.set_y_axis(FM_Y_min, FM_Y_max)
        self.qtgui_freq_sink_x_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0.enable_grid(True)
        self.qtgui_freq_sink_x_0_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0_0.set_fft_window_normalized(False)

        self.qtgui_freq_sink_x_0_0.disable_legend()

        self.qtgui_freq_sink_x_0_0.set_plot_pos_half(not False)

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
                self.qtgui_freq_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_win, 5, 20, 4, 180)
        for r in range(5, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(20, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq_tune, #fc
            (samp_rate/decimation), #bw
            "", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(baseband_Y_min, baseband_Y_max)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
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
        alphas = [1, 1.0, 1.0, 1.0, 1.0,
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 0, 100, 5, 100)
        for r in range(0, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(100, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(True)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)

        self.qtgui_const_sink_x_0.disable_legend()

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["green", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win, 5, 0, 6, 20)
        for r in range(5, 11):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 20):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.limesuiteng_sdrdevice_source_0 = limesuiteng.sdrdevice_source('', '', 0, [0], "complex32f_t", "complex12_t", samp_rate, 0)
        self.limesuiteng_sdrdevice_source_0.set_lo_frequency(LO_freq*1e6)
        self.limesuiteng_sdrdevice_source_0.set_gfir_bandwidth(0)
        self.limesuiteng_sdrdevice_source_0.set_antenna('auto')
        if 0 == 1:
          self.limesuiteng_sdrdevice_source_0.set_gain(0, 30+0)
          self.limesuiteng_sdrdevice_source_0.set_gain(2, 0)
          self.limesuiteng_sdrdevice_source_0.set_gain(3, 12+-3)
        else:
          self.limesuiteng_sdrdevice_source_0.set_gain_generic(gain)
        self.limesuiteng_sdrdevice_source_0.set_nco_frequency(NCO_offset)
        self.limesuiteng_sdrdevice_source_0.set_lpf_bandwidth(20e6) # Rx LPF range depends on TIA gain
        self.limesuiteng_sdrdevice_source_0.set_calibration_enable(0)
        self.freq_xlating_fir_filter_xxx_1_0 = filter.freq_xlating_fir_filter_fcc(10, firdes.low_pass(1.0, samp_rate / decimation, 7.5e3, 5e3), 57e3, (samp_rate / decimation))
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(decimation, firdes.low_pass(1, samp_rate, 135000, 20000), 0, samp_rate)
        self.fir_filter_xxx_2 = filter.fir_filter_ccc(1, rrc_taps_manchester)
        self.fir_filter_xxx_2.declare_sample_delay(0)
        self.fir_filter_xxx_1_0 = filter.fir_filter_fff(5, firdes.low_pass(-2.1,240000,15e3,2e3))
        self.fir_filter_xxx_1_0.declare_sample_delay(0)
        self.fir_filter_xxx_1 = filter.fir_filter_fff(5, firdes.low_pass(1.0,240000,15e3,2e3))
        self.fir_filter_xxx_1.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_fcc(1, pilot_taps)
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_cc(
            digital.TED_ZERO_CROSSING,
            16,
            0.01,
            1.0,
            1.0,
            0.1,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2, digital.DIFF_DIFFERENTIAL)
        self.digital_constellation_receiver_cb_0 = digital.constellation_receiver_cb(digital.constellation_bpsk().base(), (2*math.pi / 100), (-0.002), 0.002)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff((10**(1.*(volume)/10)))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff((10**(1.*(volume)/10)))
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, ((len(pilot_taps) - 1) // 2))
        self.blocks_complex_to_imag_0 = blocks.complex_to_imag(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(((samp_rate / decimation) / (2*math.pi*75000)))
        self.analog_pll_refout_cc_0 = analog.pll_refout_cc(0.001, (2 * math.pi * 19020 / 240000), (2 * math.pi * 18980 / 240000))
        self.analog_fm_deemph_0_0_0 = analog.fm_deemph(fs=48000, tau=(50e-6))
        self.analog_fm_deemph_0_0 = analog.fm_deemph(fs=48000, tau=(50e-6))
        self.analog_agc_xx_0 = analog.agc_cc((2e-3), 0.585, 53, 1000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.rds_decoder_0, 'out'), (self.rds_parser_0, 'in'))
        self.msg_connect((self.rds_parser_0, 'out'), (self.rds_panel_0, 'in'))
        self.connect((self.analog_agc_xx_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.analog_fm_deemph_0_0_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.freq_xlating_fir_filter_xxx_1_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_freq_sink_x_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_fm_deemph_0_0_0, 0))
        self.connect((self.blocks_complex_to_imag_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_delay_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.blocks_delay_0, 0), (self.fir_filter_xxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.audio_sink_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_complex_to_imag_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.fir_filter_xxx_1_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.analog_fm_deemph_0_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0, 2), (self.blocks_null_sink_0, 1))
        self.connect((self.digital_constellation_receiver_cb_0, 1), (self.blocks_null_sink_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0, 3), (self.blocks_null_sink_0, 2))
        self.connect((self.digital_constellation_receiver_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0, 4), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.rds_decoder_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_constellation_receiver_cb_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.analog_pll_refout_cc_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.fir_filter_xxx_1_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.fir_filter_xxx_1_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.fir_filter_xxx_2, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_1_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.limesuiteng_sdrdevice_source_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.fir_filter_xxx_2, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "LimeSDR_FM_RDS_RX")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.set_rrc_taps_manchester([self.rrc_taps[n] - self.rrc_taps[n+8] for n in range(len(self.rrc_taps)-8)])

    def get_NCO_offset(self):
        return self.NCO_offset

    def set_NCO_offset(self, NCO_offset):
        self.NCO_offset = NCO_offset
        self.set_freq_tune(self.LO_freq*1e6 +self.NCO_offset)
        self.limesuiteng_sdrdevice_source_0.set_nco_frequency(self.NCO_offset)

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        self.set_freq_tune(self.LO_freq*1e6 +self.NCO_offset)
        self.limesuiteng_sdrdevice_source_0.set_lo_frequency(self.LO_freq*1e6)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_0.set_k((10**(1.*(self.volume)/10)))
        self.blocks_multiply_const_vxx_0_0.set_k((10**(1.*(self.volume)/10)))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_quadrature_demod_cf_0.set_gain(((self.samp_rate / self.decimation) / (2*math.pi*75000)))
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1, self.samp_rate, 135000, 20000))
        self.freq_xlating_fir_filter_xxx_1_0.set_taps(firdes.low_pass(1.0, self.samp_rate / self.decimation, 7.5e3, 5e3))
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_tune, (self.samp_rate/self.decimation))
        self.qtgui_freq_sink_x_0_0.set_frequency_range(0, (self.samp_rate / self.decimation))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, (self.samp_rate / self.decimation))

    def get_rrc_taps_manchester(self):
        return self.rrc_taps_manchester

    def set_rrc_taps_manchester(self, rrc_taps_manchester):
        self.rrc_taps_manchester = rrc_taps_manchester
        self.fir_filter_xxx_2.set_taps(self.rrc_taps_manchester)

    def get_pilot_taps(self):
        return self.pilot_taps

    def set_pilot_taps(self, pilot_taps):
        self.pilot_taps = pilot_taps
        self.blocks_delay_0.set_dly(int(((len(self.pilot_taps) - 1) // 2)))
        self.fir_filter_xxx_0.set_taps(self.pilot_taps)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.limesuiteng_sdrdevice_source_0.set_gain_generic(self.gain)

    def get_freq_tune(self):
        return self.freq_tune

    def set_freq_tune(self, freq_tune):
        self.freq_tune = freq_tune
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_tune, (self.samp_rate/self.decimation))
        self.rds_panel_0.set_frequency(self.freq_tune)
        self.rds_parser_0.reset() # self.freq_tune

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.analog_quadrature_demod_cf_0.set_gain(((self.samp_rate / self.decimation) / (2*math.pi*75000)))
        self.freq_xlating_fir_filter_xxx_1_0.set_taps(firdes.low_pass(1.0, self.samp_rate / self.decimation, 7.5e3, 5e3))
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq_tune, (self.samp_rate/self.decimation))
        self.qtgui_freq_sink_x_0_0.set_frequency_range(0, (self.samp_rate / self.decimation))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, (self.samp_rate / self.decimation))

    def get_baseband_Y_min(self):
        return self.baseband_Y_min

    def set_baseband_Y_min(self, baseband_Y_min):
        self.baseband_Y_min = baseband_Y_min
        self.qtgui_freq_sink_x_0.set_y_axis(self.baseband_Y_min, self.baseband_Y_max)

    def get_baseband_Y_max(self):
        return self.baseband_Y_max

    def set_baseband_Y_max(self, baseband_Y_max):
        self.baseband_Y_max = baseband_Y_max
        self.qtgui_freq_sink_x_0.set_y_axis(self.baseband_Y_min, self.baseband_Y_max)

    def get_FM_Y_min(self):
        return self.FM_Y_min

    def set_FM_Y_min(self, FM_Y_min):
        self.FM_Y_min = FM_Y_min
        self.qtgui_freq_sink_x_0_0.set_y_axis(self.FM_Y_min, self.FM_Y_max)

    def get_FM_Y_max(self):
        return self.FM_Y_max

    def set_FM_Y_max(self, FM_Y_max):
        self.FM_Y_max = FM_Y_max
        self.qtgui_freq_sink_x_0_0.set_y_axis(self.FM_Y_min, self.FM_Y_max)




def main(top_block_cls=LimeSDR_FM_RDS_RX, options=None):

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
