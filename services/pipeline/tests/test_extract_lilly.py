import pytest
from pipeline.extract.extract_cities_lilly import get_air_pollution_history


def test_history_rejects_backwards_range():
    with pytest.raises(ValueError):
        get_air_pollution_history(40.4, -3.7, start=200, end=100)
