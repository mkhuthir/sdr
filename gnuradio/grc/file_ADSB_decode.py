#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: ADSB Decoder
# Author: Muthanna Alwahash
# Copyright: (c) 2026
# Description: ADSB Decoder
# GNU Radio version: 3.10.12.0

from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
import gnuradio.adsb as adsb
import threading




class file_ADSB_decode(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "ADSB Decoder", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Variables
        ##################################################
        self.samp_rate_ADSB = samp_rate_ADSB = 6000000
        self.samp_rate = samp_rate = 2400000
        self.fft_y_min = fft_y_min = -70
        self.fft_y_max = fft_y_max = -30
        self.fft_size = fft_size = 2048
        self.detect_thre = detect_thre = 0.20
        self.center_freq = center_freq = 1090e6

        ##################################################
        # Blocks
        ##################################################

        self.rational_resampler_xxx_0 = filter.rational_resampler_ccc(
                interpolation=samp_rate_ADSB,
                decimation=samp_rate,
                taps=[],
                fractional_bw=0)
        self.blocks_wavfile_source_0 = blocks.wavfile_source('/home/mkhuthir/rfdata/wav/ADSB/adsb.2021-11-26T15_03_30_573.wav', False)
        self.blocks_throttle2_0 = blocks.throttle( gr.sizeof_gr_complex*1, samp_rate, True, 0 if "auto" == "auto" else max( int(float(0.1) * samp_rate) if "auto" == "time" else int(0.1), 1) )
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(1)
        self.adsb_framer_1 = adsb.framer(samp_rate_ADSB, detect_thre)
        self.adsb_demod_0 = adsb.demod(samp_rate_ADSB)
        self.adsb_decoder_0 = adsb.decoder("All Messages", "Conservative", "Brief")


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.adsb_demod_0, 'demodulated'), (self.adsb_decoder_0, 'demodulated'))
        self.connect((self.adsb_demod_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.adsb_framer_1, 0), (self.adsb_demod_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.adsb_framer_1, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.blocks_throttle2_0, 0))
        self.connect((self.blocks_throttle2_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_wavfile_source_0, 1), (self.blocks_float_to_complex_0, 1))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))


    def get_samp_rate_ADSB(self):
        return self.samp_rate_ADSB

    def set_samp_rate_ADSB(self, samp_rate_ADSB):
        self.samp_rate_ADSB = samp_rate_ADSB

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle2_0.set_sample_rate(self.samp_rate)

    def get_fft_y_min(self):
        return self.fft_y_min

    def set_fft_y_min(self, fft_y_min):
        self.fft_y_min = fft_y_min

    def get_fft_y_max(self):
        return self.fft_y_max

    def set_fft_y_max(self, fft_y_max):
        self.fft_y_max = fft_y_max

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size

    def get_detect_thre(self):
        return self.detect_thre

    def set_detect_thre(self, detect_thre):
        self.detect_thre = detect_thre
        self.adsb_framer_1.set_threshold(self.detect_thre)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq




def main(top_block_cls=file_ADSB_decode, options=None):
    tb = top_block_cls()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.flowgraph_started.set()

    try:
        input('Press Enter to quit: ')
    except EOFError:
        pass
    tb.stop()
    tb.wait()


if __name__ == '__main__':
    main()
