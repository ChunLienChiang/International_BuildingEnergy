"""
calc.EUI.ClimateAdjusted.py
===========================
Calculate the climate adjusted EUI for a building.
1. Calibrate climate statistical EUI (Fonseca et al., 2020) to Energy Star EUI, yielding a climate adjusted EUI for 8 climate zones.
2. Calculate the commercial-to-residential EUI ratio for each climate zone, and apply to the climate adjusted EUI to yield a residential EUI.
"""

import numpy as np
import pandas as pd
import os
from string import ascii_uppercase

def Get_EUI_ClimateStatistical():

	df_EUI_ClimateStatistical = pd.read_csv('../data/EUI_ClimateAdjusted/EUI_CliamteProjection.csv')[['Sector', 'Zone', 'EUI [kWh/m2.yr] (% growth) 2010']]

	# Convert data format of EUI
	df_EUI_ClimateStatistical['EUI [kWh/m2.yr] (% growth) 2010'] = df_EUI_ClimateStatistical['EUI [kWh/m2.yr] (% growth) 2010'].str.split(' ').str[0].astype(float)
	df_EUI_ClimateStatistical = df_EUI_ClimateStatistical.rename(columns={'EUI [kWh/m2.yr] (% growth) 2010': 'EUI'})

	# Fill the first column
	df_EUI_ClimateStatistical['Sector'] = df_EUI_ClimateStatistical['Sector'].fillna(method='ffill')

	return df_EUI_ClimateStatistical

def Get_EUI_EnergyStar():

	df_EUI_EnergyStar = pd.read_csv('../data/EUI_EnergyStar/EUI_EnergyStar.csv')[['Market Sector', 'Property type', 'Site EUI (kBtu/ft2)']]

	# Convert unit from kBtu/ft2 to kWh/m2
	df_EUI_EnergyStar['EUI'] = df_EUI_EnergyStar['Site EUI (kBtu/ft2)'] * 3.15459
	del df_EUI_EnergyStar['Site EUI (kBtu/ft2)']

	return df_EUI_EnergyStar

def Calc_NormalizedEUI(df_EUI_ClimateStatistical):

	"""
	Normalize the EUI for each climate zone relative to the mean EUI of the climate zone.
	===========================
	Input:
		
		df_EUI_ClimateStatistical (DataFrame): EUI for each climate zone
	
	Output:
		
		df_EUI_ClimateStatistical (DataFrame): The original dataframe with new normalized EUI for each climate zone
	"""

	df_EUI_ClimateStatistical['EUI_Normalized'] = df_EUI_ClimateStatistical.apply(lambda x: x['EUI'] / df_EUI_ClimateStatistical[df_EUI_ClimateStatistical['Sector']==x['Sector']].mean(numeric_only=True)['EUI'], axis=1)

	return df_EUI_ClimateStatistical

def Calc_Adjusted(df_EUI_ClimateAdjusted, df_EUI_ClimateStatistical):

	"""
	Calculate the climate adjusted EUI for each climate zone.
	===========================
	Input:
		
		df_EUI_ClimateAdjusted (DataFrame): EUI for each building
		
		df_EUI_ClimateStatistical (DataFrame): EUI for each climate zone
	
	Output:
		
		df_EUI_ClimateAdjusted (DataFrame): The original dataframe with new climate adjusted EUI for each climate zone
	"""

	for i_Zone in df_EUI_ClimateStatistical['Zone'].unique():
		
		# Calculate the climate adjusted EUI for each climate zone
		df_EUI_ClimateAdjusted['EUI_{}'.format(i_Zone)] = df_EUI_ClimateAdjusted.apply(lambda x: x['EUI'] * df_EUI_ClimateStatistical.loc[(df_EUI_ClimateStatistical['Sector']=='Commercial')&(df_EUI_ClimateStatistical['Zone']==i_Zone), 'EUI_Normalized'].values[0], axis=1)

		# Calculate the residential EUI for each climate zone
		df_EUI_ClimateAdjusted.loc[df_EUI_ClimateAdjusted['Market Sector']=='Lodging/Residential', 'EUI_{}'.format(i_Zone)] = df_EUI_ClimateAdjusted.apply(lambda x: x['EUI'] * df_EUI_ClimateStatistical.loc[(df_EUI_ClimateStatistical['Sector']=='Residential')&(df_EUI_ClimateStatistical['Zone']==i_Zone), 'EUI_Normalized'].values[0], axis=1)

	# Remove the original EUI column
	df_EUI_ClimateAdjusted = df_EUI_ClimateAdjusted.drop(columns=['EUI'])

	return df_EUI_ClimateAdjusted

