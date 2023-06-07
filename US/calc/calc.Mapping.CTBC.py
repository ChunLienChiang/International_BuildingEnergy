"""
calc.Mapping.CTBC.py
============================
Mapping the data of climate adjusted EUI to CTBC.
"""

import pandas as pd
import os

def Get_Mapping():

	df_Mapping = pd.read_csv('../data/Mapping.Config/Mapping.CTBC.Config.csv')

	return df_Mapping

def Get_EUI():

	df_EUI = pd.read_csv('../output/output_data/EUI_ClimateAdjusted/EUI_ClimateAdjusted.csv')

	df_EUI['建物用途序號'] = df_EUI['建物用途序號'].astype(int).astype(str)
	
	# Convert the columns that contain "EUI" to float
	EUI_Columns         = df_EUI.columns[df_EUI.columns.str.contains('EUI')]
	df_EUI[EUI_Columns] = df_EUI[EUI_Columns].astype(float)

	return df_EUI

def Mapping(df_Mapping, df_EUI):

	# Create new list to store the mapping data
	df_Mapping_EUI = []

	for _, i_Mapping in df_Mapping.iterrows():

		if (isinstance(i_Mapping['2022能耗分區'], float)):

			df_Mapping_EUI_New = pd.DataFrame(columns=['擔保品細項', '細項名稱', '建物分類', '建物用途'] + list(df_EUI.columns[3:]), index=[0])
			df_Mapping_EUI_New['擔保品細項'] = i_Mapping['擔保品細項']
			df_Mapping_EUI_New['細項名稱'] = i_Mapping['細項名稱']
			df_Mapping_EUI_New['建物分類'] = '全部平均'
			df_Mapping_EUI_New['建物用途'] = '全部平均'
			
		elif (isinstance(i_Mapping['2022能耗分區'], str)):
			
			# Convert items in list to int
			df_Mapping_EUI_New = df_EUI[df_EUI['建物用途序號'].isin(str(i_Mapping['2022能耗分區']).split(', '))].drop(columns=['建物用途序號'])
			df_Mapping_EUI_New = pd.concat([df_Mapping_EUI_New.mean(axis=0, numeric_only=True).to_frame().T, df_Mapping_EUI_New], axis=0, ignore_index=True)
			df_Mapping_EUI_New['擔保品細項'] = i_Mapping['擔保品細項']
			df_Mapping_EUI_New['細項名稱'] = i_Mapping['細項名稱']
			df_Mapping_EUI_New.loc[0, '建物分類'] = '全部平均'
			df_Mapping_EUI_New.loc[0, '建物用途'] = '全部平均'
		
		df_Mapping_EUI.append(df_Mapping_EUI_New)
	
	# Convert the list to dataframe
	df_Mapping_EUI = pd.concat(df_Mapping_EUI).round(2)

	return df_Mapping_EUI

def Save_Output(df_Mapping_EUI):

	Output_Path = '../output/output_data/Mapping.CTBC/'
	Output_File = 'Mapping.CTBC.Mean.csv'
	if not os.path.exists(Output_Path): os.makedirs(Output_Path)
	df_Mapping_EUI.to_csv(Output_Path + Output_File, index=False, encoding='utf-8-sig')

	return

if (__name__ == '__main__'):

	# Get the mapping table
	df_Mapping = Get_Mapping()

	# Get the data of climate adjusted EUI
	df_EUI = Get_EUI()

	# Mapping
	df_Mapping_EUI = Mapping(df_Mapping, df_EUI)

	# Output the mapping table
	Save_Output(df_Mapping_EUI)