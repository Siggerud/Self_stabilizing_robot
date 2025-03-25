import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from roboCarHelper import get_duplicates_in_list

@pytest.mark.parametrize("test_input,expected",
                         [([1, 1, 1], [1]),
                          ([1, 2, 3, 4, 4], [4]),
                          ([1, 2, 3], []),
                          ([15, 14, 15], [15]),
                          ([2, 2, 1, 14, 14], [2, 14])])
def test_get_duplicates_in_list(test_input, expected):
    result = get_duplicates_in_list(test_input)

    assert result == expected