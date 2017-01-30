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

simulation_block = new_experiment(
    name="MyStimulationNetwork", 
    description="Simulation of a primitive 3-neuron animal receiving a "
    "light stimulus")

print("Status of NEST Kernel before simulation")
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

nest.Connect(neuron, spikedetector)
nest.Connect(poisson, neuron)

simulation_segment = add_simulation(
    time=500., 
    blk=simulation_block,
    name="StimulusOff",
    description="Baseline activity before stimulus.")

nest.SetStatus(poisson, {'rate': 32000.})

simulation_segment2 = add_simulation(
    time=1500., 
    blk=simulation_block, 
    name="StimulusOn",
    description="Stimulus turned on here.")

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

# Add results to Neo Block
add_data_from_device(spikedetector, simulation_block)

# Extract spike trains of Unit 1
spike_trains = simulation_block.filter(gid=1, objects=neo.SpikeTrain)

