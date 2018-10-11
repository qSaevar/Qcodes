from qcodes.instrument_drivers.ZI.ZIHDAWG8 import ZIHDAWG8
import numpy as np

hdawg = ZIHDAWG8('AWG8','dev8049')

hdawg.set_channel_grouping(0)

hdawg.start_channel(5)
hdawg.stop_channel(5)

awg_program = """ 
// Wave 1: Sawtooth that is 4000 samples long and repeated 4 times 
wave wave_1 = sawtooth(4000, 1, 0, 4);  

// Wave 2: Single sawtooth that is 4000 samples long
wave wave_2 = sawtooth(4000, 1, 0, 1);

while (true){
    // Play wave_1 on output 1 and wave_2 on output 2:
    playWave(wave_1, wave_2);
}
"""

awg_program2 = """ 
// Wave 1: Sawtooth that is 4000 samples long and repeated 4 times 
wave wave_1 = zeros(4000);

while (true){
    // Play wave_1 on output 1 and wave_2 on output 2:
    playWave(wave_1);
}
"""

hdawg.upload_sequence_program(2, awg_program2)
hdawg.start_awg(2)
hdawg.start_channel(5)
hdawg.start_channel(4)
waveform_2 = np.sin(np.linspace(0, 2*np.pi, 4000))
hdawg.stop_awg(2)
hdawg.upload_waveform(2, waveform_2, 0)
hdawg.start_awg(2)
hdawg.stop_channel(5)
hdawg.stop_channel(4)
hdawg.stop_awg(2)

