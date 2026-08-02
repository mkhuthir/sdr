#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: LimeSDR FM Receiver
# Author: Muthanna Alwahash
# Copyright: (c) 2026
# Description: LimeSDR Mini 1.2 FM Receiver
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5.QtCore import QObject, pyqtSlot
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



class LimeSDR_FM_RX(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "LimeSDR FM Receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("LimeSDR FM Receiver")
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

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "LimeSDR_FM_RX")

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
        self.LO_freq = LO_freq = 95000000
        self.volume = volume = 3
        self.samp_rate_audio = samp_rate_audio = 48000
        self.samp_rate = samp_rate = 5e6
        self.antenna = antenna = 'auto'
        self.VFO_freq = VFO_freq = LO_freq
        self.RX_LPF_cutoff = RX_LPF_cutoff = 4e6
        self.RF_gain = RF_gain = 20
        self.NCO_offset = NCO_offset = 0
        self.GFIR_bandwidth = GFIR_bandwidth = 300e3

        ##################################################
        # Blocks
        ##################################################

        if "real" == "int":
        	isFloat = False
        	scaleFactor = 1
        else:
        	isFloat = True
        	scaleFactor = 0.1

        _volume_dial_control = qtgui.GrDialControl('Volume', self, 0,100,3,"orange",self.set_volume,isFloat, scaleFactor, 100, True, "'value'")
        self.volume = _volume_dial_control

        self.top_grid_layout.addWidget(_volume_dial_control, 5, 1, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._antenna_options = ['LNAW', 'LNAH', 'LNAL', 'auto']
        # Create the labels list
        self._antenna_labels = ['LNAW', 'LNAH', 'LNAL', 'auto']
        # Create the combo box
        # Create the radio buttons
        self._antenna_group_box = Qt.QGroupBox("LNA Path" + ": ")
        self._antenna_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._antenna_button_group = variable_chooser_button_group()
        self._antenna_group_box.setLayout(self._antenna_box)
        for i, _label in enumerate(self._antenna_labels):
            radio_button = Qt.QRadioButton(_label)
            self._antenna_box.addWidget(radio_button)
            self._antenna_button_group.addButton(radio_button, i)
        self._antenna_callback = lambda i: Qt.QMetaObject.invokeMethod(self._antenna_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._antenna_options.index(i)))
        self._antenna_callback(self.antenna)
        self._antenna_button_group.buttonClicked[int].connect(
            lambda i: self.set_antenna(self._antenna_options[i]))
        self.top_grid_layout.addWidget(self._antenna_group_box, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._RX_LPF_cutoff_msgdigctl_win = qtgui.MsgDigitalNumberControl(lbl='RX Low Pass Filter cutoff frequency Hz', min_freq_hz=4e6, max_freq_hz=130e6, parent=self, thousands_separator=",", background_color="gray", fontColor="white", var_callback=self.set_RX_LPF_cutoff, outputmsgname='freq')
        self._RX_LPF_cutoff_msgdigctl_win.setValue(4e6)
        self._RX_LPF_cutoff_msgdigctl_win.setReadOnly(False)
        self.RX_LPF_cutoff = self._RX_LPF_cutoff_msgdigctl_win

        self.top_grid_layout.addWidget(self._RX_LPF_cutoff_msgdigctl_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        if "int" == "int":
        	isFloat = False
        	scaleFactor = 1
        else:
        	isFloat = True
        	scaleFactor = 1

        _RF_gain_dial_control = qtgui.GrDialControl('RF Gain dB', self, 0,100,20,"yellow",self.set_RF_gain,isFloat, scaleFactor, 100, True, "'value'")
        self.RF_gain = _RF_gain_dial_control

        self.top_grid_layout.addWidget(_RF_gain_dial_control, 5, 0, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._NCO_offset_msgdigctl_win = qtgui.MsgDigitalNumberControl(lbl='NCO Offset Hz', min_freq_hz=-samp_rate, max_freq_hz=samp_rate, parent=self, thousands_separator=",", background_color="black", fontColor="green", var_callback=self.set_NCO_offset, outputmsgname='freq')
        self._NCO_offset_msgdigctl_win.setValue(0)
        self._NCO_offset_msgdigctl_win.setReadOnly(False)
        self.NCO_offset = self._NCO_offset_msgdigctl_win

        self.top_grid_layout.addWidget(self._NCO_offset_msgdigctl_win, 4, 0, 1, 2)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._LO_freq_msgdigctl_win = qtgui.MsgDigitalNumberControl(lbl='LO Frequency Hz', min_freq_hz=86e+6, max_freq_hz=109e+6, parent=self, thousands_separator=".", background_color="black", fontColor="green", var_callback=self.set_LO_freq, outputmsgname='LO_freq')
        self._LO_freq_msgdigctl_win.setValue(95000000)
        self._LO_freq_msgdigctl_win.setReadOnly(False)
        self.LO_freq = self._LO_freq_msgdigctl_win

        self.top_grid_layout.addWidget(self._LO_freq_msgdigctl_win, 3, 0, 1, 2)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._GFIR_bandwidth_msgdigctl_win = qtgui.MsgDigitalNumberControl(lbl='GFIR Bandwidth Hz', min_freq_hz=0, max_freq_hz=samp_rate, parent=self, thousands_separator=",", background_color="gray", fontColor="white", var_callback=self.set_GFIR_bandwidth, outputmsgname='freq')
        self._GFIR_bandwidth_msgdigctl_win.setValue(300e3)
        self._GFIR_bandwidth_msgdigctl_win.setReadOnly(False)
        self.GFIR_bandwidth = self._GFIR_bandwidth_msgdigctl_win

        self.top_grid_layout.addWidget(self._GFIR_bandwidth_msgdigctl_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=(int(samp_rate_audio/1000)),
                decimation=(int(samp_rate/10000)),
                taps=[],
                fractional_bw=0)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            LO_freq, #fc
            samp_rate, #bw
            '', #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-140), 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(0.2)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(True)
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
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 0, 2, 12, 12)
        for r in range(0, 12):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 14):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.limesuiteng_sdrdevice_source_0 = limesuiteng.sdrdevice_source('', '', 0, [0], "complex32f_t", "complex16_t", samp_rate, 0)
        self.limesuiteng_sdrdevice_source_0.set_lo_frequency(LO_freq)
        self.limesuiteng_sdrdevice_source_0.set_gfir_bandwidth(GFIR_bandwidth)
        self.limesuiteng_sdrdevice_source_0.set_antenna(antenna)
        if 0 == 1:
          self.limesuiteng_sdrdevice_source_0.set_gain(0, 30+0)
          self.limesuiteng_sdrdevice_source_0.set_gain(2, 0)
          self.limesuiteng_sdrdevice_source_0.set_gain(3, 12+-3)
        else:
          self.limesuiteng_sdrdevice_source_0.set_gain_generic(RF_gain)
        self.limesuiteng_sdrdevice_source_0.set_nco_frequency(NCO_offset)
        self.limesuiteng_sdrdevice_source_0.set_lpf_bandwidth(RX_LPF_cutoff) # Rx LPF range depends on TIA gain
        self.limesuiteng_sdrdevice_source_0.set_calibration_enable(1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(volume)
        self.audio_sink_0 = audio.sink(samp_rate_audio, '', True)
        self.analog_wfm_rcv_0 = analog.wfm_rcv(
        	quad_rate=samp_rate_audio,
        	audio_decimation=10,
        )
        self._VFO_freq_msgdigctl_win = qtgui.MsgDigitalNumberControl(lbl='VFO Freq Hz', min_freq_hz=0, max_freq_hz=6e12, parent=self, thousands_separator=",", background_color="black", fontColor="white", var_callback=self.set_VFO_freq, outputmsgname='freq')
        self._VFO_freq_msgdigctl_win.setValue(LO_freq)
        self._VFO_freq_msgdigctl_win.setReadOnly(True)
        self.VFO_freq = self._VFO_freq_msgdigctl_win

        self.top_grid_layout.addWidget(self._VFO_freq_msgdigctl_win, 6, 0, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_wfm_rcv_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.limesuiteng_sdrdevice_source_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.limesuiteng_sdrdevice_source_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.analog_wfm_rcv_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "LimeSDR_FM_RX")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_LO_freq(self):
        return self.LO_freq

    def set_LO_freq(self, LO_freq):
        self.LO_freq = LO_freq
        self._VFO_freq_msgdigctl_win.setValue(self.LO_freq)
        self.limesuiteng_sdrdevice_source_0.set_lo_frequency(self.LO_freq)
        self.qtgui_freq_sink_x_0.set_frequency_range(self.LO_freq, self.samp_rate)

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_0.set_k(self.volume)

    def get_samp_rate_audio(self):
        return self.samp_rate_audio

    def set_samp_rate_audio(self, samp_rate_audio):
        self.samp_rate_audio = samp_rate_audio

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_freq_sink_x_0.set_frequency_range(self.LO_freq, self.samp_rate)

    def get_antenna(self):
        return self.antenna

    def set_antenna(self, antenna):
        self.antenna = antenna
        self._antenna_callback(self.antenna)
        self.limesuiteng_sdrdevice_source_0.set_antenna(self.antenna)

    def get_VFO_freq(self):
        return self.VFO_freq

    def set_VFO_freq(self, VFO_freq):
        self.VFO_freq = VFO_freq

    def get_RX_LPF_cutoff(self):
        return self.RX_LPF_cutoff

    def set_RX_LPF_cutoff(self, RX_LPF_cutoff):
        self.RX_LPF_cutoff = RX_LPF_cutoff
        self.limesuiteng_sdrdevice_source_0.set_lpf_bandwidth(self.RX_LPF_cutoff)

    def get_RF_gain(self):
        return self.RF_gain

    def set_RF_gain(self, RF_gain):
        self.RF_gain = RF_gain
        self.limesuiteng_sdrdevice_source_0.set_gain_generic(self.RF_gain)

    def get_NCO_offset(self):
        return self.NCO_offset

    def set_NCO_offset(self, NCO_offset):
        self.NCO_offset = NCO_offset
        self.limesuiteng_sdrdevice_source_0.set_nco_frequency(self.NCO_offset)

    def get_GFIR_bandwidth(self):
        return self.GFIR_bandwidth

    def set_GFIR_bandwidth(self, GFIR_bandwidth):
        self.GFIR_bandwidth = GFIR_bandwidth
        self.limesuiteng_sdrdevice_source_0.set_gfir_bandwidth(self.GFIR_bandwidth)




def main(top_block_cls=LimeSDR_FM_RX, options=None):

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
