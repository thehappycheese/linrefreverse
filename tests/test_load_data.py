
from linrefreverse import LinRefReverse
import os
import pytest

from tests.util.constants import PATH_TO_TEST_DATA


@pytest.mark.skip(reason="This test is disabled because we don't want to download the entire dataset repeatedly too often.")
def test_load_full_dataset():
    
    

    assert os.path.isdir(os.path.dirname(PATH_TO_TEST_DATA))

    if os.path.isfile(PATH_TO_TEST_DATA):
        with open(PATH_TO_TEST_DATA, 'w'):
            pass
    
    assert os.path.getsize(PATH_TO_TEST_DATA) == 0
    
    lrr = LinRefReverse(PATH_TO_TEST_DATA)

    assert not lrr.data.empty