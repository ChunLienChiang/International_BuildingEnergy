"""
Calc.Layer_Output.CTBC
======================
Output shapefiles for CTBC EUI prediction
"""

import pandas as pd
import geopandas as gpd
import os

def Get_Shapefile():

	# Read shapefile: Building America and IECC Climate Zones by U.S. County Boundaries
	gdf = gpd.read_file('../data/Shapefile.County/Building_America_and_IECC_Climate_Zones_by_US_County_Boundaries.shp')

	# Remove unnecessary columns
	gdf = gdf[['NAME', 'STATE_NAME', 'IECC_Clima', 'IECC_Moist', 'geometry']]
	
	# Create REGNAME (region name) column
	gdf['REGNAME'] = gdf['STATE_NAME'] + ' - ' + gdf['NAME']
	del gdf['STATE_NAME'], gdf['NAME']

	# Create COUNTRYNAME (ISO 3166-1 alpha-2 code + country name) column
	gdf.insert(0, 'COUNTRY', 'US-美國')

	# Create CLIMATEZONE column by combining IECC_Clima and IECC_Moist
	gdf['IECC_Moist'] = gdf['IECC_Moist'].str.replace('N/A', '')
	gdf['CLIMATEZONE'] = gdf['IECC_Clima'].astype(int).astype(str) + gdf['IECC_Moist']
	del gdf['IECC_Clima'], gdf['IECC_Moist']

	return gdf

def Get_Group_EUI():

	# Get CTBC space-class and collateral-class data
	df_Mapping_SpaceClass      = pd.read_csv('../output/output_data/Mapping.CTBC/Mapping.CTBC.Space.Mean.csv')
	df_Mapping_CollateralClass = pd.read_csv('../output/output_data/Mapping.CTBC/Mapping.CTBC.Collateral.Mean.csv')

	# Filter the data
	df_Mapping_SpaceClass      = df_Mapping_SpaceClass[df_Mapping_SpaceClass['建物用途']=='全部平均'].drop(columns=['使用空間名稱', '建物用途'])
	df_Mapping_CollateralClass = df_Mapping_CollateralClass[df_Mapping_CollateralClass['使用空間名稱']=='全部平均'].drop(columns=['細項名稱', '使用空間名稱'])
	df_Mapping_CollateralClass['擔保品細項'] = df_Mapping_CollateralClass['擔保品細項'].astype(str).str.zfill(2)

	# Transpose the data can concatenate along the column
	df_Mapping_SpaceClass['空間代號']        = 'EUI_' + df_Mapping_SpaceClass['空間代號']
	df_Mapping_CollateralClass['擔保品細項'] = 'EUI_' + df_Mapping_CollateralClass['擔保品細項']

	df_EUI = pd.concat([df_Mapping_SpaceClass.set_index('空間代號').T, df_Mapping_CollateralClass.set_index('擔保品細項').T], axis=1)

	return df_EUI

def Mapping_EUI(gdf_County, df_Group_EUI):
	
	# Set county mapping function
	def Mapping_County(IECC_ClimateZone):

		if (IECC_ClimateZone in ['1A', '2A', '3A']): ClimateZone = '溼熱氣候區'
		elif (IECC_ClimateZone in ['2B', '3B']): ClimateZone = '乾熱氣候區'
		elif (IECC_ClimateZone in ['3C']): ClimateZone = '海洋性熱氣候區'
		elif (IECC_ClimateZone in ['4A']): ClimateZone = '溼混合氣候區'
		elif (IECC_ClimateZone in ['4B']): ClimateZone = '乾混合氣候區'
		elif (IECC_ClimateZone in ['4C']): ClimateZone = '海洋性混合氣候區'
		elif (IECC_ClimateZone in ['5A', '6A']): ClimateZone = '溼冷氣候區'
		elif (IECC_ClimateZone in ['5B', '6B']): ClimateZone = '乾冷氣候區'
		elif (IECC_ClimateZone in ['7', '8']): ClimateZone = '乾冷氣候區'

		return ClimateZone

	for i_Column in df_Group_EUI.columns: gdf_County[i_Column] = gdf_County.apply(lambda x: df_Group_EUI.loc['EUI_'+Mapping_County(x['CLIMATEZONE']), i_Column], axis=1)
	
	return gdf_County

def Output_Shapefile(gdf, Output_Path, Output_Name):

	# Set output path
	if not os.path.exists(Output_Path):	os.makedirs(Output_Path)

	# Round the number columns to 2 digits
	gdf = gdf.round(1)

	gdf.to_file(Output_Path + Output_Name, encoding='utf-8')

	return

if (__name__ == '__main__'):

	# Read shapefile
	gdf_County = Get_Shapefile()

	# Get group EUI
	df_Group_EUI = Get_Group_EUI()

	# Mapping the attributes of each prefecture to the EUI table
	gdf_County = Mapping_EUI(gdf_County, df_Group_EUI)

	# ==================================================================================================
	# Output geopandas dataframe to shape file
	Output_Shapefile(\
		gdf_County, \
		'../output/output_result/Shapefile/EUI.Prediction.CTBC.Global/', \
		'EUI.Prediction.CTBC.Global.US-美國.shp', \
	)