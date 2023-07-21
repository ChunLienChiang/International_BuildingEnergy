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

	# Round the float columns to 3 digits
	for i in gdf_BasicCIE.columns:
		
		if gdf_BasicCIE[i].dtype == 'float64': gdf_BasicCIE[i] = gdf_BasicCIE[i].apply(lambda x: round(x, 3))

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

def Trim_Shapefile(gdf_EUI):

	"""
	Trim the geodataframe. Detect the polygons that overlap with each other and calculate the ratio of overlap area to the total area. If the ratio is greater than 0.5, the polygon with smaller area will be removed.
	================================================================================

	Arguments:

		gdf_EUI (GeoDataFrame): The geodataframe to be trimmed.

	Output:

		gdf_EUI (GeoDataFrame): The trimmed geodataframe.
	"""
	
	gdf_EUI.crs = 'epsg:3857'

	
	# Get the area of overlap between each pair of polygons
	gdf_EUI['Area'] = gdf_EUI['geometry'].area
	
	gdf_EUI = gpd.overlay(gdf_EUI, gdf_EUI, how='intersection', keep_geom_type=False)
	gdf_EUI = gdf_EUI[gdf_EUI['REGNAME_1'] != gdf_EUI['REGNAME_2']]

	# Calculate the area of overlap
	gdf_EUI['Overlap_Area']    = gdf_EUI['geometry'].area
	gdf_EUI['Overlap_Area_r1'] = gdf_EUI['Overlap_Area'] / gdf_EUI['Area_1']
	gdf_EUI['Overlap_Area_r2'] = gdf_EUI['Overlap_Area'] / gdf_EUI['Area_2']
	#gdf_EUI = gdf_EUI[(gdf_EUI['Overlap_Area_r1'] > 0.5)|(gdf_EUI['Overlap_Area_r2'] > 0.5)]
	gdf_EUI = gdf_EUI[['REGNAME_1', 'REGNAME_2', 'Overlap_Area', 'Overlap_Area_r1', 'Overlap_Area_r2']]
	gdf_EUI = gdf_EUI.sort_values(by=['Overlap_Area_r1', 'Overlap_Area_r2'])
	
	gdf_EUI.to_csv('test.csv')
	
	# Get the ratio of overlap area to the total area
	gdf_EUI['Overlap_Ratio'] = gdf_EUI['Overlap_Area'] / gdf_EUI['Area']

	# Get the index of polygons that overlap with each other
	List_Index = gdf_EUI[gdf_EUI['Overlap_Ratio'] > 0.8].index
	
	# Remove the polygon with smaller area
	for i in List_Index:

		if gdf_EUI.loc[i, 'Area'] < gdf_EUI.loc[i+1, 'Area']: gdf_EUI = gdf_EUI.drop(i)
		else: gdf_EUI = gdf_EUI.drop(i+1)

	# Remove the columns
	gdf_EUI = gdf_EUI.drop(['Area', 'Overlap_Area', 'Overlap_Ratio'], axis=1)
	
	return gdf_EUI

def Replace_Shapefile_EUI(gdf):	

	"""
	Replace the NaN EUI values in the shapefile by the mean EUI values in Taiwan.
	================================================================================

	Arguments:

		gdf (GeoDataFrame): The geodataframe to be replaced.

	Output:

		gdf (GeoDataFrame): The replaced geodataframe.
	"""

	# Replace the NaN EUI values in EUI_01, and EUI_20 by the mean EUI values in Taiwan
	gdf.loc[gdf['EUI_01'].isnull(), 'EUI_01'] = gdf.loc[gdf['COUNTRY']=='TW-臺灣', 'EUI_01'].dropna().mean()
	gdf.loc[gdf['EUI_10'].isnull(), 'EUI_10'] = gdf.loc[gdf['COUNTRY']=='TW-臺灣', 'EUI_10'].dropna().mean()
	gdf.loc[gdf['EUI_20'].isnull(), 'EUI_20'] = gdf.loc[gdf['COUNTRY']=='TW-臺灣', 'EUI_20'].dropna().mean()

	return gdf

def Output_Shapefile(gdf, Output_Path, Output_Name):

	# Set output path
	if not os.path.exists(Output_Path):	os.makedirs(Output_Path)

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

	# Output geodataframe to csv file
	pd.DataFrame(gdf_EUI).drop(columns=['geometry']).to_csv('EUI.Prediction.CTBC.Global.csv', encoding='utf-8', index=False)
	
	# ==================================================================================================
	# Fill EUI in Japan and US by the mean EUI in Taiwan
	gdf_EUI = Replace_Shapefile_EUI(gdf_EUI)
	
	# Output geopandas dataframe to shape file
	Output_Shapefile(\
		gdf_EUI, \
		'../output/output_result/Shapefile/EUI.Prediction.CTBC.Global/', \
		'EUI.Prediction.CTBC.Global.shp', \
	)