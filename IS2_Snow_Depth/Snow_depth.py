## Calculates snow depths by subtracting DEM values from surface heights

# Package import
import geopandas
import rasterio
import numpy as np
from astropy.convolution import convolve, convolve_fft

# Function for calculating snow depths
def snow_depth(df_surface, DEM):  
    '''
    Calculates snow depths by subtracting DEM values from surface heights

    Input:
        df_surface: Dataframe containing surface heights and coordinates per resolution
        DEM: Desired digital elevation model. Be aware of the coordinate system and whether geoid correction is necessary

    Output:
        df_sd: Dataframe containing points with snow depths and coordinates
    '''
    #Create Geodataframe from dataframe
    df_sd = df_surface
    df_sd = geopandas.GeoDataFrame(
    df_sd, geometry=geopandas.points_from_xy(df_sd.lons, df_sd.lats))

    #Set coordinate system
    df_sd = df_sd.set_crs('EPSG:4326')

    #Convert coordinate system
    df_sd = df_sd.to_crs(25833)       

    #Sample DEM to Icesat-2 points
    coords = [(x,y) for x, y in zip(df_sd.geometry.x, df_sd.geometry.y)]
    src = rasterio.open(DEM)
    df_sd['DEM'] = [x[0] for x in src.sample(coords)]
    
    
    coords = [(x,y) for x, y in zip(df_sd.geometry.x, df_sd.geometry.y)]
    
    df_sd.loc[df_sd['DEM'] == 0.0,'DEM'] = np.nan
    df_sd.loc[df_sd['Surface_corr'].isnull(),'DEM'] = np.nan
    df_sd.loc[df_sd['DEM'].isnull(),'Surface_corr'] = np.nan
    
    df_sd.loc[df_sd['Surface_corr'].isnull(),'var'] = np.nan
    df_sd.loc[df_sd['DEM'].isnull(),'var'] = np.nan
    
    df_sd.loc[df_sd['Surface_corr'].isnull(),'DEM'] = np.nan
    df_sd['DEM_raw'] = df_sd['DEM']
    df_sd['Surface_corr_raw'] = df_sd['Surface_corr']
    
    print('df1',df_sd)
   #Norwegian DEM
    df_sd['SD_OG'] = round(df_sd.Surface_corr - df_sd.DEM,2)
   #ArcticDEM
    #df_sd['SD_OG'] = round(df_sd.Surface - df_sd.DEM,2)
    df_sd.loc[df_sd['SD_OG'] > 10,'DEM'] = np.nan
    df_sd.loc[df_sd['SD_OG'] > 10,'Surface_corr'] = np.nan

    df_sd.loc[df_sd['SD_OG'] < -10,'DEM'] = np.nan
    df_sd.loc[df_sd['SD_OG'] < -10,'Surface_corr'] = np.nan
    
    print('df2',df_sd)

    #Arctic DEM - Using same coordinate system as IS2, so no need to correct.
    #df_sd['SD'] = round(df_sd.Surface - df_sd.DEM,2)
    
    df_sd['SLOPE_IS2']  = abs(np.rad2deg(np.arctan(np.gradient(df_sd.Surface_corr, df_sd.AT_dist))))
    
    print('Remaining points: ',df_sd.shape[0])

    return df_sd