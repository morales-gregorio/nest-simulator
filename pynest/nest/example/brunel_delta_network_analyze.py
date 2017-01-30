import os
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
from numpy import exp


import neo
from neo.io.nixio import NixIO 
import elephant.spike_train_correlation
import elephant.conversion
import quantities as pq


if __name__ == '__main__':
    print("Loading data")
    filename = "brunel.nix"
    outfile = NixIO(filename, mode="ro")
    loaded_block = outfile.read_block()

    print("Selecting excitatory neurons")
    spike_trains = loaded_block.filter(
        detector_label="brunel-py-ex", objects=neo.SpikeTrain)
    
    print("Calculating cross-correlation")
    cc=elephant.spike_train_correlation.corrcoef(
        elephant.conversion.BinnedSpikeTrain(
            spike_trains,binsize=1.*pq.ms),
        binary=False)

    plt.figure()
    plt.pcolor(cc)
    plt.show()
