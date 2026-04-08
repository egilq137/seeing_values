import pytest

from wiki_main import (get_list_of_wiki_artists, 
                  get_paintings_by_artist_url,
                  pick_random_element, 
                  pick_random_painting_from_paintings_by_artist, 
                  Painting)

from unittest.mock import patch, MagicMock
from requests import Timeout
import json


dummy_artist_list = [
        {
            "artistName": "Alice",
            "url": "alice-wonderland",
        }, 
        {
            "artistName": "White Rabbit",
            "url": "white-rabbit",
        }, 
    ]


@pytest.fixture
def good_response():
    """ Returns a Mock object of a response with status code 200"""
    mock = MagicMock()
    mock.status_code = 200
    return mock


@pytest.fixture
def response_not_found():
    """ Returns a Mock object of a response with status code 404"""
    mock = MagicMock()
    mock.status_code = 404
    return mock

@pytest.fixture
def dummy_painting(good_response) -> MagicMock:
    return MagicMock(
        artist='artist',
        title='title',
        completion_year=0,
        response=good_response,
    )

@pytest.fixture
def wiki_art_painting_good() -> MagicMock:
    return  MagicMock(
        image = good_response, 
        completitionYear = 1900,
        artistName = 'artist', 
        title = 'title',
        )


@pytest.fixture
def wiki_art_painting_bad() -> MagicMock:
    return MagicMock(
        artist='artist',
        title='title',
        completion_year=0,
        response=response_not_found,
    )


def test_cache_list_returns_without_call_to_network():
    with patch('requests.get') as mock_get:
        result = get_list_of_wiki_artists(cache_file='tests/dummy_artist_list.json')
        mock_get.assert_not_called()
    
    assert result == dummy_artist_list
    

@patch('wiki_main.requests.get')
def test_retries_on_failure_and_then_succeeds(mock_get, good_response, tmp_path):
    """ If the first request fails, it should retry and return data"""
    failed_response = MagicMock()
    failed_response.status_code = 500

    success_response = good_response
    success_response.json.return_value = dummy_artist_list

    # mock the sequence
    mock_get.side_effect = [failed_response, success_response]

    result = get_list_of_wiki_artists(cache_file=str(tmp_path / 'no_cache.json'))
    assert result == dummy_artist_list
    assert mock_get.call_count == 2


@patch('wiki_main.requests.get')
def test_gives_up_after_max_attempts(mock_get, tmp_path):
    """ Should raise an exception after the maximum attempts"""
    failed_response = MagicMock(status_code=500)
    mock_get.return_value = failed_response

    with pytest.raises(Exception, match='Max retries reached'):
        get_list_of_wiki_artists(str(tmp_path / 'no_cache.json'))
    
    assert mock_get.call_count == 3


@patch('wiki_main.requests.get')
def test_retries_on_timeout(mock_get, good_response, tmp_path):
    """ Should also retry on problems with the server, not only bad status code"""
    success_response = good_response
    success_response.json.return_value = dummy_artist_list

    mock_get.side_effect = [Timeout(), success_response]

    result = get_list_of_wiki_artists(str(tmp_path / 'no_cache.json'))
    assert result == dummy_artist_list
    assert mock_get.call_count == 2


@patch('wiki_main.requests.get')
def test_get_paintings_by_artist_url_returns_list(mock_get, good_response):
    """ Should return list of paintings by artist"""
    success = good_response
    success.json.return_value =[{'image': 'painting-1'}]
    mock_get.return_value = success
    
    result = get_paintings_by_artist_url('url')
    assert isinstance(result, list)

@patch('wiki_main.requests.get')
@patch('wiki_main.pick_random_element')
def test_pick_random_painting_by_artist_success_first_attempt(
    mock_pick_random, mock_get, good_response, wiki_art_painting_good):

    mock_pick_random.return_value = wiki_art_painting_good
    mock_get.return_value = good_response

    result = pick_random_painting_from_paintings_by_artist([])
    assert result.response.status_code == 200


@patch('wiki_main.requests.get')
@patch('wiki_main.pick_random_element')
def test_pick_random_painting_by_artist_success_second_attempt(
    mock_pick_random,
    mock_get,
    good_response, 
    response_not_found,
    wiki_art_painting_good,
    wiki_art_painting_bad):

    success = good_response
    fail = response_not_found

    mock_pick_random.side_effect = [
        wiki_art_painting_bad, 
        wiki_art_painting_good,
    ]

    mock_get.side_effect = [fail, success]

    result = pick_random_painting_from_paintings_by_artist([])
    assert result.response.status_code == 200
    assert mock_pick_random.call_count == 2
    assert mock_get.call_count == 2


@patch('wiki_main.requests.get')
@patch('wiki_main.pick_random_element')
def test_pick_random_painting_by_artist_gives_up_after_three_attempts(
    mock_pick_random,
    mock_get,
    response_not_found,
    wiki_art_painting_bad):

    fail = response_not_found
    mock_pick_random.side_effect = [
        wiki_art_painting_bad, 
        wiki_art_painting_bad,
        wiki_art_painting_bad
    ]

    mock_get.side_effect = [
        response_not_found, response_not_found, response_not_found
        ]

    result = pick_random_painting_from_paintings_by_artist([])
    assert result.response.status_code == 404
    assert mock_pick_random.call_count == 3
    assert mock_get.call_count == 3

