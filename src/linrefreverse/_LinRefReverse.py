
import pandas as pd
import geopandas as gpd
import requests
from arcgis2geojson import arcgis2geojson
import os


DATA_SOURCE_URL = "https://mrgis.mainroads.wa.gov.au/arcgis/rest/services/OpenData/RoadAssets_DataPortal/MapServer/17/query?where=1%3D1&outFields=ROAD,START_SLK,END_SLK,CWY,NETWORK_TYPE,START_TRUE_DIST,END_TRUE_DIST&outSR=4326&f=json"


class LinRefReverse:
    """
    Create an instance, giving it a path to data. If the data does not exist it will download fresh data.

    Then use the ".convert_lat_lng_to_slk(df:Dataframe, lat_col:str, lon_col:str)"
    """
    
    def __init__(self, path_to_data_file:str, force_overwrite:bool=False):
        self.data:gpd.GeoDataFrame = self._obtain_data_link(path_to_data_file, force_overwrite)
        print("even here we can get stuff done")
        

    def _obtain_data_link(self, path_to_data_file:str, force_overwrite:bool):
        """
        TODO: implement force update option.
        TODO: implement out of date prompt.
        TODO: implement auto version nameing in folder.
        """
        if not os.path.exists(path_to_data_file):
            raise Exception(f"Provided path to data file does not exist: {path_to_data_file}")
        
        if not os.path.isfile(path_to_data_file):
            raise Exception(f"Provided path indicates a directory{path_to_data_file}. Please specify either an empty file to be overwritten, or a cached file to be loaded.")

        if (
                not os.path.getsize(path_to_data_file) == 0
            and not force_overwrite
            ):
            # try to load the cached file
            try:
                return gpd.read_parquet(path_to_data_file)
            except Exception as e:
                raise Exception("Failed to open specified data file {}. To fix this error please create an empty file. This function will only overwrite empty files. It will not create a new file.") from e
        else:
            # attempt to download new data
            print(f"Selected data file is empty. Attempting to download new data and save to {path_to_data_file}.")
            output = []
            offset = 0
            print("Download Starting:\n")
            while True:
                response = requests.request("GET", f"{DATA_SOURCE_URL}&resultOffset={offset}")
                json = response.json()
                if json["geometryType"] != "esriGeometryPolyline":
                    raise Exception("Rest service returned an object that did not have geometryType:esriGeometryPolyline")
                offset += len(json["features"])
                output.extend(json["features"])
                if "exceededTransferLimit" not in json or not json["exceededTransferLimit"]:
                    break
                print(".", end="")
            print("\nDownload Completed")
            json["features"] = output

            json = arcgis2geojson(json)
            gdf = gpd.GeoDataFrame.from_features(json["features"])
            # cache the file in the specified location
            gdf.to_parquet(path_to_data_file)
            return gdf

    def convert_lat_lng_to_slk(self, df:pd.DataFrame, lat_col:str, lon_col:str, state_roads_only:bool=True) -> pd.DataFrame:
        coords = gpd.points_from_xy(df[lon_col], df[lat_col])
        dat = self.data
        if state_roads_only:
            dat = dat[dat["NETWORK_TYPE"]=="State Road"]
       
        nearest_features = self.data.sindex.nearest(coords.data)

        dat = dat.loc[nearest_features[1]]
        
        result = dat.loc[:,["ROAD", "CWY"]]
        result["SLK"] = (
            dat
            .project(
                gpd.GeoSeries(coords),
                align=False,
                normalized=False
            )
            / dat.length
            * (dat["END_SLK"] - dat["START_SLK"])
            + dat["START_SLK"]
        )
        result.index = df.index

        return result

