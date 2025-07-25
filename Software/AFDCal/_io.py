from numpy import ndarray
from typing import Union, Optional, Dict, List, Tuple

import scipy.io as sio
import mat73
import numpy as np
import os

import matplotlib.pyplot as plt

def savefig(fig, fig_path,
            bbox_inches='tight',
            dpi=300,
            close_fig=True):
    """
    Save figure
    """
    desertation_dir = os.path.dirname(fig_path)
    if not os.path.exists(desertation_dir):
        os.makedirs(desertation_dir)

    fig.savefig(fig_path, 
            bbox_inches=bbox_inches, dpi=dpi)
    if close_fig:
        plt.close(fig)

def savedata(file: str,
             data: dict,
             save_type: str = 'mat'):
    """
    Save data
    Parameters
    ----------
    file : str
        File name 
    data : dict
        Saving data
        Keys are variable names
        Values are variable values
    save_type : str, optional
        File type
        'mat' - matlab file in .mat format
        'np' - Binary file in NumPy .npy format
        The default is 'mat'.
    """
    desertation_dir = os.path.dirname(file)
    if not os.path.exists(desertation_dir):
        os.makedirs(desertation_dir)
    
    if save_type.lower() == 'mat':
        if os.path.isfile(file):
            os.remove(file)
        sio.savemat(file, data)
    elif save_type.lower() == 'np':
        if os.path.isfile(file):
            os.remove(file)
        with open(file, 'wb') as f:
            np.save(f, data, allow_pickle=True, fix_imports=True)
    else:
        raise ValueError("Unknown 'save_type'. 'save_type' only can be 'mat' or 'np'")
        
def loaddata(file: str,
             save_type: str = 'mat') -> dict:
    """
    Load data
    Parameters
    ----------
    file : str
        File name
    save_type : str, optional
        File type
        'mat' - matlab file in .mat format
        'np' - Binary file in NumPy .npy format
        The default is 'mat'.
    Return
    -----------
    data: dict
        Loaded data
    """
    if save_type.lower() == 'mat':
        data = loadmat(file)
    elif save_type.lower() == 'np':
        with open(file, 'rb') as f:
            data = np.load(f, allow_pickle=True)
            data = data.item()
    else:
        raise ValueError("Unknown 'save_type'. 'save_type' only can be 'mat' or 'np'")
        
    return data

def loadmat(file_path: str) -> dict:
    """
    Load mat file
    Parameters
    -------------------
    file_path: str
        Full file path
    Returns
    -------
    mat_data: dict
        Data in mat file
    """

    try:
        data = _loadmat(file_path)
    except:
        data = mat73.loadmat(file_path)

    return data

def _loadmat(filename):
    '''
    this function should be called instead of direct sio.loadmat
    as it cures the problem of not properly recovering python dictionaries
    from mat files. It calls the function check keys to cure all entries
    which are still mat-objects
    Notes: only works for mat before matlab v7.3
    '''
    def _check_keys(d):
        '''
        checks if entries in dictionary are mat-objects. If yes
        todict is called to change them to nested dictionaries
        '''
        for key in d:
            if isinstance(d[key], sio.matlab.mio5_params.mat_struct):
                d[key] = _todict(d[key])
            elif isinstance(d[key], ndarray):
                d[key] = _tolist(d[key])
        return d

    def _todict(matobj):
        '''
        A recursive function which constructs from matobjects nested dictionaries
        '''
        d = {}
        for strg in matobj._fieldnames:
            elem = matobj.__dict__[strg]
            if isinstance(elem, sio.matlab.mio5_params.mat_struct):
                d[strg] = _todict(elem)
            elif isinstance(elem, ndarray):
                d[strg] = _tolist(elem)
            else:
                d[strg] = elem
        return d

    def _tolist(elem):
        '''
        A recursive function which constructs lists from cellarrays
        (which are loaded as numpy ndarrays), recursing into the elements
        if they contain matobjects.
        '''
        if elem.dtype == object:
            elem_list = []
            for sub_elem in elem:
                if isinstance(sub_elem, sio.matlab.mio5_params.mat_struct):
                    elem_list.append(_todict(sub_elem))
                elif isinstance(sub_elem, ndarray):
                    elem_list.append(_tolist(sub_elem))
                else:
                    elem_list.append(sub_elem)
            return elem_list
        else:
            return elem

    data = sio.loadmat(filename, struct_as_record=False, squeeze_me=True)
    return _check_keys(data)