## Samples values from Sentinel-1 variables and DEM into rescaled snow depth data

# Package import
import os
import geopandas as gpd
import pandas as pd
import rasterio

# Function for sampling variables into snow depth data
def sampling(path, date):
    '''
    Samples values from Sentinel-1 variables and DEM into rescaled snow depth data

    Input:
        path: Path to AOI-folder
        date: Folder for date of observation (e.g. 20210211)

    Output:
        df_training: A shapefile with training points containing values of Sentinel-1 variables and DEM
    '''
    # Counter
    i=0

    # Path to snow depth data for the chosen date
    SD_path = path + date + '/SnowDepth/'

    # Loop through snow depth .shp files and add them to dataframe
    for file in os.listdir(SD_path):
        if file.endswith('shp'):

            points = os.path.join(SD_path,file)
            df_training = gpd.read_file(points)
            
            if i != 0:
                df_train = pd.concat([df_train,df_training])
            else: 
                df_train = df_training
                i=i+1  

    # Rename            
    df_training = df_train

    # Get coordinates
    coords = [(x,y) for x, y in zip(df_training.geometry.x, df_training.geometry.y)]

    # Paths to variables
    VH = path + date + '/S1/VH.tif'
    Diff = path + date + '/S1/Diff.tif'
    Ratio = path + date + '/S1/Ratio.tif'
    Subtract = path + date + '/S1/Subtract.tif'
    DEM = path[:-7] + '/DEM/mergedDEM10m_Hardanger.tif'
    
    # Create lists contaning variables and their names
    listofvars=[VH, Diff, Ratio, Subtract, DEM]
    listofvarsname=['VH', 'Diff', 'Ratio', 'Subtract','DEM']
    i = 0

    # Loop through and read each variable and sample to dataframe
    for var in listofvars:
        src = rasterio.open(var)
        df_training[listofvarsname[i]] = [x[0] for x in src.sample(coords)]
        i=i+1

    # Drop unnecessary columns
    df_training = df_training.drop(columns=['lats', 'lons', 'AT_dist'])

    # Define output directory and write .shp file to it
    outdir = path + date + '/Sampled/SD.shp'
    df_training.to_file(outdir)