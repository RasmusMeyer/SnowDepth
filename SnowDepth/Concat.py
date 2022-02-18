## Function for concatenating training samples from chosen dates

# Package import
import glob
import geopandas as gpd
import pandas as pd

# Concatenation function 
def concat(AOI_path, outdir, test):
    """
    Concatenates training samples from chosen dates

    Inputs:
        AOI_path: Path to AOI-folder
        outdir: Desired output directory
        test: Whether the concatenation is a test or not. Can be set to True or False
    
    Outputs:
        .shp file: Single .shp file containing training data of all chosen dates

    """
    # Create list of training data samples
    if test is False:
    # If not a test, create a list with all dates in AOI-folder
        lit = glob.glob(AOI_path + '*//Sampled//SD.shp')
    else:
    # If test, create a list with only specific dates
        lit = glob.glob(AOI_path + '20200306//Sampled//SD.shp')
        lit.append(AOI_path + '20200314//Sampled//SD.shp')
    
    print('Training Data', lit)
    
    i = 0
    # Loop through each date and concatenate in dataframe
    for item in lit:
        pts = gpd.read_file(item)
        if i != 0:
            df_train = pd.concat([df_train,pts])
        else: 
            df_train = pts
            i=i+1   
    df_train.to_file(outdir + 'SD_concat.shp')