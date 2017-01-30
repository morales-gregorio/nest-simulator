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

simulation_block = new_experiment()

print "Status of NEST Kernel before simulation"
ks_before = nest.GetKernelStatus()
for s in ks_before:
    print(s, ": ", ks_before[s])
print("")

# Create 3 neurons
neuron = nest.Create('iaf_psc_delta', 3)
# Create 1 spike detector
spikedetector = nest.Create('spike_detector')
# Create a Poisson generator
poisson = nest.Create('poisson_generator', 1, {'rate': 16000.})

# nest.SetStatus(neuron, {'I_e': 300.})
# nest.SetStatus(spikedetector, {'to_file': True, 'to_memory': False})

nest.Connect(neuron, spikedetector)
nest.Connect(poisson, neuron)

simulation_segment = add_simulation(500., simulation_block)
simulation_segment2 = add_simulation(1500., simulation_block)
#nest.Simulate(500.)

print("Changes of status of NEST Kernel after simulation")
ks_after = nest.GetKernelStatus()
for s in ks_after:
    if ks_before[s] != ks_after[s]:
        print(s, ": ", ks_before[s], "->", ks_after[s])
print("")

print("Status of Neuron")
neus = nest.GetStatus(neuron)[1]
for s in neus:
    print(s, ": ", neus[s])
print("")

print("Status of Spike Detector")
spds = nest.GetStatus(spikedetector)[0]
for s in spds:
    print(s, ": ", spds[s])
print("")

add_data_from_device(spikedetector, simulation_block)

print simulation_block.segments[0].annotations['t_start']
print simulation_block.segments[0].annotations['t_stop']
print simulation_block.segments[1].annotations['t_start']
print simulation_block.segments[1].annotations['t_stop']
print simulation_block.segments[0].spiketrains[0].t_start
print simulation_block.segments[0].spiketrains[0].t_stop
print simulation_block.segments[0].spiketrains[1].t_start
print simulation_block.segments[0].spiketrains[1].t_stop
print simulation_block.segments[1].spiketrains[0].t_start
print simulation_block.segments[1].spiketrains[0].t_stop
print simulation_block.channel_indexes
print simulation_block.channel_indexes[0].units

spike_trains = simulation_block.filter(gid=1, objects=neo.SpikeTrain)


#spike_trains = from_device(spikedetector)

# print("Annotations of spike train 1")
# for s in spike_trains[0].annotations:
#     print(s, ": ", spike_trains[0].annotations[s])
# print("")


# my_block = block_from_device(spikedetector)
# spike_trains = my_block.filter(gid=2, object=neo.SpikeTrain)

# plt.plot(np.arange(spike_trains[0].t_start, spike_trains, 0.1

# plt_time_unit="ms"
# ir = elephant.statistics.instantaneous_rate(spike_trains[0], spike_trains[0].annotations['sampling_period'] * pq.ms, kernel=elephant.kernels.GaussianKernel(sigma=30. * pq.ms, invert=False))
# plt.plot(ir.times.rescale(plt_time_unit),ir.rescale("Hz"))
# plt.xlabel(plt_time_unit)
# plt.ylabel('Hz')
# plt.show()
