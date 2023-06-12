"""
Calc.Layer_Output.CTBC
======================
Output shapefiles for CTBC EUI prediction
"""

import geopandas as gpd

def Get_Shapefile():

    # Read shapefile
    gdf = gpd.read_file('../data/Shapefile.Prefectures/Prefectures.shp')

    print(gdf)

    return gdf

if (__name__ == '__main__'):

    # Read shapefile
    gdf = Get_Shapefile()
