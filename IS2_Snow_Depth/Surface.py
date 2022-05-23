## Estimates surface height by grouping photons height values along-track, using kernel density to estimate surface height, and substracting the geoid

# Package import
import time
import numpy as np
from sklearn.neighbors import KernelDensity
import pandas as pd

# Function for estimating surface height
def surface(dfATL03, window_width, geoid, resolution):
    '''
    Estimates surface height by grouping photons height values along-track, using kernel density to estimate surface height, and substracting the geoid

    Inputs:
        dfATL03: Pandas dataframe with coordinates, height, date and confidence level per photon
        window_width: Defines the search radius in which photons will be included to calculate surface height
        geoid: Reference geoid information per defined resolution
        resolution: Distance between surface height points. Can be set to either 10 or 100 m

    Outputs:
        df_surface: Dataframe containing surface heights and coordinates per resolution
    '''
    print('Length of geoid', len(geoid))
    # Track function time
    startTime = time.time()
    
    # Along track distance values, min and max to determine boundries for moving window.
    AT_dist_values = dfATL03['AT_dist'].values
    AT_dist_totmax = AT_dist_values.max()
    AT_dist_totmin = AT_dist_values.min()
    
    # Photon height level array
    heights_values = dfATL03['heights'].values
    
    
    # Confidence level array
    conf_values = dfATL03['conf'].values
    
       # Confidence level array
    beam_info = dfATL03['conf'].values
    
    # Coordinates array
    lats = dfATL03['lats'].values
    lons = dfATL03['lons'].values
    
    # Moving Window - List of values starting from Along track distance min to max,
    # at a resulution of either 10 or 100 meters
    windows = np.arange(AT_dist_totmin, AT_dist_totmax, resolution).tolist()
          
    print('Length of windows', len(windows))

    # Empty arrays to store new along track segmented values instead of per-photon.
    
    #Along track window center array
    AT_window_center_arr = np.empty(len(windows))
    
    # Surface array
    surface_arr = np.empty(len(windows))  
    
    # Latitude
    lat_arr = np.empty(len(windows))  
    
    # Longitude
    lon_arr = np.empty(len(windows))  
    
    # WL
    WL_arr = np.empty(len(windows))  
    
    #STD
    
    std_arr = np.empty(len(windows)) 
    
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

        # Select photons AT_dist & heights within window boundries
        window_heights = heights_values[min_dist_row:max_dist_row]
        

        #print('WL',len(window_heights))
        #print('WC',window_center)
        
        #Window Length
            
        WL_arr[i] = len(window_heights)
        std_arr[i] = window_heights.std()
        
        # Only Search for surface if there is enough Photons in window
        if len(window_heights) > 5: #Normally 5 lately 50
            

            binwidth = 0.2
            
            # Kernel Density Function
            kde = KernelDensity(kernel='gaussian', bandwidth=binwidth).fit(window_heights[:, None])
            
            # Kernel density scores
            kde_scores = kde.score_samples(window_heights[:, None])
            
            # Select bin with heighest density
            maxdensityI = np.max(kde_scores)
            
            # Extract height from heighest density bin
            max_index = np.where(kde_scores == maxdensityI)
            maxdensityH =  window_heights[max_index]
            
            # Define surface-height as height with highest photon density  
            Surface_Estimation = maxdensityH[0]
            
            # Add center of window as new along track distance in element i
            AT_window_center_arr[i] = window_center 
            
            # Add estimated surface
            surface_arr[i] = Surface_Estimation
            
            # Add Latitude
            lat_arr[i] = lat
            
            # Add longitude
            lon_arr[i] = lon
            
            
            i+=1

        else:
            # If there is not enough photons in window, set surface to 0. 
            AT_window_center_arr[i] = window_center
            surface_arr[i] = np.nan
            lat_arr[i] = lat
            lon_arr[i] = lon     
            i+=1
        
        # Calculate and print progress
        wincen = int(window_center)
        if wincen % 25000 < 1:  
            m = int(i / len(windows) * 100)
            print(m, "% Done")
    
    #Track Quality Control
    kernel_size = 99
    kernel = np.ones(kernel_size) / kernel_size
    WL_conv_arr = np.convolve(WL_arr, kernel, mode='same')
    print('Length of output', len(surface_arr))
    # Create new segmented dataframe at x resolution with surface heights, along track distance and coordinates. 
    df_surface = pd.DataFrame(AT_window_center_arr, columns = ['AT_dist']) 
    df_surface["Surface"] = surface_arr
    df_surface["lats"] = lat_arr
    df_surface["lons"] = lon_arr
    df_surface["WL"] = WL_arr
    df_surface["WL_conv"] = WL_conv_arr
    df_surface["std_val"] = std_arr
    

    # Add geoid to correct surface heights when comparing heights to Digital Elevation Models with a different coordinate system.
    if len(geoid) < len(df_surface.index):
      while len(geoid) < len(df_surface.index):
        geoid.append(geoid[-1])
      df_surface["geoid"] = geoid
    elif len(geoid) > len(df_surface.index):
       df_surface["geoid"] = geoid[:len(df_surface.index)]   
    else:
      df_surface["geoid"] = geoid
    
    print('Length of df', df_surface.shape[0])
    # Calculate corrected surface height
    df_surface['Surface_corr'] = (df_surface['Surface'] - df_surface['geoid']).round(2)
    
    # Script Runtime
    runTime =  int(time.time() - startTime)
    runTimeMin = runTime/60
    runTimeSec = runTime%60
    print("\nScript Runtime: %i minutes and %i seconds" % (runTimeMin,runTimeSec))
    
    return df_surface