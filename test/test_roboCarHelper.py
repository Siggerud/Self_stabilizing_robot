import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from utility.roboCarHelper import get_duplicates_in_list, map_value_to_new_scale

@pytest.mark.parametrize("test_input,expected",
                         [([1, 1, 1], [1]),
                          ([1, 2, 3, 4, 4], [4]),
                          ([1, 2, 3], []),
                          ([15, 14, 15], [15]),
                          ([2, 2, 1, 14, 14], [2, 14])])
def test_get_duplicates_in_list(test_input, expected):
    result = get_duplicates_in_list(test_input)

    assert result == expected

@pytest.mark.parametrize("inputValue, newScaleMin, newScaleMax, oldScaleMin, oldScaleMax, precision, expected",
                         [(0.5, 0, 100, 0, 1, 1, 50.0),
                          (0.5, 0, 25, 0, 1, 1, 12.5),
                          (0.5, 0, 1.5, 0, 1, 2, 0.75)]
                         )
def test_map_value_to_new_scale(inputValue, newScaleMin, newScaleMax, oldScaleMin, oldScaleMax, precision, expected):
    result = map_value_to_new_scale(inputValue, newScaleMin, newScaleMax, oldScaleMin, oldScaleMax, precision)

    assert result == expected