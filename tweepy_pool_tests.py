"""
Unit tests for `tweepy_pool` module.
"""

import tweepy
import tweepy_pool
import json
from nose.tools import *
from mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from tweepy import TweepError

OAUTH_DICT = {
		"consumer_key"        : "12345",
		"consumer_secret"     : "23456",
		"access_token"        : "34567",
		"access_token_secret" : "45678"
	}

def test_init_with_dict():
	"""
	tests initialization of class without filename parameter
	"""
	oauth_dicts = [OAUTH_DICT]

	api_pool = tweepy_pool.APIPool(oauth_dicts)

	assert len(api_pool.apis) == 1

def test_init_with_filename():
	"""
	tests initialization of class when a filename is given
	"""

	oauth_dicts = [OAUTH_DICT, OAUTH_DICT]

	file_mock = MagicMock(spec=file)
	file_mock.read.return_value = json.dumps(oauth_dicts)
	file_mock.__enter__.return_value = file_mock

	mock_open = Mock(return_value=file_mock)

	with patch('__builtin__.open', mock_open):
		api_pool = tweepy_pool.APIPool(oauths_filename='oauths-file')

	eq_(2, len(api_pool.apis))

def test_file_mocking():
	file_mock = MagicMock(spec=file)
	file_mock.read.return_value = 'Hello, World!'
	file_mock.__enter__.return_value = file_mock

	mock_open = Mock(return_value=file_mock)

	with patch('__builtin__.open', mock_open):
		# file_contents = open('lala').read()
		with open('lala') as f:
			file_contents = f.read()

	eq_('Hello, World!', file_contents)

def test_pick_api_with_earliest_throttle_time_when_first_in_list():
	today = datetime.now()
	tomorrow = datetime.now() + timedelta(days=1)

	api_pool = tweepy_pool.APIPool([OAUTH_DICT])

	api_pool.apis = [['first',  today],
					 ['second', tomorrow]]

	api, throttledat, idx = api_pool._pick_api_with_shortest_waiting_time()

	eq_(idx, 0)
	eq_(api, 'first')
	eq_(throttledat, today)

def test_pick_api_with_earliest_throttle_time_when_in_middle_of_list():
	today = datetime.now()
	tomorrow = today + timedelta(days=1)
	yesterday = today + timedelta(days=-1)

	api_pool = tweepy_pool.APIPool([OAUTH_DICT])

	api_pool.apis = [['first',  today],
					 ['second', yesterday],
					 ['third', tomorrow]]

	api, throttledat, idx = api_pool._pick_api_with_shortest_waiting_time()

	eq_(idx, 1)
	eq_(api, 'second')
	eq_(throttledat, yesterday)

def test_pick_api_with_earliest_throttle_time_when_last_in_list():
	today = datetime.now()
	tomorrow = today + timedelta(days=1)
	yesterday = today + timedelta(days=-1)

	api_pool = tweepy_pool.APIPool([OAUTH_DICT])

	api_pool.apis = [['first',  today],
					 ['second', tomorrow],
					 ['third', yesterday]]

	api, throttledat, idx = api_pool._pick_api_with_shortest_waiting_time()

	eq_(idx, 2)
	eq_(api, 'third')
	eq_(throttledat, yesterday)


def test_with_1_api_in_pool_calls_api_when_no_time_to_wait():
	api_mock = MagicMock(spec=tweepy.API)
	api_mock.return_value = api_mock

	with patch('tweepy.API', api_mock):
		api_pool = tweepy_pool.APIPool([OAUTH_DICT])
		api_pool.user_timeline(user_id=123)

	api_mock.user_timeline.assert_called_with(user_id=123)

def raise_error_once():
	called = {'called' : False}
	def inner(*args, **kwargs):
		if not called['called']:
			called['called'] = True
			raise TweepError([{'message': 'Rate Limit Exceeded', 'code': 88}])
		else:
			return 0
	return inner

def test_with_1_api_in_pool_sets_throttle_time_if_rate_limit_error():
	api_mock = MagicMock(spec=tweepy.API)
	api_mock.return_value = api_mock

	api_mock.user_timeline.side_effect = raise_error_once()

	with patch('tweepy.API', api_mock):
		with patch('time.sleep'):
			api_pool = tweepy_pool.APIPool([OAUTH_DICT])
			api_pool.user_timeline(user_id=234)
	api_mock.user_timeline.assert_called_with(user_id=234)
	ok_(api_pool.apis[0][1] > datetime.min)

def test_tries_same_request_on_other_api_if_one_is_throttled_with_no_sleep():
	api_mock_1 = MagicMock()
	api_mock_2 = MagicMock()

	api_mock_1.user_timeline.side_effect = raise_error_once()

	api_pool = tweepy_pool.APIPool([OAUTH_DICT, OAUTH_DICT])
	api_pool.apis[0][0] = api_mock_1
	api_pool.apis[1][0] = api_mock_2

	sleep_mock = MagicMock()
	with patch('time.sleep', sleep_mock):
		api_pool.user_timeline(user_id=345)

	sleep_mock.assert_no_calls()
	api_mock_1.user_timeline.assert_called_with(user_id=345)
	api_mock_2.user_timeline.assert_called_with(user_id=345)

def test_waits_if_rate_limit_exceeded_and_no_other_available_api():
	api_mock = MagicMock(spec=tweepy.API)
	api_mock.return_value = api_mock

	api_mock.user_timeline.side_effect = raise_error_once()

	sleep_mock = MagicMock()

	with patch('tweepy.API', api_mock):
		with patch('time.sleep', sleep_mock):
			api_pool = tweepy_pool.APIPool([OAUTH_DICT], time_to_wait=15*60)
			api_pool.user_timeline(user_id=234)
	api_mock.user_timeline.assert_called_with(user_id=234)
	sleep_mock.assert_called_with(15*60+1)