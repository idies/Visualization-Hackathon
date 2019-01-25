import pandas as pd
import geopandas as gpd
import os
import numpy as np
import pickle
import ast
from shapely.geometry import Point

fname = os.path.join('data/pickles', 'baltimore.pkl')
gdf = pickle.load(open(fname, 'rb'))
df = pd.read_csv('data/911_calls_for_service.csv')
df.drop(columns='Unnamed: 0', inplace=True)
latlon = df['location'].str.strip('()').str.split(',', expand=True).rename(columns={0:'lat', 1:'lon'}) 
df = pd.concat([df, latlon], axis=1)
geocoded = pd.DataFrame({'lat':[""],'lon':[""], 'congressional_district':[""],'county':[""],
                           'legislative_district':[""], 'neighborhood':[""],
                           'zipcode':[""]})
for i in range(len(df.iloc[:1000])):
    geocoded = geocoded.append(geocode_point(df.loc[i,'lat'], df.loc[i,'lon']), sort=False)
geocoded = geocoded.iloc[1:]
geocoded = geocoded.reset_index()
geocoded['location'] = geocoded.apply(lambda x: str('(' + x.lat + ', ' + x.lon + ')'), axis=1)
geocoded.drop(columns=['lat', 'lon'], inplace=True)
geocoded = geocoded[['location', 'congressional_district', 'county', 'legislative_district',
                     'neighborhood', 'zipcode']]

def geocode(gdf, directory='data/pickles', pickle_name='baltimore.pkl'):
    reference = pickle.load(open(os.path.join(directory, pickle_name), 'rb'))
    try:
        df = gpd.sjoin(gdf, reference, how = 'left')
        df.drop(columns = ['index_right', 'geometry'], inplace=True)
        df = df.sort_values(by='category')
        df = df.set_index(['lat', 'lon', 'category'], append='category').unstack()
        df.columns = df.columns.droplevel()
        df = df.reset_index()
        df.drop(columns=['level_0'], inplace=True)
        df.columns.name = None
    except:
        df = pd.DataFrame({'lat':[gdf.lat.item()],'lon':[gdf.lon.item()], 'congressional_district':[np.nan], 'county':[np.nan],
                           'legislative_district':[np.nan], 'neighborhood':[np.nan],
                           'zipcode':[np.nan]})
    return df

def geocode_point(left, right):
    try:
        point = pd.DataFrame(data={'lat': [left], 'lon': [right], 'geometry':
            [Point((float(right), float(left)))]})
    except:
        return pd.DataFrame({'lat':[left],'lon':[right],
                            'congressional_district':[np.nan], 'county':[np.nan],
                           'legislative_district':[np.nan], 'neighborhood':[np.nan],
                           'zipcode':[np.nan]})
    point = point[['lat', 'lon', 'geometry']]
    point = gpd.GeoDataFrame(point, geometry='geometry')
    point.crs = {'init' :'epsg:4326'}
    return geocode(point)


def main()