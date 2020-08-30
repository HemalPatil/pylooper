loop_settings_file = open('LoopSetup.config', 'w')

tempo = input('Enter Tempo in BPM: ')
beats_per_bar = input('How many beats per bar?: ')
bars_per_loop = input('How many bars per loop?: ')
bars_of_countin = input('How many bars of count-in?: ')

loop_settings_file.write(tempo + '\n')
loop_settings_file.write(beats_per_bar + '\n')
loop_settings_file.write(bars_per_loop + '\n')
loop_settings_file.write(bars_of_countin + '\n')

loop_settings_file.close()
