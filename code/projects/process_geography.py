import os
import sys
import pandas as pd
import geopandas as gpd
from fiona.crs import from_epsg
from shapely.geometry import Polygon, Point
from shapely.ops import cascaded_union
from geopandas.tools import sjoin
import pickle
import spatial_overlays as sp


def read_file_into_dataframe(desired_geometry, name, cat, directory, crs={'init' :'epsg:4326'}):
    desired_geometry = str(desired_geometry) + '.shp'
    FP = os.path.join(directory, desired_geometry)
    df = gpd.read_file(FP)
    df = df.to_crs(crs)
    gdf = gpd.GeoDataFrame(df.loc[:, (name, 'geometry')], crs=crs, geometry='geometry')
    gdf.columns = ['key', 'geometry']
    gdf['category'] = cat
    gdf = gdf[['key', 'category', 'geometry']]
    return gdf


def get_reference(pickle_name, shapefile_dir, pickle_dir):
    try:
        fname = os.path.join(pickle_dir, pickle_name)
        gdf = pickle.load(open(fname, 'rb'))
    except:
        if pickle_name == 'maryland.pkl':
            gdf = make_reference(shapefile_dir, pickle_dir, pickle_name)
        elif pickle_name == 'baltimore.pkl':
            gdf = get_baltimore(shapefile_dir, pickle_dir)
    return gdf


def make_reference(shapefile_dir, pickle_dir, pickle_name):
    COUNTY_FN = 'Maryland_Physical_Boundaries__County_Boundaries_Generalized'
    ZIPCODE_FN = 'Maryland_Political_Boundaries__ZIP_Codes__5_Digit'
    CONGRESSIONAL_FN = 'Maryland_Archived_Election_Boundaries__2002_US_Congressional_Districts'
    LEGISLATIVE_FN = 'Maryland_Election_Boundaries__Maryland_Legislative_Districts_2012'

    county = read_file_into_dataframe(COUNTY_FN, 'county', 'county', directory=os.path.join(shapefile_dir, 'counties'))
    zipcode = read_file_into_dataframe(ZIPCODE_FN, 'ZIPCODE1', 'zipcode', directory=os.path.join(shapefile_dir, 'zipcode'))
    congressional = read_file_into_dataframe(CONGRESSIONAL_FN, 'ID_1', 'congressional_district', directory=os.path.join(shapefile_dir, 'congressional_district'))
    legislative = read_file_into_dataframe(LEGISLATIVE_FN, 'DISTRICT', 'legislative_district', directory=os.path.join(shapefile_dir, 'legislative_district'))
    maryland = pd.concat([county, zipcode, congressional, legislative], sort=False)
    maryland = maryland.reset_index()
    maryland.drop(columns='index', inplace=True)
    make_pickle(pickle_dir, maryland, pickle_name)
    return maryland


def baltimore_outline(gdf, crs={'init' :'epsg:4326'}):
    polygons = gdf.geometry
    boundary = gpd.GeoSeries(cascaded_union(polygons))
    boundary.crs = from_epsg(4326)
    outline = gpd.GeoDataFrame(boundary, crs=crs)
    outline.columns = ['geometry']
    return outline


def get_baltimore(shapefile_dir, pickle_dir, pickle_name='maryland.pkl'):
    NEIGHBORHOOD_FP = 'geo_export_78598ce9-415c-46aa-8676-d6ccfed48544'
    CENSUS_FP = 'census_tract'
    neighborhood = read_file_into_dataframe(NEIGHBORHOOD_FP, 'name', 'neighborhood', directory=os.path.join(shapefile_dir, 'neighborhood'))
    census_tract = read_file_into_dataframe(CENSUS_FP, 'name', 'census_tract', directory=os.path.join(shapefile_dir, 'census_tract'))
    outline = baltimore_outline(neighborhood)
    maryland = get_reference(pickle_name, shapefile_dir, pickle_dir)
    baltimore = sp.spatial_overlays(outline, maryland, how='intersection')
    census_tract = sp.spatial_overlays(outline, census_tract, how='intersection')
    baltimore = pd.concat([baltimore, census_tract, neighborhood], sort=False)
    baltimore = baltimore.reset_index()
    baltimore.drop(columns=['index', 'idx1', 'idx2'], inplace=True)
    make_pickle(pickle_dir, baltimore, 'baltimore.pkl')
    return baltimore


def make_pickle(processed_dir, df, pickle_name):
    with open(os.path.join(processed_dir, str(pickle_name)), 'wb') as pickle_file:
        pickle.dump(df, pickle_file)

def process(name, pickle_name, csv=False, processed_dir='data/'):
    shapefile_dir = os.path.join(os.pardir, 'data/shapefiles')
    pickle_dir = os.path.join(os.pardir, 'data/pickles/')
    gdf = get_reference(pickle_name, shapefile_dir, pickle_dir)
    if csv:
        gdf.to_csv(os.path.join(os.pardir, 'data/geography', name), index=False)

if __name__ == "__main__":
    try:
        if sys.argv[1] == "1":
            process('baltimore_geography.csv', 'baltimore.pkl', True)
            process('maryland_geography.csv', 'maryland.pkl', True)
    except:
        process('baltimore_geography.csv', 'baltimore.pkl')
        process('maryland_geography.csv', 'maryland.pkl')
