from qcodes.instrument_drivers.ZI.ZIHDAWG8 import ZIHDAWG8

hdawg = ZIHDAWG8('HDAWG8','dev555')

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

hdawg.upload_sequence_program(awg_program)