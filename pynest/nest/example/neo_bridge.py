"""
Module to convert NEST output and simulation metadata into the hierarchical Neo
object model.
"""
import numpy as np
import quantities as pq

import neo
import nest


def new_experiment(name="NEST Simulation", description=""):
    """
    Creates a new Neo Block structure to hold a series of calls to
    nest.simulate().

    Parameters:
    -----------

    Returns:
    --------

    """
    return neo.Block(name=name, description=description)


def add_simulation(time, blk, name=None, description=None):
    """
    Performs a call to nest.simulate() and creates a corresponding Neo Segment
    containing kernel parameters before the simulation call.

    Parameters:
    -----------

    Returns:
    --------

    """
    sgmt = neo.Segment(name=name, description=description)

    t_start = nest.GetKernelStatus('time') * pq.ms
    nest.Simulate(time)
    t_stop = nest.GetKernelStatus('time') * pq.ms

    sgmt.annotate(t_start=t_start, t_stop=t_stop)

    # Retrieve parameters
    kernel_parameters = nest.GetKernelStatus()
    for parameter in kernel_parameters:
        # Discard special parameters (e.g., handled above)
        if parameter not in ['time']:
            # Neo annotation should make clear which device
            # contributes the information
            annotation = "kernel_" + parameter
            try:
                sgmt.annotate(
                    **{annotation: kernel_parameters[parameter]})
            except ValueError:
                # For annotations which are of a special type, such as
                # SLILiteral, we store a string representation
                try:
                    sgmt.annotate(**{annotation: str(
                        kernel_parameters[parameter])})
                except:
                    warnings.warn(
                        "pynest.neo_bridge: Cannot create "
                        "annotation for key %parameter", parameter)

    blk.segments.append(sgmt)
    return sgmt


def add_data_from_device(device, blk):
    """
    Extracts data from a NEST device and stores it in a Neo Block structure by
    cutting data into the corresponding segments.

    Parameters:
    -----------

    Returns:
    --------

    """
    spiketrains, channel_annotations, unit_annotations = from_device(device)
    
    channelind = neo.ChannelIndex(
        name = "Recording Device", index=device)
    channelind.annotate(**channel_annotations[0])
    blk.channel_indexes.append(channelind)
    blk.create_relationship()
    
    for spiketrain,unit_annotation in zip(spiketrains, unit_annotations):
        for sgmt in blk.segments:
            spiketrain_cut = spiketrain.time_slice(
                sgmt.annotations["t_start"],sgmt.annotations["t_stop"])

            sgmt.spiketrains.append(spiketrain_cut)
            
            gid = unit_annotation['global_id']
            unit = blk.filter(
                targdict={"global_id": gid}, container=True, objects=neo.Unit)
            if not unit:
                unit = [neo.Unit()]
                unit[0].annotate(**unit_annotation)
                channelind.units.append(unit[0])
            elif len(unit)!=1:
                raise ValueError(
                    "pynest.neo_bridge: Neo Block has multiple units "
                    "for global_id %i." % gid)
            unit[0].spiketrains.append(spiketrain_cut)
            unit[0].create_relationship()


def from_device(device):
    """
    Extracts data from a NEST device and stores it in a Neo SpikeTrain or
    AnalogSignal structure.

    Parameters:
    -----------
    device : tuple of int
    
    Returns:
    --------
    spike_trains : list of neo.SpikeTrain
    channel_annotations : list of dict
    unit_annotations : list of dict
    """
    # Determine whether the device saved to memory or to file
    to_memory = nest.GetStatus(device, 'to_memory')
    to_file = nest.GetStatus(device, 'to_file')

    if not to_memory and not to_file:
        raise ValueError('pynest.neo_bridge: Device did not output data.')

    # Get data from memory
    if to_memory:
        events = nest.GetStatus(device, 'events')[0]
        senders = events['senders']
        times = events['times']

        # For each sender, create a corresponding SpikeTrain object
        spiketrains = []
        channel_annotations=[]
        unit_annotations=[]
        
        for gid in np.unique(senders):
            x = neo.SpikeTrain(
                times[senders == gid] * pq.ms,
                t_start=0. * pq.ms,
                t_stop=nest.GetKernelStatus('time') * pq.ms)

            x.annotate(
                sampling_period=nest.GetKernelStatus('resolution'))
            
            export_annotations = {}

            # Annotate everything from the spike detector and the sender
            for annotation_device, annotation_prefix in zip(
                    [device, (gid,)], ["detector", "sender"]):

                export_annotations[annotation_prefix] = {}
                
                # Retrieve parameters
                device_parameters = nest.GetStatus(annotation_device)[0]
                for parameter in device_parameters:
                    # Discard special parameters (e.g., handled above)
                    if parameter not in ['events']:
                        # Neo annotation should make clear which device
                        # contributes the information
                        annotation = annotation_prefix + "_" + parameter
                        try:
                            if device_parameters[parameter] == None:
                                contents = "None"
                            else:
                                contents = device_parameters[parameter]
                            x.annotate(
                                **{annotation: contents})
                            export_annotations[
                                annotation_prefix][parameter]=contents
                        except ValueError:
                            # For annotations which are of a special type, such as
                            # SLILiteral, we store a string representation
                            try:
                                x.annotate(**{annotation: str(
                                    device_parameters[parameter])})
                                export_annotations[
                                    annotation_prefix][parameter]=str(
                                        device_parameters[parameter])
                            except:
                                warnings.warn(
                                    "pynest.neo_bridge: Cannot create "
                                    "annotation for key %parameter", parameter)

            # Annotate everything from the spike detector
            spiketrains.append(x)
            channel_annotations.append(export_annotations['detector'])
            unit_annotations.append(export_annotations['sender'])

        return spiketrains, channel_annotations, unit_annotations

    # Get data from file
    if to_file:
        # TODO: Implement file based neo_bridge based on the Neo GDF IO
        raise NotImplementedError(
            'pynest.neo_bridge: Loading from file not implemented.')
