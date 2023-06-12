"""
Calc.Layer_Output.CTBC
======================
Output shapefiles for CTBC EUI prediction
"""

import pandas as pd
import geopandas as gpd
import os

def Get_Shapefile():

	# Read shapefile
	gdf = gpd.read_file('../data/Shapefile.Prefectures/Prefectures.shp')

	# Remove columns
	gdf = gdf.drop(columns=['FID', 'JCODE', 'KEN_ENG', 'P_NUM', 'H_NUM', 'Shape_Leng', 'Shape_Area', 'Shape__Are', 'Shape__Len'])

	# Create REGNAME (region name) column
	gdf = gdf.rename(columns={'KEN': 'REGNAME'})

	# Create COUNTRYNAME (ISO 3166-1 alpha-2 code + country name) column
	gdf.insert(0, 'COUNTRY', 'JP-日本')

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

def Mapping_EUI(gdf_Prefectures, df_Group_EUI):

	# Set prefecture mapping dictionary
	Mapping_Prefectures = {\
		'北海道': '北海道', \
		'青森県': '東北', \
		'岩手県': '東北', \
		'宮城県': '東北', \
		'秋田県': '東北', \
		'山形県': '東北', \
		'福島県': '東北', \
		'茨城県': '關東', \
		'栃木県': '關東', \
		'群馬県': '關東', \
		'埼玉県': '關東', \
		'千葉県': '關東', \
		'東京都': '關東', \
		'神奈川県': '關東', \
		'新潟県': '北信越', \
		'富山県': '北信越', \
		'石川県': '北信越', \
		'福井県': '北信越', \
		'山梨県': '關東', \
		'長野県': '北信越', \
		'岐阜県': '中部', \
		'静岡県': '中部', \
		'愛知県': '中部', \
		'三重県': '中部', \
		'滋賀県': '關西', \
		'京都府': '關西', \
		'大阪府': '關西', \
		'兵庫県': '關西', \
		'奈良県': '關西', \
		'和歌山県': '關西', \
		'鳥取県': '中國四國', \
		'島根県': '中國四國', \
		'岡山県': '中國四國', \
		'広島県': '中國四國', \
		'山口県': '中國四國', \
		'徳島県': '中國四國', \
		'香川県': '中國四國', \
		'愛媛県': '中國四國', \
		'高知県': '中國四國', \
		'福岡県': '九州', \
		'佐賀県': '九州', \
		'長崎県': '九州', \
		'熊本県': '九州', \
		'大分県': '九州', \
		'宮崎県': '九州', \
		'鹿児島県': '九州', \
		'沖縄県': '九州', \
	}

	for i_Column in df_Group_EUI.columns: gdf_Prefectures[i_Column] = gdf_Prefectures.apply(lambda x: df_Group_EUI.loc['EUI_'+Mapping_Prefectures[x['REGNAME']], i_Column], axis=1)
	
	return gdf_Prefectures

def Output_Shapefile(gdf, Output_Path, Output_Name):

	# Set output path
	if not os.path.exists(Output_Path):	os.makedirs(Output_Path)

	# Round the number columns to 2 digits
	gdf = gdf.round(1)

	gdf.to_file(Output_Path + Output_Name, encoding='utf-8')

	return

if (__name__ == '__main__'):

	# Read shapefile
	gdf_Prefectures = Get_Shapefile()

	# Get group EUI
	df_Group_EUI = Get_Group_EUI()

	# Mapping the attributes of each prefecture to the EUI table
	gdf_Prefectures = Mapping_EUI(gdf_Prefectures, df_Group_EUI)

	# ==================================================================================================
	# Output geopandas dataframe to shape file
	Output_Shapefile(\
		gdf_Prefectures, \
		'../output/output_result/Shapefile/EUI.Prediction.CTBC.Global/', \
		'EUI.Prediction.CTBC.Global.JP-日本.shp', \
	)