"""
Module to convert NEST output and simulation metadata into the hierarchical Neo
object model.
"""
import numpy as np
import quantities as pq

import neo
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
    """
    Extracts data from a NEST device and stores it in a Neo SpikeTrain or
    AnalogSignal structure.
    
    Parameters:
    -----------
    
    Returns:
    --------
    
    """
    
    # Determine whether the device saved to memory or to file
    to_memory = nest.GetStatus(device, 'to_memory')
    to_file = nest.GetStatus(device, 'to_file')

    if not to_memory and not to_file:
        raise ValueError('pynest.neo_bridge: Device did not output to memory.')

    # Get data from memory
    if to_memory:
        events = nest.GetStatus(device, 'events')[0]
        senders = events['senders']
        times = events['times']

        # For each sender, create a corresponding SpikeTrain object
        st = []
        for gid in np.unique(senders):
            x = neo.SpikeTrain(
                times[senders == gid] * pq.ms, 
                t_start=0. * pq.ms, 
                t_stop=nest.GetKernelStatus('time') * pq.ms)
            
            x.annotate(
                gid=gid)
                #sampling_period=nest.GetKernelStatus('resolution'))

            device_parameters = nest.GetStatus(device)[0]
            for s in device_parameters:
                # These 3 parameters are special and are handled above
                if s not in ['events', 'senders', 'times']:
                    try:
                        x.annotate(**{s: device_parameters[s]})
                    except ValueError:
                        # For annotations which are of a special type, such as
                        # SLILiteral, we store a string representation
                        try:
                            x.annotate(**{s: str(device_parameters[s])})
                        except:
                            warnings.warn(
                                "pynest.neo_bridge: Cannot create annotation "
                                " for key %s", s)
                    
            
            st.append(x)

        return st
    
    # Get data from file
    if to_file:
        raise NotImplementedError(
            'pynest.neo_bridge: Loading from file not implemented.')
