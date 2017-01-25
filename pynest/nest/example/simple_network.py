import elephant
import neo
import matplotlib.pyplot as plt
import numpy as np
import quantities as pq

import nest
from nest.neo_bridge import block_from_device, segment_from_device, from_device


nest.ResetKernel()
# nest.SetKernelStatus({'overwrite_files': True})
nest.SetKernelStatus({'resolution': 0.01})

neuron = nest.Create('iaf_psc_delta', 2)
spikedetector = nest.Create('spike_detector')
poisson = nest.Create('poisson_generator', 1, {'rate': 16000.})

# nest.SetStatus(neuron, {'I_e': 300.})
# nest.SetStatus(spikedetector, {'to_file': True, 'to_memory': False})

nest.Connect(neuron, spikedetector)
nest.Connect(poisson, neuron)

nest.Simulate(500.)

my_block = block_from_device(spikedetector)
# spike_trains = from_device(spikedetector)

spike_trains = my_block.filter(gid=2, object=neo.SpikeTrain)

# plt.plot(np.arange(spike_trains[0].t_start, spike_trains, 0.1

plt_time_unit="ms"
ir = elephant.statistics.instantaneous_rate(spike_trains[0], spike_trains[0].annotations['sampling_period'] * pq.ms, kernel=elephant.kernels.GaussianKernel(sigma=30. * pq.ms, invert=False))
plt.plot(ir.times.rescale(plt_time_unit),ir.rescale("Hz"))
plt.xlabel(plt_time_unit)
plt.ylabel('Hz')
plt.show()
