from io import StringIO
import pandas as pd

from linrefreverse import LinRefReverse
from tests.util.constants import PATH_TO_TEST_DATA

def test_convert_lat_lng_to_slk():
    
    df = pd.read_csv(StringIO("""road,cwy,slk,lat,lon
H016,L,10.0,-31.89006203575722,115.80183730752809
H016,L,10.1,-31.88917258651777,115.80163116441184
H016,L,12.0,-31.872186451099108,115.8006898763081
H016,L,13.0,-31.863836058300908,115.8012528548626"""))

    lrr = LinRefReverse(PATH_TO_TEST_DATA)

    result = lrr.convert_lat_lng_to_slk(df,"lat","lon")


    expected_result = pd.read_csv(StringIO("""ROAD,CWY,SLK
H016,Left,10.0
H016,Left,10.1
H016,Left,12.0
H016,Left,13.0
    """))

    result["SLK"] = result["SLK"].round(3)

    assert (result.to_numpy() == expected_result.to_numpy()).all()

