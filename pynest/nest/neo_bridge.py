import elephant
import neo
import matplotlib.pyplot as plt
import numpy as np
import quantities as pq

import nest


def block_from_device(device, block=None):
    if block is None:
        block = neo.Block()
    block.segments.append(segment_from_device(device))
    return block


def segment_from_device(device):
    sgmt = neo.Segment()
    sgmt.spiketrains.extend(from_device(device))
    return sgmt


def from_device(device):
    to_memory = nest.GetStatus(device, 'to_memory')
    to_file = nest.GetStatus(device, 'to_file')

    if not to_memory and not to_file:
        raise ValueError('sadasdasd')

    if to_memory:
        events = nest.GetStatus(device, 'events')[0]
        senders = events['senders']
        times = events['times']

        st = []
        for gid in np.unique(senders):
            x = neo.SpikeTrain(times[senders == gid] * pq.ms, t_start=0. * pq.ms, t_stop=nest.GetKernelStatus('time') * pq.ms)
            x.annotate(gid=gid, sampling_period=nest.GetKernelStatus('resolution'))
            st.append(x)

        return st

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

# my_block = block_from_device(spikedetector)
spike_trains = from_device(spikedetector)

# print my_block.filter(gid=2, object=neo.SpikeTrain)

#plt.plot(np.arange(spike_trains[0].t_start, spike_trains, 0.1

ir = elephant.statistics.instantaneous_rate(spike_trains[0], spike_trains[0].annotations['sampling_period'] * pq.ms, kernel=elephant.kernels.GaussianKernel(sigma=30. * pq.ms, invert=False))
plt.plot(ir.times.rescale("ms"),ir)
plt.xlabel('ms')
plt.show()
