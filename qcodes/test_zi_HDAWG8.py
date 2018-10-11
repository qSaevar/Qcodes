import unittest
import json
from unittest import mock

import qcodes
import zhinst

from qcodes.instrument_drivers.ZI.ZIHDAWG8 import ZIHDAWG8


class TestZIHDAWG8(unittest.TestCase):
    def setUp(self):
        config_file = 'C:\\Users\\saevarhilmarss\\Projects\\PycQED_py3\\pycqed\\instrument_drivers\\physical_instruments\\ZurichInstruments\\zi_parameter_files\\node_doc_HDAWG8.json'
        with open(config_file, 'r') as f:
            self.paramter_nodes = json.loads(f.read())

    def test_create_parameter(self):
        with mock.patch.object(zhinst.utils, 'create_api_session', return_value=(1, 2, 3)), \
             mock.patch.object(qcodes.instrument_drivers.ZI.ZIHDAWG8.ZIHDAWG8, 'download_device_node_tree',
                               return_value=self.paramter_nodes):
            hdawg = ZIHDAWG8('HDAWG8', 'dev42')
            self.assertTrue(len(hdawg.parameters) > 500)
