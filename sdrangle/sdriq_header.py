#!/usr/bin/env python3
import sys
import struct
from datetime import datetime, timezone

def parse_sdriq(filepath):
    try:
        with open(filepath, 'rb') as f:
            header_bytes = f.read(32)
            
        if len(header_bytes) < 32:
            print(f"Error: File '{filepath}' is too small for a 32-byte header.")
            return

        # Decode little-endian structure
        fmt = "<IQQI"
        sample_rate, center_freq, unix_timestamp, sample_size = struct.unpack(fmt, header_bytes[:24])

        # Automatically detect and fix millisecond timestamps
        # Millisecond timestamps from 2001-2050 start with 1xxxxxxxxxxxx (13 digits)
        if unix_timestamp > 50000000000: 
            adjusted_timestamp = unix_timestamp / 1000.0
        else:
            adjusted_timestamp = unix_timestamp

        # Convert timestamp to human-readable string
        try:
            utc_time = datetime.fromtimestamp(adjusted_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        except (ValueError, OverflowError, OSError):
            utc_time = f"Unknown / Invalid Timestamp ({unix_timestamp})"

        # Output results
        print(f"File Name:        {filepath}")
        print(f"Sample Rate:      {sample_rate:,} Hz ({sample_rate / 1e3:.1f} kHz)")
        print(f"Center Frequency: {center_freq:,} Hz ({center_freq / 1e6:.3f} MHz)")
        print(f"Capture Time:     {utc_time}")
        print(f"Sample Size:      {sample_size} bits")
        
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 sdriq_header.py <path_to_sdriq_file>")
        sys.exit(1)
        
    parse_sdriq(sys.argv[1])
