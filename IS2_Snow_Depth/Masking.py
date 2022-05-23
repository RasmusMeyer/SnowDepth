## Masks out unwanted data from the dataframe containing snow depths

# Package import
import rasterio
import numpy as np
from astropy.convolution import convolve, convolve_fft

# Function for masking out unwanted data
def masking(df_sd, path, date, slope_threshold):
    '''
    Masks out unwanted data from the dataframe containing snow depths

    Input:
        df_sd: Dataframe containing points with snow depths and coordinates
        path: Path to AOI-folder used to access slope and binary masks
        date: Folder for date of observation (e.g. 20210211) used to access binary mask
        slope_threshold: Mask out points on slopes above X degrees (e.g. 8)

    Output:
        df_sd_masked: Dataframe containing points with snow depths and coordinates - unwanted data has been masked out
    '''
    # Rename df
    df_sd_masked = df_sd
    # Get coordinates
    coords = [(x,y) for x, y in zip(df_sd_masked.geometry.x, df_sd_masked.geometry.y)]
    # Get slope mask as variable
    SLOPE = path[:-7] + '/Masks/Slope.tif'
    # Get binary mask as variable
    Binary_Mask = path[:-7] + '/DEM/Binary_Mask.tif'
    # Create a list containing both masks
    listofmasks=[SLOPE, Binary_Mask]
    # List containing the names of the masks as strings
    listofmasksname=['SLOPE', 'Binary_Mask']
    
    # Counter
    i = 0
    # Read each mask and sample values into the dataframe
    for mask in listofmasks:
        src = rasterio.open(mask)
        df_sd_masked[listofmasksname[i]] = [x[0] for x in src.sample(coords)]
        i=i+1
    
    print('Remaining points before masking: ',df_sd_masked.shape[0])
    

    #df_sd_masked.loc[df_sd_masked['SLOPE'] > slope_threshold ,'SD'] = np.nan
    df_sd_masked.loc[df_sd_masked['SLOPE'] > slope_threshold ,'DEM'] = np.nan
    df_sd_masked.loc[df_sd_masked['SLOPE'] > slope_threshold ,'Surface_corr'] = np.nan
    
    df_sd_masked.loc[df_sd_masked['SLOPE'] < 1 ,'DEM'] = np.nan
    df_sd_masked.loc[df_sd_masked['SLOPE'] < 1 ,'Surface_corr'] = np.nan


    
    # Mask out points on slope over X degrees (e.g. 8)
    #df_sd_masked = df_sd_masked[df_sd_masked['SLOPE'] < slope_threshold]
    #df_sd_masked = df_sd_masked[df_sd_masked['SLOPE'] > 1]
    print('Remaining points after applying slope mask: ',df_sd_masked.shape[0])
    
    # Mask out points on ICESAT-2 slope over X degrees
    df_sd_masked.loc[df_sd_masked['SLOPE_IS2'] > slope_threshold ,'DEM'] = np.nan
    df_sd_masked.loc[df_sd_masked['SLOPE_IS2'] > slope_threshold ,'Surface_corr'] = np.nan
    
    df_sd_masked.loc[df_sd_masked['SLOPE_IS2'] < 1 ,'DEM'] = np.nan
    df_sd_masked.loc[df_sd_masked['SLOPE_IS2'] < 1 ,'Surface_corr'] = np.nan

    
    # Mask out points that are not 1
    df_sd_masked.loc[df_sd_masked['Binary_Mask'] < 1 ,'DEM'] = np.nan
    df_sd_masked.loc[df_sd_masked['Binary_Mask'] < 1 ,'Surface_corr'] = np.nan
    
    kernel_size = 201
    kernel = np.ones(kernel_size) / kernel_size
    df_sd_masked['DEM'] = convolve(df_sd_masked.DEM, kernel)
    df_sd_masked['Surface_corr'] = convolve(df_sd_masked.Surface_corr, kernel)
    
    df_sd_masked['SD'] = round(df_sd_masked.Surface_corr - df_sd_masked.DEM,2)
    
    df_sd_masked.loc[df_sd_masked['Binary_Mask'] < 1 ,'SD'] = np.nan
    
    df_sd_masked['SD_OG2'] = df_sd_masked['SD']
    kernel_size = 201
    kernel = np.ones(kernel_size) / kernel_size
    df_sd_masked['SD'] = convolve(df_sd_masked.SD, kernel)
    df_sd_masked.loc[df_sd_masked['Binary_Mask'] < 1 ,'SD'] = np.nan
    print('Remaining points after applying binary mask: ',df_sd_masked.shape[0])
    
    return df_sd_masked