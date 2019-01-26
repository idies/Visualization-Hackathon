"""
from https://github.com/geopandas/geopandas/issues/400
"""

import pandas as pd
import geopandas as gpd

def spatial_overlays(df1, df2, how='intersection'):
    '''Compute overlay intersection of two
        GeoPandasDataFrames df1 and df2
    '''
    df1 = df1.copy()
    df2 = df2.copy()
    df1['geometry'] = df1.geometry.buffer(0)
    df2['geometry'] = df2.geometry.buffer(0)
    if how == 'intersection':
        # Spatial Index to create intersections
        spatial_index = df2.sindex
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        df1['histreg'] = df1.bbox.apply(lambda x: list(spatial_index.intersection(x)))
        pairs = df1['histreg'].to_dict()
        nei = []
        for i, j in pairs.items():
            for k in j:
                nei.append([i, k])

        pairs = gpd.GeoDataFrame(nei, columns=['idx1', 'idx2'], crs=df1.crs)
        pairs = pairs.merge(df1, left_on='idx1', right_index=True)
        pairs = pairs.merge(df2, left_on='idx2', right_index=True, suffixes=['_1', '_2'])
        pairs['Intersection'] = pairs.apply(lambda x: (x['geometry_1'].intersection(x['geometry_2'])).buffer(0), axis=1)
        pairs = gpd.GeoDataFrame(pairs, columns=pairs.columns, crs=df1.crs)
        cols = pairs.columns.tolist()
        cols.remove('geometry_1')
        cols.remove('geometry_2')
        cols.remove('histreg')
        cols.remove('bbox')
        cols.remove('Intersection')
        dfinter = pairs[cols+['Intersection']].copy()
        dfinter.rename(columns={'Intersection': 'geometry'}, inplace=True)
        dfinter = gpd.GeoDataFrame(dfinter, columns=dfinter.columns, crs=pairs.crs)
        dfinter = dfinter.loc[dfinter.geometry.is_empty == False]
        return dfinter
    elif how == 'difference':
        spatial_index = df2.sindex
        df1['bbox'] = df1.geometry.apply(lambda x: x.bounds)
        df1['histreg'] = df1.bbox.apply(lambda x: list(spatial_index.intersection(x)))
        df1['new_g'] = df1.apply(lambda x: reduce(lambda x, y: x.difference(y).buffer(0),
            [x.geometry] + list(df2.iloc[x.histreg].geometry)), axis=1)
        df1.geometry = df1.new_g
        df1 = df1.loc[df1.geometry.is_empty == False].copy()
        df1.drop(['bbox', 'histreg', new_g], axis=1, inplace=True)
        return df1