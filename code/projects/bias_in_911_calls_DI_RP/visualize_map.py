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
import pickle
import numpy as np


def load_pickle(pickle_dir, pickle_name):
    """
    Loads SeattleCensusBlockGroups geometries as geodataframe from pickle file.
    Inputs: pickle
    Outputs: geodataframe, pickle if it does not exist
    """
    return pickle.load(open(os.path.join(pickle_dir, pickle_name), 'rb'))


def merge_data(attribute_column, geography, chloropleth, pickle_dir):
    """
    Merges geometry geodataframe with chloropleth attribute data.
    Inputs: dataframe or csv file name for data desired to be choropleth
    Outputs: dataframe
    """
    gdf = load_pickle(pickle_dir, geography)
    chloropleth = load_pickle(pickle_dir, chloropleth)
    chloropleth.columns = ['key', attribute_column]
    return gdf.merge(chloropleth, on='key', how='left')
    

def plot_map(attribute_column, geography, chloropleth, pickle_dir='data/pickles'):
    """
    Plots geodataframe using the attribute as the chloropleth
    Inputs: column to be plotted as chloropleth, filename of csv file (optional)
    Outputs: plot
    """
    df = merge_data(attribute_column, geography, chloropleth, pickle_dir)
    gdf = gpd.GeoDataFrame(df, crs={'init' :'epsg:4326'}, geometry='geometry')
    gdf.plot(column=attribute_column, cmap=cmap, figsize=figsize, scheme='equal_interval',
        k=colors, categorical=False, legend=True)
    

def prepare_for_altair(attribute_column, geography, chloropleth, pickle_dir='data/pickles'):
    df = merge_data(attribute_column, geography, chloropleth, pickle_dir)
    gdf = gpd.GeoDataFrame(df, crs={'init' :'epsg:4326'}, geometry='geometry')
    gdf = gdf[['key', 'category', attribute_column, 'geometry']]
    json_gdf = gdf.to_json()
    json_features = json.loads(json_gdf)
    return alt.Data(values=json_features['features'])


def plot_map_altair(attribute_column, geography, chloropleth, pickle_dir='data/pickles'):
    data_geo = prepare_for_altair(attribute_column, geography, chloropleth, pickle_dir)
    multi = alt.selection_multi()
    highlight = alt.selection(type='single', on='mouseover',
                          fields=['symbol'], nearest=True)
    baltimore = alt.Chart(data_geo).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        projection={'type': 'mercator'},
        width=550,
        height=600,
        selection=multi
    ).encode(
        color=alt.condition(multi, 'properties.' + attribute_column +':Q', alt.value('lightgray')),
        tooltip=('properties.key:O', 'properties.' + attribute_column +':Q')
    )
    return baltimore

def main(attribute, chloropleth, geomap='baltimore.pkl', directory='data/geography'):
    chart = plot_map_altair(attribute, geomap, chloropleth)
    chart.save(os.path.join(directory, attribute + '.html'))

if __name__ == "__main__":
    if len(sys.argv) == 3:
        main(attribute=sys.argv[1], chloropleth=sys.argv[2])
    else if len(sys.argv) == 4:
        main(attribute=sys.argv[1], chloropleth=sys.argv[2], geomap=sys.argv[3])
    else if len(sys.argv) == 5:
        main(attribute=sys.argv[1], chloropleth=sys.argv[2], geomap=sys.argv[3], directory=sys.argv[4])
    else:
        print("invalid number of command line arguments")
