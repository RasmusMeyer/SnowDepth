## Masks out unwanted data from the dataframe containing snow depths

# Package import
import rasterio

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
    Binary_Mask = path + date + '/Masks/Binary_Mask.tif'
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

    # Mask out points on slope over X degrees (e.g. 8)
    df_sd_masked = df_sd_masked[df_sd_masked['SLOPE'] < slope_threshold]
    df_sd_masked = df_sd_masked[df_sd_masked['SLOPE'] > 1]
    print('Remaining points after applying slope mask: ',df_sd_masked.shape[0])
    
    # Mask out points that are not 1
    df_sd_masked = df_sd_masked[df_sd_masked['Binary_Mask'] > 0]
    print('Remaining points after applying binary mask: ',df_sd_masked.shape[0])
    
    return df_sd_masked