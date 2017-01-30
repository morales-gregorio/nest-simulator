import matplotlib.pyplot as plt

import numpy as np
import quantities as pq

import elephant
import neo

from neo_bridge import new_experiment, add_simulation, add_data_from_device,\
    from_device
import nest

# Set up kernel
nest.ResetKernel()
# nest.SetKernelStatus({'overwrite_files': True})
nest.SetKernelStatus({'resolution': 0.01})

# Create 3 neurons
neuron = nest.Create('iaf_psc_delta', 3)
# Create 1 spike detector
spikedetector = nest.Create('spike_detector')
# Create a Poisson generator
poisson = nest.Create('poisson_generator', 1, {'rate': 16000.})

# Modify parameters
# nest.SetStatus(neuron, {'I_e': 300.})
# nest.SetStatus(spikedetector, {'to_file': True, 'to_memory': False})

# Connect
nest.Connect(neuron, spikedetector)
nest.Connect(poisson, neuron)

# Simulate 500 ms
nest.Simulate(500.)

spike_trains = from_device(spikedetector)[0]

plt_time_unit="ms"
rate_profile = elephant.statistics.instantaneous_rate(
    spike_trains[0], 
    spike_trains[0].annotations['sampling_period'] * pq.ms, 
    kernel=elephant.kernels.GaussianKernel(sigma=30. * pq.ms, invert=False))
plt.plot(
    rate_profile.times.rescale(plt_time_unit), rate_profile.rescale("Hz"))
plt.xlabel(plt_time_unit)
plt.ylabel('Hz')
plt.show()
