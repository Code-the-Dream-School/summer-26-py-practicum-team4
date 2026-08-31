import pytest 
import responses


# Successful data pull

def test_extract(payload):

    responses.add(responses.GET, API_URL, json=payload, status=200)
    result = extract("Los Angeles, CA")

    assert result == {
        "location" : "Los Angeles",
        "Latitude" : Latitude,
        "Longitude" : Longitude
    }

    sent = responses.calls[0].request


# Invalud location input


# Empty, unsuccessful, or malformed responses



# Missing API key/config