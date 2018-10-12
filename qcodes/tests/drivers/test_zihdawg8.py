import unittest
from unittest.mock import patch, MagicMock

import zhinst

import qcodes
from qcodes.instrument_drivers.ZI.ZIHDAWG8 import ZIHDAWG8
from qcodes.utils import validators


class TestZIHDAWG8(unittest.TestCase):
    def setUp(self):
        self.node_tree = {"/DEV8049/SYSTEM/AWG/CHANNELGROUPING": {
            "Node": "/DEV8049/SYSTEM/AWG/CHANNELGROUPING",
            "Description": "Sets the channel grouping mode of the device.",
            "Properties": "Read, Write, Setting",
            "Type": "Integer (enumerated)",
            "Unit": "None",
            "Options": {
                "0": "Use the outputs in groups of 2. One sequencer program controls 2 outputs ",
                "1": "Use the outputs in groups of 4. One sequencer program controls 4 outputs ",
                "2": "Use the outputs in groups of 8. One sequencer program controls 8 outputs "
            }
        }, "/DEV8049/SIGOUTS/0/ON": {
            "Node": "/DEV8049/SIGOUTS/0/ON",
            "Description": "Enabling/Disabling the Signal Output. Corresponds to the blue LED indicator",
            "Properties": "Read, Write, Setting",
            "Type": "Integer (64 bit)",
            "Unit": "None"
        }, "/DEV8049/SYSTEM/OWNER": {
            "Node": "/DEV8049/SYSTEM/OWNER",
            "Description": "Returns the current owner of the device (IP).",
            "Properties": "Read",
            "Type": "String",
            "Unit": "None"
        }, "/DEV8049/SINES/0/AMPLITUDES/0": {
            "Node": "/DEV8049/SINES/0/AMPLITUDES/0",
            "Description": "Sets the peak amplitude that the sine signal contributes to the signal output. Note that\
             the last index is either 0 or 1 and will map to the pair of outputs given by the first index.\
              (e.g. sines/3/amplitudes/0 corresponds to wave output 2)",
            "Properties": "Read, Write, Setting",
            "Type": "Double",
            "Unit": "None"
        }, "/DEV8049/AWGS/1/WAVEFORM/MEMORYUSAGE": {
            "Node": "/DEV8049/AWGS/1/WAVEFORM/MEMORYUSAGE",
            "Description": "Amount of the used waveform data relative to the device cache memory. The cache memory \
            provides space for 32 kSa of waveform data. Memory Usage over 100% means that waveforms must be loaded from\
             the main memory (128 MSa per channel) during playback, which can lead to delays.",
            "Properties": "Read",
            "Type": "Double",
            "Unit": "%"
        }}

    def test_create_parameters_from_node_tree(self):
        with patch.object(zhinst.utils, 'create_api_session', return_value=3 * (MagicMock(),)), \
             patch.object(qcodes.instrument_drivers.ZI.ZIHDAWG8.ZIHDAWG8, 'download_device_node_tree',
                          return_value=self.node_tree):
            hdawg8 = ZIHDAWG8('Name', 'dev-test')

            self.assertIn('system_awg_channelgrouping', hdawg8.parameters)
            with self.assertRaises(ValueError):
                hdawg8.system_awg_channelgrouping.set(4)
            self.assertEqual('None', hdawg8.system_awg_channelgrouping.unit)
            self.assertEqual('system_awg_channelgrouping', hdawg8.system_awg_channelgrouping.name)
            self.assertIsNotNone(hdawg8.system_awg_channelgrouping.vals)
            self.assertIsInstance(hdawg8.system_awg_channelgrouping.vals, validators.Enum)

            self.assertIn('sigouts_0_on', hdawg8.parameters)
            self.assertEqual('None', hdawg8.sigouts_0_on.unit)
            self.assertEqual('sigouts_0_on', hdawg8.sigouts_0_on.name)
            self.assertIsNone(hdawg8.sigouts_0_on.vals)

            self.assertIn('system_owner', hdawg8.parameters)
            self.assertEqual('None', hdawg8.system_owner.unit)
            self.assertEqual('system_owner', hdawg8.system_owner.name)
            self.assertIsNone(hdawg8.system_owner.vals)

            self.assertIn('sines_0_amplitudes_0', hdawg8.parameters)
            self.assertEqual('None', hdawg8.sines_0_amplitudes_0.unit)
            self.assertEqual('sines_0_amplitudes_0', hdawg8.sines_0_amplitudes_0.name)
            self.assertIsNone(hdawg8.sines_0_amplitudes_0.vals)

            self.assertIn('awgs_1_waveform_memoryusage', hdawg8.parameters)
            self.assertEqual('%', hdawg8.awgs_1_waveform_memoryusage.unit)
            self.assertEqual('awgs_1_waveform_memoryusage', hdawg8.awgs_1_waveform_memoryusage.name)
            self.assertIsNone(hdawg8.awgs_1_waveform_memoryusage.vals)
