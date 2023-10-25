import h5py
import numpy as np

from tqdm.auto import tqdm
from slacube.utils import filter_data_packets, group_by_time
from slacube.geom import MAX_UID

def getPackets( pkts, show_progress = False ):

    mask, uids = filter_data_packets(pkts, return_uids=True)
    data_pkts = pkts[mask]

    return uids, data_pkts

def analyzeExttrig( pkts, mincnt = 5, show_progress = False ):

    mask, uids = filter_data_packets(pkts, return_uids=True)
    data_pkts = pkts[mask]

    output = analyzeExttrig( data_pkts, uids, mincnt, show_progress )

    if len(output) == 1:
        return output[0]
    
    return tuple(output)

def analyzeExttrig( data_pkts, uids, mincnt = 5, show_progress = False ):
    
    summary = np.zeros(
        MAX_UID,
        dtype=[('active',bool), ('mean',float), ('std', float)]
    )
    
    for uid in tqdm(np.unique(uids), disable=not show_progress):
        mask = uids == uid
        if np.count_nonzero(mask) < mincnt:
           continue
        
        data = data_pkts[mask]
        evt = data['dataword']
        
        mean = evt.mean()
        std = evt.std()

        summary[uid] = True, mean, std
        
        output = [summary]

    if len(output) == 1:
        return summary

    return tuple(output)