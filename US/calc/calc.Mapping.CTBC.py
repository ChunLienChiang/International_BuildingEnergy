"""
calc.Mapping.CTBC.py
============================
Mapping the data of climate-adjusted EUI to CTBC space-class and collateral-class.
"""

import pandas as pd
import os

def Get_Mapping():

	"""
	Get the mapping configurations of CTBC space-class and collateral-class.
	"""

	df_Mapping_SpaceClass      = pd.read_csv('../data/Mapping.Config/Mapping.CTBC.Space.Config.csv')
	df_Mapping_CollateralClass = pd.read_csv('../data/Mapping.Config/Mapping.CTBC.Collateral.Config.csv')

	return df_Mapping_SpaceClass, df_Mapping_CollateralClass

def Get_EUI_ClimateAdjusted():

	df_EUI = pd.read_csv('../output/output_data/EUI_ClimateAdjusted/EUI_ClimateAdjusted.csv')

	# Convert the columns that contain "EUI" to float
	EUI_Columns         = df_EUI.columns[df_EUI.columns.str.contains('EUI')]
	df_EUI[EUI_Columns] = df_EUI[EUI_Columns].astype(float)

	return df_EUI

def Mapping_to_SpaceClass(df_Mapping, df_EUI_ClimateAdjusted):

	"""
	Mapping the data of DECC to CTBC space-class.
	==================================================================================================
	Input:

		df_Mapping: The mapping configurations of CTBC space-class.

		df_EUI_ClimateAdjusted: The raw data of climate-adjusted EUI data.

	Output:

		df_EUI: The data of climate-adjusted EUI mapped to CTBC space-class (with group-mean).
	"""

	# Create new list to store the mapping data
	df_EUI = []

	for _, i_Mapping in df_Mapping.iterrows():

		if (', ' in str(i_Mapping['建築能耗原始分區'])):

			df_EUI_New = df_EUI_ClimateAdjusted[df_EUI_ClimateAdjusted['建物用途序號'].isin(i_Mapping['建築能耗原始分區'].split(', '))].drop(columns=['建物用途序號'])
			df_EUI_New = pd.concat([df_EUI_New.mean(axis=0, numeric_only=True).to_frame().T, df_EUI_New], axis=0, ignore_index=True)
			df_EUI_New['空間代號'] = i_Mapping['空間代號']
			df_EUI_New['使用空間名稱'] = i_Mapping['使用空間名稱']
			df_EUI_New.loc[0, '建物分類'] = '全部平均'
			df_EUI_New.loc[0, '建物用途'] = '全部平均'

		else:

			df_EUI_New  = df_EUI_ClimateAdjusted[df_EUI_ClimateAdjusted['建物用途序號'] == i_Mapping['建築能耗原始分區']].drop(columns=['建物用途序號'])
			if (df_EUI_New.shape[0] == 0): df_EUI_New = pd.DataFrame(index=[0])
			df_EUI_New['空間代號'] = i_Mapping['空間代號']
			df_EUI_New['使用空間名稱'] = i_Mapping['使用空間名稱']
			df_EUI_New['建物分類'] = '全部平均'
			df_EUI_New['建物用途'] = '全部平均'

		df_EUI.append(df_EUI_New)
	
	# Convert the list to dataframe
	df_EUI = pd.concat(df_EUI).round(2)

	# Rearrange columns
	df_EUI = df_EUI[['空間代號', '使用空間名稱', '建物分類', '建物用途'] + df_EUI.columns[:-4].tolist()]

	return df_EUI

def Mapping_to_CollateralClass(df_Mapping_CollateralClass, df_EUI_SpaceClass):

	# Create new list to store the mapping data
	df_EUI = []

	for _, i_Mapping in df_Mapping_CollateralClass.iterrows():

		if (', ' in str(i_Mapping['空間代號'])):

			df_EUI_New = df_EUI_SpaceClass[(df_EUI_SpaceClass['空間代號'].isin(i_Mapping['空間代號'].split(', ')))&(df_EUI_SpaceClass['建物用途']=='全部平均')].drop(columns=['空間代號', '建物分類', '建物用途'])
			df_EUI_New = pd.concat([df_EUI_New.mean(axis=0, numeric_only=True).to_frame().T, df_EUI_New], axis=0, ignore_index=True)
			df_EUI_New['擔保品細項'] = str(int(i_Mapping['擔保品細項'])).zfill(2)
			df_EUI_New['細項名稱'] = str(i_Mapping['細項名稱'])
			df_EUI_New.loc[0, '使用空間名稱'] = '全部平均'

		else:
		
			df_EUI_New  = df_EUI_SpaceClass[(df_EUI_SpaceClass['空間代號'] == i_Mapping['空間代號'])&(df_EUI_SpaceClass['建物用途']=='全部平均')].drop(columns=['空間代號', '建物分類', '建物用途'])
			df_EUI_New['擔保品細項'] = str(int(i_Mapping['擔保品細項'])).zfill(2)
			df_EUI_New['細項名稱'] = str(i_Mapping['細項名稱'])
			df_EUI_New['使用空間名稱'] = '全部平均'

		df_EUI.append(df_EUI_New)
	
	# Convert the list to dataframe
	df_EUI = pd.concat(df_EUI).round(2)

	# Rearrange columns
	df_EUI = df_EUI[['擔保品細項', '細項名稱', '使用空間名稱'] + [i for i in df_EUI.columns if i.startswith('EUI_')]]

	return df_EUI

def Save_Output(df_EUI, Output_File):

	"""
	Save the output data.
	==================================================================================================
	Input:

		df_EUI: The output dataframe.

		Output_File: The output file name.
	"""

	Output_Path = '../output/output_data/Mapping.CTBC/'
	if not os.path.exists(Output_Path): os.makedirs(Output_Path)
	df_EUI.to_csv(Output_Path + Output_File, index=False, encoding='utf-8-sig')

	return

if (__name__ == '__main__'):

	# Get the mapping table
	df_Mapping_SpaceClass, df_Mapping_CollateralClass = Get_Mapping()

	# Get the data of DECC building type mean
	df_EUI_ClimateAdjusted = Get_EUI_ClimateAdjusted()

	# ==================================================================================================
	# Mapping to space-class
	df_EUI_SpaceClass      = Mapping_to_SpaceClass(\
		df_Mapping_SpaceClass, \
		df_EUI_ClimateAdjusted, \
	)

	# Mapping to collateral-class
	df_EUI_CollateralClass = Mapping_to_CollateralClass(\
		df_Mapping_CollateralClass, \
		df_EUI_SpaceClass, \
	)

	# ==================================================================================================
	# Save output to files
	# Output the mapping table
	Save_Output(\
		df_EUI_SpaceClass, \
		'Mapping.CTBC.Space.Mean.csv', \
	)
	Save_Output(\
		df_EUI_CollateralClass, \
		'Mapping.CTBC.Collateral.Mean.csv', \
	)