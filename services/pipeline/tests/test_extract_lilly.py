data_sample = {
	'dt': 1756252800,
	'main': {'aqi': 3},
	    'components': {'co': 137.02, 'no': 0, 'no2': 0.55, 'o3': 18.06,
                   'so2': 0.12, 'pm2_5': 3.18, 'pm10': 3.31, 'nh3': 0.3}
}

def test_aqi_is_in_main():
	assert data_sample['main']['aqi'] == 3

def test_pollution_keys_present():
	keys = set(data_sample['components'].keys())
	assert keys == {'co', 'no', 'no2', 'o3','so2', 'pm2_5', 'pm10', 'nh3'}

def test_fine_and_coarse_different():
	assert data_sample['components']['pm2_5'] != data_sample['components']['pm10']



import pytest
from pipeline.extract.extract_cities_lilly import get_air_pollution_history


def test_history_rejects_backwards_range():
    with pytest.raises(ValueError):
        get_air_pollution_history(40.4, -3.7, start=200, end=100)
