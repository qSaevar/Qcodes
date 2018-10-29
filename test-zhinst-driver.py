# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Example

Demonstrate how to connect to a Zurich Instruments UHF Lock-in Amplifier and
upload and run an AWG program.
"""

# Copyright 2016 Zurich Instruments AG

from __future__ import print_function
import os
import time
import textwrap
import numpy as np
import zhinst.utils


def run_example(device_id, do_plot=False):
    """
    Run the example: Connect to a Zurich Instruments UHF Lock-in Amplifier or
    UHFAWG, upload and run a basic AWG sequence program. It then demonstrates
    how to upload (replace) a waveform without changing the sequencer program.

    Requirements:

      UHFLI with UHF-AWG Arbitrary Waveform Generator Option.

       Hardware configuration: Connect signal output 1 to signal input 1 with a
       BNC cable.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      do_plot (bool, optional): Specify whether to plot the signal measured by the scope
        output. Default is no plot output.

    Returns:

      data: Data structure returned by the Scope

    Raises:

      Exception: If the UHF-AWG Option is not installed.

      RuntimeError: If the device is not "discoverable" from the API.

    See the "LabOne Programing Manual" for further help, available:
      - On Windows via the Start-Menu:
        Programs -> Zurich Instruments -> Documentation
      - On Linux in the LabOne .tar.gz archive in the "Documentation"
        sub-folder.
    """

    # Settings
    apilevel_example = 6  # The API level supported by this example.
    err_msg = "This example can only be ran on either a UHFAWG or a UHF with the AWG option enabled."
    # Call a zhinst utility function that returns:
    # - an API session `daq` in order to communicate with devices via the data server.
    # - the device ID string that specifies the device branch in the server's node hierarchy.
    # - the device's discovery properties.
    (daq, device, _) = zhinst.utils.create_api_session(device_id, apilevel_example, required_devtype='UHF',
                                                       required_options=['AWG'], required_err_msg=err_msg)
    zhinst.utils.api_server_version_check(daq)

    # Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
    zhinst.utils.disable_everything(daq, device)

    # Now configure the instrument for this experiment. The following channels
    # and indices work on all device configurations. The values below may be
    # changed if the instrument has multiple input/output channels and/or either
    # the Multifrequency or Multidemodulator options installed.
    # out_channel = 0
    # out_mixer_channel = 3
    in_channel = 0
    osc_index = 0
    # awg_channel = 0
    frequency = 1e6
    amplitude = 1.0

    exp_setting = [
        ['/%s/sigins/%d/imp50' % (device, in_channel), 1],
        ['/%s/sigins/%d/ac' % (device, in_channel), 0],
        ['/%s/sigins/%d/diff' % (device, in_channel), 0],
        ['/%s/sigins/%d/range' % (device, in_channel), 1],
        ['/%s/oscs/%d/freq' % (device, osc_index), frequency]
    ]
    daq.set(exp_setting)

    daq.sync()

    # Number of points in AWG waveform
    AWG_N = 2000

    # Configure the Scope for measurement
    # 'channels/0/inputselect' : the input channel for the scope:
    #   0 - signal input 1
    daq.setInt('/%s/scopes/0/channels/0/inputselect' % (device), in_channel)
    # 'time' : timescale of the wave, sets the sampling rate to 1.8GHz/2**time.
    #   0 - sets the sampling rate to 1.8 GHz
    #   1 - sets the sampling rate to 900 MHz
    #   ...
    #   16 - sets the sampling rate to 27.5 kHz
    daq.setInt('/%s/scopes/0/time' % device, 0)
    # Disable the scope.
    daq.setInt('/%s/scopes/0/enable' % device, 0)
    # Configure the length of the scope shot.
    daq.setInt('/%s/scopes/0/length' % device, 10000)
    # Now configure the scope's trigger to get aligned data
    # 'trigenable' : enable the scope's trigger (boolean).
    daq.setInt('/%s/scopes/0/trigenable' % device, 1)
    # Specify the trigger channel:
    #
    # Here we trigger on the signal from UHF signal input 1. If the instrument has the DIG Option installed we could
    # trigger the scope using an AWG Trigger instead (see the `setTrigger(1);` line in `awg_program` above).
    # 0:   Signal Input 1
    # 192: AWG Trigger 1
    trigchannel = 0
    daq.setInt('/%s/scopes/0/trigchannel' % device, trigchannel)
    if trigchannel == 0:
        # Trigger on the falling edge of the negative blackman waveform `w0` from our AWG program.
        daq.setInt('/%s/scopes/0/trigslope' % device, 2)
        daq.setDouble('/%s/scopes/0/triglevel' % device, -0.600)
        # Set hysteresis triggering threshold to avoid triggering on noise
        # 'trighysteresis/mode' :
        #  0 - absolute, use an absolute value ('scopes/0/trighysteresis/absolute')
        #  1 - relative, use a relative value ('scopes/0trighysteresis/relative') of the trigchannel's input range
        #      (0.1=10%).
        daq.setDouble('/%s/scopes/0/trighysteresis/mode' % device, 0)
        daq.setDouble('/%s/scopes/0/trighysteresis/relative' % device, 0.025)
        # Set a negative trigdelay to capture the beginning of the waveform.
        trigdelay = -1.0e-6
        daq.setDouble('/%s/scopes/0/trigdelay' % device, trigdelay)
    else:
        # Assume we're using an AWG Trigger, then the scope configuration is simple: Trigger on rising edge.
        daq.setInt('/%s/scopes/0/trigslope' % device, 1)
        # Set trigdelay to 0.0: Start recording from when the trigger is activated.
        trigdelay = 0.0
        daq.setDouble('/%s/scopes/0/trigdelay' % device, trigdelay)
    trigreference = 0.0
    # The trigger reference position relative within the wave, a value of 0.5 corresponds to the center of the wave.
    daq.setDouble('/%s/scopes/0/trigreference' % device, trigreference)
    # Set the hold off time in-between triggers.
    daq.setDouble('/%s/scopes/0/trigholdoff' % device, 0.025)

    # Set up the Scope Module.
    scopeModule = daq.scopeModule()
    scopeModule.set('scopeModule/mode', 1)
    scopeModule.subscribe('/' + device + '/scopes/0/wave')
    # 'single' : only get a single scope shot.
    #   0 - take continuous shots
    #   1 - take a single shot
    daq.setInt('/%s/scopes/0/single' % device, 1)

    scopeModule.execute()

    # Start the scope...
    daq.setInt('/%s/scopes/0/enable' % device, 1)
    daq.sync()
    time.sleep(1.0)

    daq.setInt('/%s/awgs/0/userregs/0' % device, 1)

    # Read the scope data with timeout.
    local_timeout = 2.0
    records = 0
    while (records < 1) and (local_timeout > 0):
        time.sleep(0.1)
        local_timeout -= 0.1
        records = scopeModule.getInt("scopeModule/records")

    # Disable the scope.
    daq.setInt('/%s/scopes/0/enable' % device, 0)

    data_read = scopeModule.read(True)
    wave_nodepath = '/{}/scopes/0/wave'.format(device)
    assert wave_nodepath in data_read, "Error: The subscribed data `{}` was returned.".format(wave_nodepath)
    data = data_read[wave_nodepath][0][0]

    f_s = 1.8e9  # sampling rate of scope and AWG
    for n in range(0, len(data['channelenable'])):
        p = data['channelenable'][n]
        if p:
            y_measured = data['wave'][n]
            x_measured = np.arange(-data['totalsamples'], 0) * data['dt'] + \
                         (data['timestamp'] - data['triggertimestamp']) / f_s

    # Compare expected and measured signal
    full_scale = 0.75

    # Correlate measured and expected signal

    if do_plot:
        # The shift between measured and expected signal depends among other things on cable length.
        # We simply determine the shift experimentally and then plot the signals with an according correction
        # on the horizontal axis.
        import matplotlib.pyplot as plt
        print('Plotting the expected and measured AWG signal.')
        x_unit = 1e-9
        plt.figure(1)
        plt.clf()
        plt.title('Measured and expected AWG Signals')
        plt.plot(x_measured / x_unit, y_measured, label='measured')
        plt.grid(True)
        plt.autoscale(axis='x', tight=True)
        plt.legend(loc='upper left')
        plt.xlabel('Time, relative to trigger (ns)')
        plt.ylabel('Voltage (V)')
        plt.draw()
        plt.show()

    return data_read


run_example('dev', True)
