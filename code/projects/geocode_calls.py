import pandas as pd
import geopandas as gpd
import os
import sys
import numpy as np
import pickle
from shapely.geometry import Point

def geocode(gdf, directory, pickle_name='baltimore.pkl'):
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
        df = pd.DataFrame({'lat':[gdf.lat.item()],'lon':[gdf.lon.item()], 'census_tract':[np.nan], 'congressional_district':[np.nan],
                           'county':[np.nan], 'legislative_district':[np.nan], 'neighborhood':[np.nan],
                           'zipcode':[np.nan]})
    return df

def geocode_point(left, right):
    try:
        point = pd.DataFrame(data={'lat': [left], 'lon': [right], 'geometry':
            [Point((float(right), float(left)))]})
    except:
        return pd.DataFrame({'lat':[left],'lon':[right], 'census_tract':[np.nan],
                            'congressional_district':[np.nan], 'county':[np.nan],
                           'legislative_district':[np.nan], 'neighborhood':[np.nan],
                           'zipcode':[np.nan]})
    point = point[['lat', 'lon', 'geometry']]
    point = gpd.GeoDataFrame(point, geometry='geometry')
    point.crs = {'init' :'epsg:4326'}
    return geocode(point, os.path.join(os.pardir, os.pardir, 'data/pickles'))

def geocode_df(df):
    df['geometry'] = df.apply(lambda x: Point((float(x[1]), float(x[0]))), axis=1)
    df = gpd.GeoDataFrame(df, geometry='geometry')
    df.crs = {'init' :'epsg:4326'}
    return geocode(df, os.path.join(os.pardir, os.pardir, 'data/pickles'))

def _chunker(df, chunks):
        size = len(df) // chunks
        return (df[pos:pos + size] for pos in range(0, len(df), size))
    
def process_chunk(df):
        temp = []
        for chunk in _chunker(df, 100):
            coords = chunk.loc[:, ('lat', 'lon')]
            data = geocode_df(coords)
            temp.append(pd.merge(chunk, data, left_on=['lat', 'lon'],
                right_on=['lat', 'lon'], how='left').drop_duplicates())
        df = pd.concat(temp, sort=False).reset_index()
        df['location'] = df.apply(lambda x: str('(' + x.lat + ', ' + x.lon + ')'), axis=1)
        df.drop(columns=['lat', 'lon', 'index'], inplace=True)
        return df[['recordId','callDateTime','priority','district','description','callNumber',
                   'incidentLocation','location','census_tract','congressional_district','county',
                   'legislative_district','neighborhood','zipcode']]

def main(dataset='911_Police_Calls_for_Service.csv', pickle_name='baltimore.pkl', directory='data/baltimore_crime', pickle_dir='data/pickles'):
    fname = os.path.join(pickle_dir, pickle_name)
    gdf = pickle.load(open(fname, 'rb'))
    df = pd.read_csv(os.path.join(directory, dataset)
    df.location = "(" + df.location.str.split('(').str[1]
    df = df[pd.notnull(df['location'])].reset_index(drop=True)
    latlon = df['location'].str.strip('()').str.split(',', expand=True).rename(columns={0:'lat', 1:'lon'}) 
    df = pd.concat([df, latlon], axis=1)
    geocoded = process_chunk(df)
    temp.to_csv(os.path.join(directory, '911_geocoded.csv'), index=False)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    elif len(sys.argv) == 2:
        main(dataset=sys.argv[1])
    elif len(sys.argv) == 3:
        main(dataset=sys.argv[1], pickle_name=sys.argv[2])
    elif len(sys.argv) == 4:
        main(dataset=sys.argv[1], pickle_name=sys.argv[2], directory=sys.argv[3])
    elif len(sys.argv) == 5:
        main(dataset=sys.argv[1], pickle_name=sys.argv[2], directory=sys.argv[3], pickle_dir=sys.argv[4])
    else:
        print("invalid number of command line arguments")
