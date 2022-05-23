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
                if df_training.shape[0] > 0:
                    i=i+1
                    df_train = df_training
                else:
                    i=i+1
                    continue
                  

    # Rename 
    if df_train.shape[0] > 0:
        df_training = df_train


        # Get coordinates
        coords = [(x,y) for x, y in zip(df_training.geometry.x, df_training.geometry.y)]

        # Paths to variables
        #VV = path + date + '/S1/VV.tif'
        #VH2k = path + date + '/S1/VHyr2k.tif'
        CS2k = path + date + '/S1/CSyr2k.tif'
        #CR2k = path + date + '/S1/CRyr2k.tif'

        
        listofvars=[VV, VH2k, CS2k, CR2k]
        listofvarsname=['VV','VH2k', 'CS2k','CR2k']
        i = 0

        # Loop through and read each variable and sample to dataframe
        for var in listofvars:
            src = rasterio.open(var)
            df_training[listofvarsname[i]] = [x[0] for x in src.sample(coords)]
            i=i+1

        # Drop unnecessary columns
        df_training = df_training.drop(columns=['lats', 'lons'])

        # Define output directory and write .shp file to it
        outdir = path + date + '/Sampled/SD.shp'
        df_training.to_file(outdir)
    