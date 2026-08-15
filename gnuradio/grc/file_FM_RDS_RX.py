#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: File Stereo FM receiver and RDS Decoder
# Author: Muthanna Alwahash
# Copyright: (c) 2026
# Description: File Stereo FM receiver and RDS Decoder
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
import rds
import sip
import threading



class file_FM_RDS_RX(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "File Stereo FM receiver and RDS Decoder", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("File Stereo FM receiver and RDS Decoder")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "file_FM_RDS_RX")

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
        self.samp_rate_RDS = samp_rate_RDS = 19000
        self.RDS_sps = RDS_sps = 8
        self.samp_rate_audio_band = samp_rate_audio_band = int(samp_rate_audio_sink*5)
        self.samp_rate_FM = samp_rate_FM = int(200e3)
        self.samp_rate = samp_rate = 4e6
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(1.0, samp_rate_RDS,samp_rate_RDS/RDS_sps, 1.0, (11*RDS_sps))
        self.LO_freq = LO_freq = 97.3
        self.volume = volume = -6
        self.rrc_taps_manchester = rrc_taps_manchester = [rrc_taps[n] - rrc_taps[n+8] for n in range(len(rrc_taps)-8)]
        self.rf_gain = rf_gain = 25
        self.freq_tune = freq_tune = (LO_freq)*1e6
        self.fft_size = fft_size = 1024
        self.cent_freq = cent_freq = 99
        self.RDS_freq = RDS_freq = 57000
        self.RDS_LPF_taps = RDS_LPF_taps = firdes.low_pass(1.0, samp_rate_FM, 7.5e3, 1e3, window.WIN_HAMMING, 6.76)
        self.Pilot_BPF_taps = Pilot_BPF_taps = firdes.complex_band_pass(1.0, samp_rate_audio_band, 18980, 19020, 1e3, window.WIN_HAMMING, 6.76)
        self.LR_LPF_taps = LR_LPF_taps = firdes.low_pass(1.0, samp_rate_audio_band, 15e3, 1e3, window.WIN_HAMMING, 6.76)
        self.Ch_LPF_taps = Ch_LPF_taps = firdes.low_pass(1.0, samp_rate, 135e3, 1e3, window.WIN_HAMMING, 6.76)
        self.CSA_freq = CSA_freq = 76000

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
        self._LO_freq_range = qtgui.Range(cent_freq-(samp_rate/2/1e6), cent_freq+(samp_rate/2/1e6), 0.1, 97.3, 200)
        self._LO_freq_win = qtgui.RangeWidget(self._LO_freq_range, self.set_LO_freq, "LO Freq.", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._LO_freq_win, 1, 0, 1, 100)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 100):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rf_gain_range = qtgui.Range(0, 49.6, 1, 25, 200)
        self._rf_gain_win = qtgui.RangeWidget(self._rf_gain_range, self.set_rf_gain, "RF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rf_gain_win, 3, 0, 1, 100)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 100):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rds_parser_0 = rds.parser(False, False, 0)
        self.rds_panel_0 = rds.rdsPanel((freq_tune/1e6))
        self._rds_panel_0_win = self.rds_panel_0
        self.top_grid_layout.addWidget(self._rds_panel_0_win, 0, 0, 1, 100)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 100):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rds_decoder_0 = rds.decoder(False, False)
        self.rational_resampler_xxx_1 = filter.rational_resampler_ccc(
                interpolation=samp_rate_RDS,
                decimation=samp_rate_FM,
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=samp_rate_audio_band,
                decimation=samp_rate_FM,
                taps=[],
                fractional_bw=0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_f(
            fft_size, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate_FM, #bw
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

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 9, 27, 2, 173)
        for r in range(9, 11):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(27, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_1 = qtgui.freq_sink_c(
            fft_size, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate_RDS, #bw
            '', #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_1.set_update_time(0.10)
        self.qtgui_freq_sink_x_1.set_y_axis((-100), (-55))
        self.qtgui_freq_sink_x_1.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_1.enable_grid(True)
        self.qtgui_freq_sink_x_1.set_fft_average(0.2)
        self.qtgui_freq_sink_x_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_1.enable_control_panel(False)
        self.qtgui_freq_sink_x_1.set_fft_window_normalized(False)

        self.qtgui_freq_sink_x_1.disable_legend()


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
                self.qtgui_freq_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_1.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_1_win, 9, 0, 2, 20)
        for r in range(9, 11):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 20):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_0 = qtgui.freq_sink_f(
            fft_size, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate_FM, #bw
            "FM MPX", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0_0.set_y_axis((-100), (-10))
        self.qtgui_freq_sink_x_0_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_0.enable_grid(True)
        self.qtgui_freq_sink_x_0_0.set_fft_average(0.2)
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_0_win, 7, 20, 2, 180)
        for r in range(7, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(20, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            fft_size, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            (cent_freq*1e6), #fc
            samp_rate, #bw
            "Baseband", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-70), (-25))
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 0, 100, 4, 100)
        for r in range(0, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(100, 200):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "RDS Constellation", #name
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
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win, 7, 0, 2, 20)
        for r in range(7, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 20):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.freq_xlating_fir_filter_xxx_1_0 = filter.freq_xlating_fir_filter_fcc(1, RDS_LPF_taps, RDS_freq, samp_rate_FM)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc((int(samp_rate/samp_rate_FM)), Ch_LPF_taps, ((LO_freq-cent_freq)*1e6), samp_rate)
        self.fir_filter_xxx_2 = filter.fir_filter_ccc(1, rrc_taps_manchester)
        self.fir_filter_xxx_2.declare_sample_delay(0)
        self.fir_filter_xxx_1_0 = filter.fir_filter_fff(5, LR_LPF_taps)
        self.fir_filter_xxx_1_0.declare_sample_delay(0)
        self.fir_filter_xxx_1 = filter.fir_filter_fff((int(samp_rate_audio_band/samp_rate_audio_sink)), LR_LPF_taps)
        self.fir_filter_xxx_1.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_fcc(1, Pilot_BPF_taps)
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
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/mkhuthir/rfdata/wav/Broadcast_FM/bfm.2021-12-16T14_23_16_147.wav', True)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff((10**(1.*(volume)/10)))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff((10**(1.*(volume)/10)))
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, ((len(Pilot_BPF_taps) - 1) // 2))
        self.blocks_correctiq_0 = blocks.correctiq()
        self.blocks_complex_to_imag_0 = blocks.complex_to_imag(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((samp_rate_FM / (2*math.pi*75e3)))
        self.analog_pll_refout_cc_0 = analog.pll_refout_cc(0.001, (2 * math.pi * 19020 / samp_rate_audio_band), (2 * math.pi * 18980 / samp_rate_audio_band))
        self.analog_fm_deemph_0_0_0 = analog.fm_deemph(fs=samp_rate_audio_sink, tau=(50e-6))
        self.analog_fm_deemph_0_0 = analog.fm_deemph(fs=samp_rate_audio_sink, tau=(50e-6))
        self.analog_agc_xx_0 = analog.agc_cc((2e-3), 0.585, 53, 1000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.rds_decoder_0, 'out'), (self.rds_parser_0, 'in'))
        self.msg_connect((self.rds_parser_0, 'out'), (self.rds_panel_0, 'in'))
        self.connect((self.analog_agc_xx_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.analog_fm_deemph_0_0_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.freq_xlating_fir_filter_xxx_1_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_freq_sink_x_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_fm_deemph_0_0_0, 0))
        self.connect((self.blocks_complex_to_imag_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_correctiq_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_correctiq_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.blocks_delay_0, 0), (self.fir_filter_xxx_1, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.audio_sink_0, 1))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_complex_to_imag_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.fir_filter_xxx_1_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.analog_fm_deemph_0_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.blocks_correctiq_0, 0))
        self.connect((self.blocks_wavfile_source_0, 1), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0, 2), (self.blocks_null_sink_0, 1))
        self.connect((self.digital_constellation_receiver_cb_0, 3), (self.blocks_null_sink_0, 2))
        self.connect((self.digital_constellation_receiver_cb_0, 1), (self.blocks_null_sink_0, 0))
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
        self.connect((self.freq_xlating_fir_filter_xxx_1_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.fir_filter_xxx_2, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.qtgui_freq_sink_x_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "file_FM_RDS_RX")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate_audio_sink(self):
        return self.samp_rate_audio_sink

    def set_samp_rate_audio_sink(self, samp_rate_audio_sink):
        self.samp_rate_audio_sink = samp_rate_audio_sink
        self.set_samp_rate_audio_band(int(self.samp_rate_audio_sink*5))

    def get_samp_rate_RDS(self):
        return self.samp_rate_RDS

    def set_samp_rate_RDS(self, samp_rate_RDS):
        self.samp_rate_RDS = samp_rate_RDS
        self.set_rrc_taps(firdes.root_raised_cosine(1.0, self.samp_rate_RDS, self.samp_rate_RDS/self.RDS_sps, 1.0, (11*self.RDS_sps)))
        self.qtgui_freq_sink_x_1.set_frequency_range(0, self.samp_rate_RDS)

    def get_RDS_sps(self):
        return self.RDS_sps

    def set_RDS_sps(self, RDS_sps):
        self.RDS_sps = RDS_sps
        self.set_rrc_taps(firdes.root_raised_cosine(1.0, self.samp_rate_RDS, self.samp_rate_RDS/self.RDS_sps, 1.0, (11*self.RDS_sps)))

    def get_samp_rate_audio_band(self):
        return self.samp_rate_audio_band

    def set_samp_rate_audio_band(self, samp_rate_audio_band):
        self.samp_rate_audio_band = samp_rate_audio_band
        self.set_LR_LPF_taps(firdes.low_pass(1.0, self.samp_rate_audio_band, 15e3, 1e3, window.WIN_HAMMING, 6.76))
        self.set_Pilot_BPF_taps(firdes.complex_band_pass(1.0, self.samp_rate_audio_band, 18980, 19020, 1e3, window.WIN_HAMMING, 6.76))
        self.analog_pll_refout_cc_0.set_max_freq((2 * math.pi * 19020 / self.samp_rate_audio_band))
        self.analog_pll_refout_cc_0.set_min_freq((2 * math.pi * 18980 / self.samp_rate_audio_band))

    def get_samp_rate_FM(self):
        return self.samp_rate_FM

    def set_samp_rate_FM(self, samp_rate_FM):
        self.samp_rate_FM = samp_rate_FM
        self.set_RDS_LPF_taps(firdes.low_pass(1.0, self.samp_rate_FM, 7.5e3, 1e3, window.WIN_HAMMING, 6.76))
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate_FM / (2*math.pi*75e3)))
        self.qtgui_freq_sink_x_0_0.set_frequency_range(0, self.samp_rate_FM)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate_FM)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_Ch_LPF_taps(firdes.low_pass(1.0, self.samp_rate, 135e3, 1e3, window.WIN_HAMMING, 6.76))
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)
        self.qtgui_freq_sink_x_0.set_frequency_range((self.cent_freq*1e6), self.samp_rate)

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.set_rrc_taps_manchester([self.rrc_taps[n] - self.rrc_taps[n+8] for n in range(len(self.rrc_taps)-8)])

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        self.set_freq_tune((self.LO_freq)*1e6)
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(((self.LO_freq-self.cent_freq)*1e6))

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_0.set_k((10**(1.*(self.volume)/10)))
        self.blocks_multiply_const_vxx_0_0.set_k((10**(1.*(self.volume)/10)))

    def get_rrc_taps_manchester(self):
        return self.rrc_taps_manchester

    def set_rrc_taps_manchester(self, rrc_taps_manchester):
        self.rrc_taps_manchester = rrc_taps_manchester
        self.fir_filter_xxx_2.set_taps(self.rrc_taps_manchester)

    def get_rf_gain(self):
        return self.rf_gain

    def set_rf_gain(self, rf_gain):
        self.rf_gain = rf_gain

    def get_freq_tune(self):
        return self.freq_tune

    def set_freq_tune(self, freq_tune):
        self.freq_tune = freq_tune
        self.rds_panel_0.set_frequency((self.freq_tune/1e6))
        self.rds_parser_0.reset() # self.freq_tune

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size

    def get_cent_freq(self):
        return self.cent_freq

    def set_cent_freq(self, cent_freq):
        self.cent_freq = cent_freq
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(((self.LO_freq-self.cent_freq)*1e6))
        self.qtgui_freq_sink_x_0.set_frequency_range((self.cent_freq*1e6), self.samp_rate)

    def get_RDS_freq(self):
        return self.RDS_freq

    def set_RDS_freq(self, RDS_freq):
        self.RDS_freq = RDS_freq
        self.freq_xlating_fir_filter_xxx_1_0.set_center_freq(self.RDS_freq)

    def get_RDS_LPF_taps(self):
        return self.RDS_LPF_taps

    def set_RDS_LPF_taps(self, RDS_LPF_taps):
        self.RDS_LPF_taps = RDS_LPF_taps
        self.freq_xlating_fir_filter_xxx_1_0.set_taps(self.RDS_LPF_taps)

    def get_Pilot_BPF_taps(self):
        return self.Pilot_BPF_taps

    def set_Pilot_BPF_taps(self, Pilot_BPF_taps):
        self.Pilot_BPF_taps = Pilot_BPF_taps
        self.blocks_delay_0.set_dly(int(((len(self.Pilot_BPF_taps) - 1) // 2)))
        self.fir_filter_xxx_0.set_taps(self.Pilot_BPF_taps)

    def get_LR_LPF_taps(self):
        return self.LR_LPF_taps

    def set_LR_LPF_taps(self, LR_LPF_taps):
        self.LR_LPF_taps = LR_LPF_taps
        self.fir_filter_xxx_1.set_taps(self.LR_LPF_taps)
        self.fir_filter_xxx_1_0.set_taps(self.LR_LPF_taps)

    def get_Ch_LPF_taps(self):
        return self.Ch_LPF_taps

    def set_Ch_LPF_taps(self, Ch_LPF_taps):
        self.Ch_LPF_taps = Ch_LPF_taps
        self.freq_xlating_fir_filter_xxx_0.set_taps(self.Ch_LPF_taps)

    def get_CSA_freq(self):
        return self.CSA_freq

    def set_CSA_freq(self, CSA_freq):
        self.CSA_freq = CSA_freq




def main(top_block_cls=file_FM_RDS_RX, options=None):

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
