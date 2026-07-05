import csv

# CHANGE THIS to your actual amateur radio callsign
MY_CALLSIGN = "A6009SWL"

def clean_key(key):
    """Removes spaces, quotes, or invisible characters from column headers."""
    if key is None:
        return ""
    return key.strip().replace('"', '').replace("'", "").lower()

with open('92a3da5c3df97261604c331a69d20945.csv', mode='r', encoding='utf-8-sig') as infile:
    # Automatically detect if your file uses tabs, commas, or semicolons
    sample = infile.read(2048)
    infile.seek(0)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=',\t;')
        delimiter = dialect.delimiter
    except Exception:
        delimiter = ',' # Fallback to comma if detection fails

    # Read the file with the detected delimiter
    reader = csv.reader(infile, delimiter=delimiter)
    
    # Read the first line (headers) and clean them up
    raw_headers = next(reader)
    headers = [clean_key(h) for h in raw_headers]
    
    # Print the detected headers to the terminal for verification
    print(f"DEBUG: Detected columns -> {headers}\n")
    
    # Verify if 'time' exists anywhere in the cleaned list
    if 'time' not in headers:
        raise KeyError(f"Could not find 'time' column. Cleaned headers found: {headers}")

    # Open output file
    with open('wspr_output.adi', mode='w', encoding='utf-8') as outfile:
        outfile.write("WSPR Live Export to ADIF\n<ADIF_VER:5>3.1.4\n<EOH>\n")
        
        for row_data in reader:
            # Skip empty rows
            if not row_data or len(row_data) < len(headers):
                continue
                
            # Create a dictionary using our cleaned headers
            row = dict(zip(headers, row_data))
            
            # Clean up the timestamps (Expected format: YYYY-MM-DD HH:MM:SS)
            raw_time = row['time'].replace('-', '').replace(':', '').replace(' ', '')
            date_str = raw_time[:8]   # YYYYMMDD
            time_str = raw_time[8:14] # HHMMSS
            
            # Fallbacks for empty timestamps
            if not date_str or not time_str:
                continue
                
            # Determine if you were the transmitter or receiver in this row
            if row.get('tx_sign') == MY_CALLSIGN:
                contact_call = row.get('rx_sign', '')
                contact_grid = row.get('rx_loc', '')
                rst_tag = f"<RST_SENT:{len(row.get('snr', ''))}>{row.get('snr', '')}"
            else:
                contact_call = row.get('tx_sign', '')
                contact_grid = row.get('tx_loc', '')
                rst_tag = f"<RST_RCVD:{len(row.get('snr', ''))}>{row.get('snr', '')}"
                
            try:
                freq_mhz = float(row.get('frequency', 0)) / 1000000
                freq_str = f"{freq_mhz:.6f}"
            except ValueError:
                freq_str = "0.000000"
            
            # Construct and write ADIF line
            outfile.write(f"<QSO_DATE:{len(date_str)}>{date_str}")
            outfile.write(f"<TIME_ON:{len(time_str)}>{time_str}")
            outfile.write(f"<STATION_CALLSIGN:{len(MY_CALLSIGN)}>{MY_CALLSIGN}")
            outfile.write(f"<CALL:{len(contact_call)}>{contact_call}")
            outfile.write(f"<GRIDSQUARE:{len(contact_grid)}>{contact_grid}")
            outfile.write(f"<FREQ:{len(freq_str)}>{freq_str}")
            outfile.write(f"<MODE:4>WSPR {rst_tag} <EOR>\n")

print("Generated wspr_output.adi successfully!")
