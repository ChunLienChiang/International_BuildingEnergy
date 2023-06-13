"""
calc.DECC.py
========================
Calculate and output the statistics of DECC data:
1. The mean of primary energy (PE) consumption of each building type.
2. The mean of electricity consumption of each building type.

if there's any nan value in the data, the mean of the data will be filled.
"""

import pandas as pd
import os

def Get_Data():

	"""
	Get the data of DECC and convert the unit of primary energy (PE) consumption to kWh/m2.
	=================================
	Output:
		df_DECC (dataframe): The data of DECC
	"""

	# Get data
	df_DECC = pd.read_csv('../data/DECC/DECC.csv', encoding='shift_jisx0213')
	df_DECC = df_DECC[[\
		'建物用途', \
		'建物ID', \
		'電力_年合計(kWh/㎡・年)', \
		'一次エネルギー原単位_MJ/㎡・年', \
	]]

	# Drop the rows that the first character of "建物ID" is abnormal
	df_DECC = df_DECC[df_DECC['建物ID'].str[0].isin(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'])]

	# Rename the column and convert unit
	df_DECC = df_DECC.rename(columns={\
		'一次エネルギー原単位_MJ/㎡・年': '一次エネルギー原単位_kWh/㎡・年', \
		'電力_年合計(kWh/㎡・年)': '電力年合計(kWh/㎡・年)', \
	})
	df_DECC['一次エネルギー原単位_kWh/㎡・年'] = df_DECC['一次エネルギー原単位_kWh/㎡・年'] * 0.2778

	return df_DECC

def Calc_Group(df_DECC):

	"""
	Calculate the mean/nSample of primary energy (PE) consumption and electricity consumption of each building type.
	=================================
	Input:
		df_DECC (dataframe): The data of DECC
	Output:
		df_DECC (dataframe): The data of DECC
	"""

	# Group dataframe by column "建物用途" and the first character of "建物ID"
	df_DECC_Grouped = df_DECC.groupby(['建物用途', df_DECC['建物ID'].str[0]]).mean(numeric_only=True)
	df_DECC_nSample = df_DECC.groupby(['建物用途', df_DECC['建物ID'].str[0]]).count().drop(columns=['建物ID'])

	# Convert level 1 index to column
	df_DECC_Grouped = df_DECC_Grouped.reset_index(level=1).rename(columns={'建物ID': '地域分區'})
	df_DECC_nSample = df_DECC_nSample.reset_index(level=1).rename(columns={'建物ID': '地域分區'})

	df_DECC_Grouped = pd.pivot_table(df_DECC_Grouped, index='建物用途', columns='地域分區', values=['電力年合計(kWh/㎡・年)', '一次エネルギー原単位_kWh/㎡・年'])
	df_DECC_nSample = pd.pivot_table(df_DECC_nSample, index='建物用途', columns='地域分區', values=['電力年合計(kWh/㎡・年)', '一次エネルギー原単位_kWh/㎡・年'])

	# Get the list of the first level of column
	for i_Var in df_DECC_Grouped.columns.get_level_values(0).unique():
		
		# Fill the missing values with the mean of row in df_DECC_Grouped
		df_DECC_Grouped[i_Var] = df_DECC_Grouped[i_Var].T.fillna(df_DECC_Grouped[i_Var].mean(axis=1)).T

	# Fill the missing values with 0 in df_DECC_nSample
	df_DECC_nSample = df_DECC_nSample.fillna(0)

	# Concatenate the two dataframes
	df_DECC = pd.concat([df_DECC_Grouped, df_DECC_nSample], axis=1, keys=['Mean', 'nSample'])

	# Convert multilevel column to single level column by joining all levels by '_'
	df_DECC.columns = df_DECC.columns.map('_'.join)

	return df_DECC

def Output_File(Data, Output_Language='Japanese'):

	"""
	Output the data as csv file.
	=================================
	Input:
		Data (dataframe): The data of DECC
		Output_Language (string): The language of output file
	"""

	# Reset index
	Data = Data.reset_index()

	# Translate the column names except the first column and the column "建物用途"
	if (Output_Language == 'Chinese'):

		# Rename columns
		Data = Data.rename(columns={\
			'電力年合計(kWh/㎡・年)': '電力_年消耗(kWh/m2*year)', \
			'一次エネルギー原単位_kWh/㎡・年': '初級能耗(kWh/m2)', \
		})

		# Rename "建物用途"
		Data['建物用途'] = Data['建物用途'].replace({\
			'その他': '其他', \
			'その他物販': '其他產品銷售', \
			'コンビニ': '便利商店', \
			'スポーツ施設': '體育設施', \
			'デパート・スーパー': '百貨公司和超市', \
			'ホテル・旅館': '酒店和旅館', \
			'一般小売': '一般零售店', \
			'事務所': '辦公室', \
			'劇場・ホール': '劇院和禮堂', \
			'大学・専門学校': '大學和專業學校', \
			'官公庁': '政府機關', \
			'家電量販店': '電器量販店', \
			'小・中学校': '小學/中學', \
			'展示施設': '展覽設施', \
			'幼稚園・保育園': '幼兒園/托兒所', \
			'病院': '醫院', \
			'研究機関': '研究機構', \
			'福祉施設': '福利設施', \
			'複合施設': '綜合設施', \
			'郊外大型店舗': '郊區大型商店', \
			'電算・情報センター': '計算機資訊中心', \
			'飲食店': '餐廳', \
			'高校': '高中', \
		})

		# Add index column
		Data.insert(0, '建物用途序號', range(1, len(Data) + 1))

		Output_Encoding = 'utf-8-sig'
	
	else:

		Output_Encoding = 'shift_jisx0213'

	# Output the data as csv file
	Output_Path = '../output/output_data/DECC/'
	Output_File = 'DECC.BuildingType_Mean.csv'
	if not os.path.exists(Output_Path):	os.makedirs(Output_Path)

	# Keep only two decimal places
	Data.round(2).to_csv(Output_Path + Output_File, encoding=Output_Encoding, index=False)

	return

if (__name__ == '__main__'):

	# Get data
	df_DECC = Get_Data()

	# Calculate the mean/nSample of primary energy (PE) consumption and electricity consumption of each building type
	df_DECC = Calc_Group(df_DECC)

	# Save as csv file
	Output_File(\
		df_DECC, \
		Output_Language='Chinese', \
	)