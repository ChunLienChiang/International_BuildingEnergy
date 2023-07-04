"""
Calc.Layer_Output.CTBC
======================
Output shapefiles for CTBC EUI prediction
"""

import pandas as pd
import geopandas as gpd
import os

def Get_Shapefile(Spacial_Area='Merge'):

	# Read shapefile: Building America and IECC Climate Zones by U.S. County Boundaries
	gdf = gpd.read_file('../data/Shapefile/world-administrative-boundaries/world-administrative-boundaries.shp')

	# Remove unnecessary columns
	gdf = gdf[['name', 'iso_3166_1_', 'geometry']].rename(columns={'iso3': 'ISO_3', 'iso_3166_1_': 'ISO_2'})
	
	if (Spacial_Area == 'Merge'):

		gdf.loc[gdf['name']=='Ma\'tan al-Sarra', 'ISO_2'] = 'LY'
		gdf.loc[gdf['name']=='Jersey', 'ISO_2'] = 'GB'
		gdf.loc[gdf['name']=='Glorioso Islands', 'ISO_2'] = 'FR'
		gdf.loc[gdf['name']=='Guernsey', 'ISO_2'] = 'GB'
		gdf.loc[gdf['name']=='Abyei', 'ISO_2'] = 'SD'
		gdf.loc[gdf['name']=='Ilemi Triangle', 'ISO_2'] = 'KE'
		gdf.loc[gdf['name']=='Guantanamo', 'ISO_2'] = 'US'
		gdf.loc[gdf['name']=='Midway Is.', 'ISO_2'] = 'US'
		gdf.loc[gdf['name']=='Jarvis Island', 'ISO_2'] = 'US'
		gdf.loc[gdf['name']=='Isle of Man', 'ISO_2'] = 'GB'
		gdf.loc[gdf['name']=='South Georgia & the South Sandwich Islands', 'ISO_2'] = 'GB'
		gdf.loc[gdf['name']=='Hala\'ib Triangle', 'ISO_2'] = 'SD'
		gdf.loc[gdf['name']=='Madeira Islands', 'ISO_2'] = 'PT'

		gdf = gdf[gdf['name']!='Kuril Islands']
	
	else:

		# Remove the rows that ISO_2 is NaN
		gdf = gdf[gdf['ISO_2'].notna()]
	
	# Remove Peurto Rico
	gdf = gdf[gdf['ISO_2']!='PR']

	# Create REGNAME (region name) column
	gdf = gdf.rename(columns={'name': 'REGNAME'})

	# Create COUNTRYNAME (ISO 3166-1 alpha-2 code + country name) column
	gdf['COUNTRY'] = gdf['ISO_2'] + '-' + gdf['REGNAME']

	return gdf

def Get_EUI():

	# Get CTBC space-class and collateral-class data
	df_Mapping_SpaceClass      = pd.read_csv('../data/EEWH_EUI/Mapping.CTBC.Space.Mean.csv')[['空間代號', 'EUI_Mean']]
	df_Mapping_CollateralClass = pd.read_csv('../data/EEWH_EUI/Mapping.CTBC.Collateral.Mean.csv')[['擔保品細項', 'EUI_Mean']]

	df_Mapping_CollateralClass['擔保品細項'] = df_Mapping_CollateralClass['擔保品細項'].astype(int).astype(str).str.zfill(2)

	# Transpose the data can concatenate along the column
	df_Mapping_SpaceClass['空間代號']        = 'EUI_' + df_Mapping_SpaceClass['空間代號']
	df_Mapping_CollateralClass['擔保品細項'] = 'EUI_' + df_Mapping_CollateralClass['擔保品細項']

	df_EUI = pd.concat([df_Mapping_SpaceClass.set_index('空間代號').T, df_Mapping_CollateralClass.set_index('擔保品細項').T], axis=1)

	return df_EUI

def Get_EUI_SG():

	# Get Singapore EUI data
	df_EUI_SG = pd.read_csv('../data/EUI_SG/EUI_SG.csv', encoding='utf-8')

	return df_EUI_SG

def Get_Coef_CarbonIntensity():
	
	# Read carbon intensity data
	df_CarbonIntensity = pd.read_csv('../data/Coef_CarbonIntensity_Electricity/Coef_CarbonIntensity_Electricity.csv', encoding='utf-8')

	return df_CarbonIntensity

def Mapping_EUI(gdf_Country, df_EUI, df_Coef_CIE):
	
	# Set index
	gdf_Country = gdf_Country.set_index('ISO_2')
	df_Coef_CIE = df_Coef_CIE.set_index('國家/地區代號')

	# Combine gdf_Country and column "電力排碳係數_公斤CO2e/度" in df_Coef_CIE based on ISO_2 and "國家/地區代號"
	gdf_Country = gdf_Country.join(df_Coef_CIE['電力排碳係數_公斤CO2e/度'], on='ISO_2')
	gdf_Country = gdf_Country.rename(columns={'電力排碳係數_公斤CO2e/度': 'Coef_CIE'})

	# Reset index
	gdf_Country = gdf_Country.reset_index()

	# Mapping data
	# Merge all columns in df_EUI to gdf_Country
	gdf_Country[list(df_EUI.columns)] = df_EUI.loc[df_EUI.index.repeat(len(gdf_Country))].reset_index(drop=True)

	# Remove unnecessary columns
	gdf_Country = gdf_Country.drop(columns=['ISO_2'])

	return gdf_Country

def Replace_SG(gdf_Country):

	# Get Singapore EUI data
	df_EUI_SG   = Get_EUI_SG()

	# Replace the EUI attributes in Singapore polygon (EUI_A1, ..., EUI_33) to Singapore EUI data
	gdf_Country.loc[gdf_Country['COUNTRY']=='SG-Singapore', [i for i in gdf_Country.columns if i.startswith('EUI_')]] = df_EUI_SG.T.values[-1, ...]

	return gdf_Country

def Output_Shapefile(gdf, Output_Path, Output_Name):

	# Set output path
	if not os.path.exists(Output_Path):	os.makedirs(Output_Path)

	# Round the number columns to 1 digits
	gdf = gdf.round(3)

	gdf.to_file(Output_Path + Output_Name, encoding='utf-8')

	return

if (__name__ == '__main__'):

	# Get shapefile
	gdf_Country = Get_Shapefile()

	# Get EUI
	df_EUI      = Get_EUI()

	# Get carbon intensity of electricity
	df_Coef_CIE = Get_Coef_CarbonIntensity()

	# Mapping the attributes of each prefecture to the EUI table
	gdf_Country = Mapping_EUI(gdf_Country, df_EUI, df_Coef_CIE)
	gdf_Country = Replace_SG(gdf_Country)

	# ==================================================================================================
	# Output geopandas dataframe to shape file
	Output_Shapefile(\
		gdf_Country, \
		'../output/output_result/Shapefile/EUI.Prediction.CTBC.Global/', \
		'EUI.Prediction.CTBC.Global.Basic_Coef.shp', \
	)