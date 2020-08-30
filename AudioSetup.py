audio_settings_file = open('AudioSetup.config', 'w')

RATE = input('Enter Sample Rate in Hz (safe choices 44100 and 48000): ')
CHUNK = input('Enter Buffer Size (integer, typical values 256, 512, 1024. Affects latency): ')
latency_in_milliseconds = input('Enter Latency Correction in milliseconds (negative integer): ')
metronome_beeplength = input('Enter length of metronome beeps in buffers (integer, typical values 2 to 10): ')

audio_settings_file.write(RATE + '\n')
audio_settings_file.write(CHUNK + '\n')
audio_settings_file.write(latency_in_milliseconds + '\n')
audio_settings_file.write(metronome_beeplength + '\n')

audio_settings_file.close()
