"""
calc.Layer_Output.Merge.py
======================
Merge the shapefiles created by (1) basic CIE coef method and (2) country EUI method.
"""

import pandas as pd
import geopandas as gpd
import os
import json

def Get_Shapefile_BasicCIE():

	# Read shapefile created by basic CIE coef method
	gdf_BasicCIE = gpd.read_file('../../Basic_Coef/output/output_result/Shapefile/EUI.Prediction.CTBC.Global/EUI.Prediction.CTBC.Global.Basic_Coef.shp', encoding='utf-8')

	return gdf_BasicCIE

def Get_Shapefile_CountryEUI(List_Country):

	# Read shapefile created by country EUI method
	gdf_CountryEUI = {}

	for i_Country in List_Country:
		
		# List file under the folder
		File_Name = os.listdir('../../{}/output/output_result/Shapefile/EUI.Prediction.CTBC.Global/'.format(i_Country))
		File_Name = [i for i in File_Name if i.endswith('.shp')][0]
		gdf_CountryEUI[i_Country] = gpd.read_file('../../{}/output/output_result/Shapefile/EUI.Prediction.CTBC.Global/{}'.format(i_Country, File_Name), encoding='utf-8').to_crs('epsg:4326')

	return gdf_CountryEUI

def Combine_Shapefile(gdf_BasicCIE, gdf_CountryEUI):

	# Inquire CIE coef of each country, add column into gdf_CountryEUI, and remove the country from gdf_BasicCIE
	for i_Country in list(gdf_CountryEUI.keys()):

		gdf_CountryEUI[i_Country].insert(0, 'Coef_CIE', gdf_BasicCIE.loc[gdf_BasicCIE['COUNTRY'].str.split('-').str[0]==i_Country, 'Coef_CIE'].values[0])
		gdf_BasicCIE = gdf_BasicCIE[gdf_BasicCIE['COUNTRY'].str.split('-').str[0]!=i_Country]
	
	# Combine the shapefiles
	List_gdf = [gdf_BasicCIE] + list(gdf_CountryEUI.values())
	gdf_EUI = gpd.GeoDataFrame(pd.concat(List_gdf, ignore_index=True), crs=gdf_BasicCIE.crs)

	# Rearrange the columns
	gdf_EUI = gdf_EUI[[gdf_EUI.columns[1]] + [gdf_EUI.columns[0]] + list(gdf_EUI.columns[2:])]

	return gdf_EUI

def Output_Shapefile(gdf, Output_Path, Output_Name):

	# Set output path
	if not os.path.exists(Output_Path):	os.makedirs(Output_Path)

	# Round the number columns to 1 digits
	gdf = gdf.round(1)

	gdf.to_file(Output_Path + Output_Name, encoding='utf-8')

	return

if (__name__ == '__main__'):

	# Get configuration files
	with open('../Config.json', 'r', encoding='utf-8') as f: config = json.load(f)

	# Get shapefile created by basic CIE coef method
	gdf_BasicCIE = Get_Shapefile_BasicCIE()

	# Get shapefile created by country EUI method
	gdf_CountryEUI = Get_Shapefile_CountryEUI(List_Country=config['Method2_CountryEUI'])

	# Combine the shapefiles
	gdf_EUI = Combine_Shapefile(gdf_BasicCIE, gdf_CountryEUI)

	# ==================================================================================================
	# Output geopandas dataframe to shape file
	Output_Shapefile(\
		gdf_EUI, \
		'../output/output_result/Shapefile/EUI.Prediction.CTBC.Global/', \
		'EUI.Prediction.CTBC.Global.shp', \
	)