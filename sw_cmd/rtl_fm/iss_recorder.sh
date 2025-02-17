rtl_fm -f 145800000 -s 11025 -g 29 -p 22 - | sox -t raw -e signed -c 1 -b 16 -r 11025 - recording.wav
