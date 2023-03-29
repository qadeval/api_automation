"""
demo test case
"""

import pytest

import pytest

@pytest.mark.xray("REAL-19")
def test_example(xray_credentials):
    assert 1+1 == 2  # Replace this with your actual test assertion
