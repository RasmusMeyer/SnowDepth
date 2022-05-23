## Rescales snow depth points and exports a .shp file for the chosen beam

# Package import
import numpy as np
import geopandas as gpd
from astropy.convolution import convolve, convolve_fft

# Function for rescaling snow depth point data
def rescaling(df_sd_masked, window_width, rescale_resolution, beam, path, date, beaminfo):
    '''
    Rescales snow depth points and exports a .shp file for the chosen beam

    Input:
        df_sd_masked: Dataframe containing points with snow depths and coordinates - unwanted data has been masked out
        window_width: Defines the search radius in which points will be included for rescaling - median value is given to the point currently being rescaled
        rescale_resolution: Desired distance between each rescaled point
        beam: ICESat-2 has 6 beams [gt1l, gt2l, gt3l, gt1r, gt2r, gt3r]
        path: Path to AOI-folder
        date: Folder for date of observation (e.g. 20210211)

    Output:
        .shp-file per beam: A shapefile with points at the rescaled resolution for the chosen beam
    '''
    # Along track distance values, min and max to determine boundries for moving window.
    AT_dist_values = df_sd_masked['AT_dist'].values
    AT_dist_totmax = AT_dist_values.max()
    AT_dist_totmin = AT_dist_values.min()

    # Coordinates
    df_sd_masked['lons'] = df_sd_masked.geometry.x
    df_sd_masked['lats']= df_sd_masked.geometry.y

    # Coordinates array
    lats = df_sd_masked['lats'].values
    lons = df_sd_masked['lons'].values

    # Snow depth array
    SD_values = df_sd_masked['SD'].values
    
    #WL
    WL_values = df_sd_masked['WL'].values

    # Moving Window - List of values starting from Along track distance min to max,
    # at a resulution of x meters.
    windows = np.arange(AT_dist_totmin, AT_dist_totmax, rescale_resolution).tolist()

    #Along track window center array
    AT_window_center_arr = np.empty(len(windows))
    
    # Snow depth array
    snow_depth_arr = np.empty(len(windows))  
    
    # Latitude
    lat_arr = np.empty(len(windows))  
    
    # Longitude
    lon_arr = np.empty(len(windows)) 
    
    # Window Length
    
    WL_arr = np.empty(len(windows))  

    # track number of iterations
    i = 0
    
    # Iterate through every photon(row), store then into segments at x resolution and calculate surface
    # height based on photon height density.
    for window_center in windows:    

        # Get minimum window boundries
        min_dist = window_center - window_width
        min_dist_array = np.where(AT_dist_values > min_dist)
        min_dist_row = min_dist_array[0][0]

        # Get maximum window boundries
        max_dist = window_center + window_width
        if max_dist < AT_dist_values[-1]:
            max_dist_array = np.where(AT_dist_values > max_dist)
            max_dist_row = max_dist_array[0][0]
        else:
            max_dist = AT_dist_values[-1] 

        # Get window center lat & long (for plotting)     
        idx = (np.abs(AT_dist_values - window_center)).argmin()
        lat = lats[idx]
        lon = lons[idx]
        
        # Select snow depths within window boundries
        window_SD = SD_values[min_dist_row:max_dist_row]
        
        window_WL = WL_values[min_dist_row:max_dist_row]
        

        
        #if div < 3:
        #    continue
        
        # Only Search for snow depths if there is enough Photons in window
        if len(window_SD) > 0: #Normally 5
            
            maks = len(window_SD)
            lend = sum(window_WL)
            if lend > 0:
                div = lend/maks
            else:
                div = 0
                
            print('point density: ', div, 'of dist: ', window_center)
                
            #Define new snow depth as median of snow depth within larger rescaled window boundries
            SD = np.median(window_SD)

            # Add center of window as new along track distance in element i.
            AT_window_center_arr[i] = window_center 
            
            # Add estimated surface
            snow_depth_arr[i] = SD
            
            # Add Latitude
            lat_arr[i] = lat
            
            # Add longitude
            lon_arr[i] = lon
            
            WL_arr[i] = div
            i+=1

        else:
            
            # If there is not enough photons in window, set surface to -999. 
            AT_window_center_arr[i] = window_center
            snow_depth_arr[i] = np.nan
            lat_arr[i] = lat
            lon_arr[i] = lon
            WL_arr[i] = 0
            i+=1

    df = gpd.GeoDataFrame(AT_window_center_arr, columns = ['AT_dist']) 
    df["SD"] = snow_depth_arr
    df["lats"] = lat_arr
    df["lons"] = lon_arr
    df["pho_qt"] = WL_arr
    print('Length of rescale arr', len(snow_depth_arr))
    df["beaminfo"] = [beaminfo] * len(lon_arr)
    df["beam"] = [beam] * len(lon_arr)
    df["date"] = [date] * len(lon_arr)
    
    gdf = gpd.GeoDataFrame(
    df, geometry=gpd.points_from_xy(df.lons, df.lats))
    gdf = gdf.set_crs('EPSG:25833')
    
    print(gdf.shape, 'shape1')
    #Filter bad observations
    #gdf = gdf[gdf['SD'] > -10]
    #gdf = gdf[gdf['SD'] < 10]
    #gdf = gdf[gdf['SD'] != np.nan]
    print(gdf.shape, 'shape2')
    print(gdf, 'gdf1')
    
    
    if gdf.shape[0] > 20:
    
        gdf.drop(gdf.tail(10).index,
        inplace = True)
        
        gdf.drop(gdf.head(10).index,
        inplace = True)
    
    
        outdir = path + date + '/SnowDepth/' + beam + '.shp'
        gdf.to_file(outdir)
        
    return gdf