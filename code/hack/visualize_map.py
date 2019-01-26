"""
Module for plotting geospatial chloropleth maps.
Data passed should have the blockgroups column labeled 'key'.
Inputs: either dataframe or csv file
Outputs: geospatial chloropleth plot
To use with dataframe:
$ plot_map('column_name', df='df_name')
To use with csv file:
$ plot_map('column_name', file_name='file_name')
"""

import os
import altair as alt
import pandas as pd
import geopandas as gpd
import json
import shapely.wkt

colors = 9
cmap = 'Blues'
figsize = (16, 10)


def get_blockgroup_geometries(pickle_dir, pickle_name):
    """
    Loads SeattleCensusBlockGroups geometries as geodataframe from pickle file.
    Inputs: pickle
    Outputs: geodataframe, pickle if it does not exist
    """
    fname = os.path.join(pickle_dir, pickle_name)
    gdf = pickle.load(open(fname, 'rb'))
    return gdf


def load_choropleth_attribute(file_name, processed_dir):
    """
    Loads data for choropleth into dataframe from csv file.
    Inputs: csv file name for data desired to be choropleth
    Outputs: dataframe
    """
    df = pd.read_csv(os.path.join(processed_dir, file_name), dtype={'key': str})
    df.key = df.key.apply(lambda x: x.rstrip('.0'))
    return df


def merge_data(processed_dir, df=None, file_name=None):
    """
    Merges geometry geodataframe with chloropleth attribute data.
    Inputs: dataframe or csv file name for data desired to be choropleth
    Outputs: dataframe
    """
    block_groups = get_blockgroup_geometries()
    if df is not None:
        attribute = df
    else:
        attribute = load_choropleth_attribute(file_name, processed_dir)
    
    return block_groups.merge(attribute, on='key', how='inner')
    

def plot_map(attribute_column, processed_dir, df=None, file_name=None):
    """
    Plots geodataframe using the attribute as the chloropleth
    Inputs: column to be plotted as chloropleth, filename of csv file (optional)
    Outputs: plot
    """
    df = merge_data(df, file_name, processed_dir)
    gdf = gpd.GeoDataFrame(df, crs={'init' :'epsg:4326'}, geometry='geometry')
    gdf.plot(column=attribute_column, cmap=cmap, figsize=figsize, scheme='equal_interval',
        k=colors, categorical=True, legend=True)
    
def prepare_for_altair(self, processed_dir, df=None, file_name=None):
    df = self.merge_data(df, file_name, processed_dir)
    gdf = gpd.GeoDataFrame(df, crs={'init' :'epsg:4326'}, geometry='geometry')
    json_gdf = gdf.to_json()
    json_features = json.loads(json_gdf)
    return alt.Data(values=json_features['features'])


def plot_map_altair(self, processed_dir, df=None, file_name=None):
    data_geo = self.prepare_for_altair(df, file_name, processed_dir)
    multi = alt.selection_multi()
    return alt.Chart(data_geo).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        projection={'type': 'mercator'},
        width=300,
        height=600,
        selection=multi
    ).encode(
        color=alt.condition(multi, 'properties.mode_index_scaled:Q', alt.value('lightgray')),
        tooltip=('properties.key:Q', 'properties.neighborhood_short:N',
                 'properties.neighborhood_long:N', 'properties.seattle_city_council_district:N',
                 'properties.urban_village:N', 'properties.zipcode:N', 'properties.mode_index:Q',
                 'properties.driving:Q', 'properties.transit:Q', 
                 'properties.bicycling:Q', 'properties.walking:Q')
    )