def Output_File(Data, Output_Language='English'):

	"""
	Output the data to csv file.
	===========================
	Input:
		Data (DataFrame): The data to be output
		Output_Language (str): The language of the output file
	"""

	# Output the data to csv file
	if (Output_Language == 'Chinese'):
		
		# Translate the market sector
		Data['Market Sector'] = Data['Market Sector'].replace({\
			'Banking/Financial Services': '銀行/金融服務', \
			'Education': '教育', \
			'Public Assembly': '公眾集會', \
			'Food Sales & Service': '食品銷售服務', \
			'Healthcare': '醫療保健', \
			'Lodging/Residential': '住宿/住宅', \
			'Mixed Use': '混合用途', \
			'Office': '辦公室', \
			'Public Services': '公共服務設施', \
			'Retail': '零售', \
			'Technology/Science': '科技/科學', \
			'Services': '個人服務', \
			'Utility': '公有設施', \
			'Warehouse/Storage': '倉庫/倉儲', \
		})

		# Translate the property type
		Data['Property type'] = Data['Property type'].replace({\
			'Bank Branch': '銀行分行', \
			'Financial Office': '金融辦公室', \
			'College/University': '大學/學院', \
			'K-12 School': 'K-12學校', \
			'Pre-school/Daycare': '幼兒園/日托', \
			'Vocational School/Adult Education': '職業學校/成人教育', \
			'Convention Center/Meeting Hall': '會議中心/會議廳', \
			'Recreation/Athletic Centers': '休閒/運動中心', \
			'Entertainment': '娛樂場所', \
			'Worship Facility': '宗教設施', \
			'Convenience Store': '便利商店', \
			'Bar/Nightclub': '酒吧/夜總會', \
			'Fast Food Restaurant': '快餐店', \
			'Restaurant': '餐廳', \
			'Supermarket/Grocery Store': '超市/雜貨店', \
			'Wholesale Club/Supercenter': '批發商店', \
			'Ambulatory Surgical Center': '門診手術中心', \
			'Hospital (General Medical & Surgical)': '醫院(一般醫療和外科)', \
			'Other/Specialty Hospital': '其他/專科醫院', \
			'Medical Office': '醫療辦公室', \
			'Outpatient Rehabilitation/Physical Therapy': '門診復健/物理治療', \
			'Urgent Care/Clinic/Other Outpatient': '急診/診所/其他門診', \
			'Barracks': '軍營', \
			'Hotel': '酒店', \
			'Multifamily Housing': '多家庭住宅', \
			'Prison/Incarceration': '監獄', \
			'Residence Hall/Dormitory': '宿舍', \
			'Residential Care Facility': '養老院', \
			'Mixed Use Property': '混合用途物業', \
			'Office': '辦公室', \
			'Veterinary Office': '獸醫辦公室', \
			'Courthouse': '法院', \
			'Fire/Police Station': '消防/警察局', \
			'Library': '圖書館', \
			'Mailing Center/Post Office': '郵寄中心/郵局', \
			'Transportation Terminal/Station': '交通運輸轉運站', \
			'Automobile Dealership': '汽車經銷商', \
			'Enclosed Mall': '封閉式購物中心', \
			'Strip Mall': '連鎖商場', \
			'Retail Store': '零售店', \
			'Laboratory': '實驗室', \
			'Dry cleaning, Shoe Repair, Locksmith, Salon, etc.': '乾洗店、鞋修理店、鎖匠、沙龍等', \
			'Drinking Water Treatment & Distribution': '飲用水處理', \
			'Energy/Power Station': '能源/發電站', \
			'Self-Storage Facility': '自存倉', \
			'Distribution Center': '配送中心', \
			'Non-Refrigerated Warehouse': '非冷藏倉庫', \
			'Refrigerated Warehouse': '冷藏倉庫', \
		})
	
	# Rename the columns
	Data = Data.rename(columns={\
		'Property type'   : '建物用途', \
		'Market Sector'   : '建物分類', \
		'EUI_Cold-dry'    : 'EUI_乾冷氣候區', \
		'EUI_Cold-humid'  : 'EUI_溼冷氣候區', \
		'EUI_Hot-dry'     : 'EUI_乾熱氣候區', \
		'EUI_Hot-humid'   : 'EUI_溼熱氣候區', \
		'EUI_Hot-marine'  : 'EUI_海洋性熱氣候區', \
		'EUI_Mixed-dry'   : 'EUI_乾混合氣候區', \
		'EUI_Mixed-humid' : 'EUI_溼混合氣候區', \
		'EUI_Mixed-marine': 'EUI_海洋性混合氣候區', \
	})


	# Add index column
	Index_Character = iter(ascii_uppercase)
	for i_Sector in Data['建物分類'].unique():

		Data.loc[Data['建物分類'] == i_Sector, '建物用途序號'] = range(1, Data[Data['建物分類'] == i_Sector].shape[0] + 1)
		Data.loc[Data['建物分類'] == i_Sector, '建物用途序號'] = next(Index_Character) + Data.loc[Data['建物分類'] == i_Sector, '建物用途序號'].astype(int).astype(str)
	
	# Rearrange the last columns to the first columns
	Data = Data[Data.columns[-1:].tolist() + Data.columns[:-1].tolist()]

	# Save the data
	Output_Path = '../output/output_data/EUI_ClimateAdjusted/'
	Output_File = 'EUI_ClimateAdjusted.csv'
	if not os.path.exists(Output_Path):	os.makedirs(Output_Path)
	Data.round(2).to_csv(Output_Path + Output_File, index=False, encoding='utf-8-sig')

if (__name__ == '__main__'):

	# Get data
	df_EUI_ClimateStatistical = Get_EUI_ClimateStatistical()
	df_EUI_EnergyStar         = Get_EUI_EnergyStar()

	# Calculate normalized EUI for climate zones relative to mean EUI (divided by mean EUI)
	df_EUI_ClimateStatistical = Calc_NormalizedEUI(df_EUI_ClimateStatistical)

	# Create new dataframe for all climate adjusted EUI
	df_EUI_ClimateAdjusted = df_EUI_EnergyStar.copy()

	# Calculate climate adjusted EUI for each climate zone
	df_EUI_ClimateAdjusted = Calc_Adjusted(df_EUI_ClimateAdjusted, df_EUI_ClimateStatistical)

	# Save output
	Output_File(df_EUI_ClimateAdjusted, Output_Language='Chinese')