#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 21:23:52 2023

@author: yuntse
"""

import argparse
import os
from glob import glob

import h5py
import numpy as np
# import pandas as pd
import json

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

from slacube.exttrig import analyzeExttrig, getPackets
from slacube.geom import load_layout_np

#%% Concatenate the data packets
def concatPackets( files, progress ):

    firstFile = True
    for file in files:

        file = file.replace('\n', '')
        
        with h5py.File( file, 'r' ) as f:
            uids, data_pkts = getPackets( f['packets'], show_progress = progress )
        
            if firstFile:
                pktArray = data_pkts
                uidArray = uids
                firstFile = False
            else:
                pktArray = np.concatenate( (pktArray, data_pkts), axis = -1 )
                uidArray = np.concatenate( (uidArray, uids) )

    return uidArray, pktArray

#%%
def getChannelMask(cfgfiles):
    
    chMask = {}
    for cfgfile in cfgfiles:
        with open(cfgfile, 'r') as f:
            cfg = json.load(f)
            
        reg = cfg['register_values']
        for chid in range(0, 64):
            uid = ((reg['chip_id'] - 11) << 6) + chid
            if uid in chMask.keys():
                print( f'Uid {uid} already exists...')
                continue
            chMask[uid] = reg['channel_mask'][chid]
    
    return chMask

#%%
def make_plot(evt, outfile, title):
    mpl.use('agg')
    sns.set_theme('talk', 'white')

    pix_loc = load_layout_np()

    fig, axes = plt.subplots(2, 1, figsize=(6, 10), sharex=True, sharey=True)

    kwargs = dict(marker='o', s=5, cmap='viridis')
    
    mask = evt['active']
    
    x, y = pix_loc[mask].T

    ax = axes[0]
    sc = ax.scatter(x, y, c = evt[mask]['mean'], vmin = 90, vmax = 125, **kwargs)
    ax.set_aspect('equal')
    fig.colorbar(sc, ax=ax, label='Mean [ADC]')

    ax = axes[1]
    sc = ax.scatter(x, y, c = evt[mask]['std'], vmin = 0, vmax = 20, **kwargs)
    ax.set_aspect('equal')
    fig.colorbar(sc, ax=ax, label='Std [ADC]')

    for ax in axes:
        ax.set_ylabel('y [mm]')
        axes[-1].set_xlabel('x [mm]')

    fig.suptitle(title, fontsize='medium')
    fig.tight_layout()
    # fig.show()

    fig.savefig(outfile)

#%%
def make_diffplot( sig, bkg, outfile, title):
    sns.set_theme('talk', 'white')

    pix_loc = load_layout_np()

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))

    kwargs = dict(marker='o', s=5, cmap='viridis')

    mask = sig['active']
    x, y = pix_loc[mask].T
    d = sig[mask]['mean'] - bkg[mask]['mean']

    sc = ax.scatter(x, y, c = d, vmin = 0, vmax = d.max(), **kwargs)
    ax.set_aspect('equal')
    fig.colorbar(sc, ax=ax, label= r'$\Delta$ADC')

    ax.set_ylabel('y [mm]')
    ax.set_xlabel('x [mm]')

    fig.suptitle(title, fontsize='medium')
    fig.tight_layout()
    fig.show()

    fig.savefig(outfile)

#%%
def save_hdf(exttrig, outfile):
    print('Saving to', outfile)
    with h5py.File(outfile, 'w') as f:
        f.create_dataset('exttrig', data = exttrig, compression = 'gzip')

#%%
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser( description = 'Make a PE map' )
    
    parser.add_argument( '-s', dest = 'sigFileList', type = str, 
                        help = 'input signal filelist' )
    parser.add_argument( '-b', dest = 'bkgFileList', type = str,
                        help = 'input background file list' )
    parser.add_argument( '-o', dest = 'outDir', type = str, default = 'test',
                        help = 'output directory' )
    parser.add_argument( '-c', dest = 'cfgDir', type = str,
                        help = 'configuration directory' )
    parser.add_argument( '-t', dest = 'title', type = str, default = '2023-10-23 Long Fiber',
                        help = 'plot title' )
    parser.add_argument( '-p', dest = 'progress', type = bool, default = False,
                        help = 'show progress' )
    args = parser.parse_args()
    
    
    # try: os.makedirs( args.outDir )
    # except FileExistsError():
    #     pass
    
    outFigName = os.path.join(args.outDir, f'{args.title.replace(" ", "_")}.png')
    
    # Load configuration files
    channelMask = {}
    print( 'Obtaining channel masks...Not used at this moment' )
    cfgfiles = glob(os.path.join(args.cfgDir, 'config-*.json'))
    if len(cfgfiles) == 0:
        raise FileNotFoundError('No config file found', args.cfgDir)
    channelMask = getChannelMask(cfgfiles)
    
    print( f'Processing {args.sigFileList}' )
    
    with open( args.sigFileList, 'r' ) as sflist:
        sigfiles = list(sflist)

    uids, sigPkts = concatPackets( sigfiles, args.progress )

    signal = analyzeExttrig( sigPkts, uids, show_progress = args.progress )
    outFileName = outFigName.replace('.png', '_sig.h5')
    save_hdf(signal, outFileName)

    # make_plot(signal, outName, '2023-10-03_SLACube_LongFiber')
    
    print( f'Processing {args.bkgFileList}' )
    
    with open( args.bkgFileList, 'r' ) as bflist:
        bkgfiles = list(bflist)

    uids, bkgPkts = concatPackets( bkgfiles, args.progress )

    bkg = analyzeExttrig( bkgPkts, uids, show_progress = args.progress )
    outFileName = outFigName.replace('.png', '_bkg.h5')
    save_hdf(bkg, outFileName)

    make_diffplot(signal, bkg, outFigName, f'SLACube: {args.title}' )