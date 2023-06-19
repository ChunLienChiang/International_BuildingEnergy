import numpy as np
import pandas as pd
import geopandas as gpd

def Create_Random_Points(Feature, n_Point, Radius):

	Feature = Feature.dissolve('COUNTRY')

	# Create n points in Feature centered at centroid
	gdf_RDPoint = gpd.GeoDataFrame(geometry=gpd.points_from_xy( \
		x=np.random.uniform(Feature['geometry'].centroid.x-Radius, Feature['geometry'].centroid.x+Radius, n_Point), \
		y=np.random.uniform(Feature['geometry'].centroid.y-Radius, Feature['geometry'].centroid.y+Radius, n_Point), \
	))

	# Create spatial join object
	gdf_SJ = gpd.tools.sjoin(gdf_RDPoint, Feature, predicate='within', how='left')

	# Filter points
	gdf_RDPoint = gdf_SJ[gdf_SJ['index_right'].notnull()]

	return gdf_RDPoint

if (__name__ == '__main__'):
	
	# Read global shapefile
	gdf_world = gpd.read_file('../../Layer_Output/output/output_result/Shapefile/EUI.Prediction.CTBC.Global/EUI.Prediction.CTBC.Global.shp')

	# Select TW, JP, US, CN, SG, HK
	gdf_world = gdf_world[gdf_world['COUNTRY'].str.split('-').str[0].isin(['TW', 'JP', 'US', 'CN', 'SG', 'HK'])]
	
	# =============================================================================
	# Create random points
	gdf_NewPoint = gpd.GeoDataFrame()

	# Taiwan
	gdf_NewPoint = pd.concat([gdf_NewPoint, Create_Random_Points(gdf_world[gdf_world['COUNTRY'].str.split('-').str[0]=='TW'], 100, 1.5)])
	
	# Japan
	gdf_NewPoint = pd.concat([gdf_NewPoint, Create_Random_Points(gdf_world[gdf_world['COUNTRY'].str.split('-').str[0]=='JP'], 1000, 10)])
	
	# US
	gdf_NewPoint = pd.concat([gdf_NewPoint, Create_Random_Points(gdf_world[gdf_world['COUNTRY'].str.split('-').str[0]=='US'], 4000, 50)])
	
	# CN
	gdf_NewPoint = pd.concat([gdf_NewPoint, Create_Random_Points(gdf_world[gdf_world['COUNTRY'].str.split('-').str[0]=='CN'], 800, 30)])
	
	# SG
	gdf_NewPoint = pd.concat([gdf_NewPoint, Create_Random_Points(gdf_world[gdf_world['COUNTRY'].str.split('-').str[0]=='SG'], 100, 0.1)])
	
	# HK
	gdf_NewPoint = pd.concat([gdf_NewPoint, Create_Random_Points(gdf_world[gdf_world['COUNTRY'].str.split('-').str[0]=='HK'], 100, 0.1)])
	
	# Extract x and y from geometry
	gdf_NewPoint['x'] = gdf_NewPoint['geometry'].x
	gdf_NewPoint['y'] = gdf_NewPoint['geometry'].y

	# Save columns x and y to file
	gdf_NewPoint[['x', 'y']].to_csv('EUI.Prediction.CTBC.Global.RandomPoints.csv', index=False)
	gdf_NewPoint.to_file('EUI.Prediction.CTBC.Global.RandomPoints.shp')