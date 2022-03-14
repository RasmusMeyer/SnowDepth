## Calculates snow depths by subtracting DEM values from surface heights

# Package import
import geopandas
import rasterio

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

    #Norwegian DEM
    #df_sd['SD'] = round(df_sd.Surface_corr - df_sd.DEM,2)

    #Arctic DEM - Using same coordinate system as IS2, so no need to correct.
    df_sd['SD'] = round(df_sd.Surface - df_sd.DEM,2)

    print('Remaining points: ',df_sd.shape[0])

    return df_sd