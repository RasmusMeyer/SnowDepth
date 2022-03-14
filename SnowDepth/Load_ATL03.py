## Loads ICESat-2 ATL03 photons into Python and converts to Pandas dataframe

# Package import
import os
import h5py
import numpy as np
import pandas as pd

# Get ATL03 function
def get_ATL03(f,beam):
    """
    Extracts photon data from .h5 file

    Inputs:
        f: ATL03 .h5 file
        beam: ICESat-2 has 6 beams [gt1l, gt2l, gt3l, gt1r, gt2r, gt3r]
    
    Outputs:
        df: Pandas dataframe with coordinates, height, date and confidence level per photon

    """
    # height of each received photon, relative to the WGS-84 ellipsoid (with some, not all corrections applied, see background info above)
    heights=f[beam]['heights']['h_ph'][:]
    # latitude (decimal degrees) of each received photon
    lats=f[beam]['heights']['lat_ph'][:]
    # longitude (decimal degrees) of each received photon
    lons=f[beam]['heights']['lon_ph'][:]
    # seconds from ATLAS Standard Data Product Epoch. use the epoch parameter to convert to gps time
    dt=f[beam]['heights']['delta_time'][:]
    # confidence level associated with each photon event
    # -2: TEP
    # -1: Events not associated with a specific surface type
    #  0: noise
    #  1: buffer but algorithm classifies as background
    #  2: low
    #  3: medium
    #  4: high
    # Surface types for signal classification confidence
    # 0=Land; 1=Ocean; 2=SeaIce; 3=LandIce; 4=InlandWater    
    conf=f[beam]['heights']['signal_conf_ph'][:,0] #choose column 2 for confidence of sea ice photons
    # number of ATL03 20m segments
    n_seg, = f[beam]['geolocation']['segment_id'].shape
    #GEOID
    geoid = f[beam]['geophys_corr']['geoid'][:]
    # first photon in the segment (convert to 0-based indexing)
    Segment_Index_begin = f[beam]['geolocation']['ph_index_beg'][:] - 1
    # number of photon events in the segment
    Segment_PE_count = f[beam]['geolocation']['segment_ph_cnt'][:]
    # along-track distance for each ATL03 segment
    Segment_Distance = f[beam]['geolocation']['segment_dist_x'][:]
    # along-track distance (x) for photon events
    x_atc = np.copy(f[beam]['heights']['dist_ph_along'][:])
    # cross-track distance (y) for photon events
    y_atc = np.copy(f[beam]['heights']['dist_ph_across'][:])

    for j in range(n_seg):
        # index for 20m segment j
        idx = Segment_Index_begin[j]
        # number of photons in 20m segment
        cnt = Segment_PE_count[j]
        # add segment distance to along-track coordinates
        x_atc[idx:idx+cnt] += Segment_Distance[j]
        #geoid
        #geoid[idx:idx+cnt] += geoid[j]


    df=pd.DataFrame({'lats':lats,'lons':lons,'x':x_atc,'y':y_atc,'heights':heights,'dt':dt,'conf':conf})
    return df

# Load ATL03 function
def load_ATL03(path, date, beam, resolution):
    """
    Loads ICESat-2 photons into Python and converts to Pandas dataframe

    Inputs:
        path: Path to AOI-folder
        date: Folder for date of observation (e.g. 20210211)
        beam: ICESat-2 has 6 beams [gt1l, gt2l, gt3l, gt1r, gt2r, gt3r]
        resolution: Can be set to either 10 or 100 m depending on distance between points

    Outputs:
        df: Pandas dataframe with coordinates, height and date for photons with confidence level > 2
        geoid: Reference geoid information per defined resolution
    """
    # Defines ATL03 path based on AOI-path and date
    ATL03_path = path + date + '/ATL03/'
    for file in os.listdir(ATL03_path):
        if file.endswith('.h5'):
            fname = file
    # Opens .h5 file with h5py library
    f = h5py.File(ATL03_path+fname,'r')
    # Get geoid information per 20 m segment
    geoid = f[beam]['geophys_corr']['geoid'][:]
    # Convert to 10 m resolution
    if resolution == 10:
        geoid = list(np.repeat(geoid, 2))
    # Convert to 100 m resolution
    if resolution == 100:
        geoid = geoid[::5]
        geoid = geoid.tolist()
    # Call get_ATL03 function
    df = get_ATL03(f,beam)
    # Select photons with a medium or high confidence level (> 2)
    df = df[df['conf'] > 2]
    # Calculate along-track distance
    df['AT_dist']=df.x-df.x.values[0]
    return df, geoid