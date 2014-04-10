"""
Unit tests for `tweepy_pool` module.
"""

import tweepy
from smappPy import tweepy_pool
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


def raise_error_once():
    """
    Utility method. This returns a function that throws a rate-limit error the first time it's called
    and returns 0 on subsequent calls.
    """

    called = {'called' : False}
    def inner(*args, **kwargs):
        if not called['called']:
            called['called'] = True
            raise TweepError([{'message': 'Rate Limit Exceeded', 'code': 88}])
        else:
            return 0
    return inner


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
    """
    If the tweepy.API's throttle time is more than 15 minutes ago, call the api.
    """
    api_mock = MagicMock(spec=tweepy.API)
    api_mock.return_value = api_mock
    ut_mock = Mock(return_value=0)
    api_mock.user_timeline = ut_mock

    with patch('tweepy.API', api_mock):
        api_pool = tweepy_pool.APIPool([OAUTH_DICT])
        api_pool.user_timeline(user_id=123)

    api_mock.user_timeline.assert_called_with(user_id=123)

def test_with_1_api_in_pool_sets_throttle_time_if_rate_limit_error():
    """
    If the tweepy.API throws a rate-limit error, it should note the time of that error
    in apis[x][1].
    """
    api_mock = MagicMock(spec=tweepy.API)
    api_mock.return_value = api_mock
    ut_mock = Mock(return_value=0)
    api_mock.user_timeline = ut_mock

    api_mock.user_timeline.side_effect = raise_error_once()

    with patch('tweepy.API', api_mock):
        with patch('time.sleep'):
            api_pool = tweepy_pool.APIPool([OAUTH_DICT])
            api_pool.user_timeline(user_id=234)
    api_mock.user_timeline.assert_called_with(user_id=234)
    ok_(api_pool.apis[0][1] > datetime.min)

def test_tries_same_request_on_other_api_if_one_is_throttled_with_no_sleep():
    """
    If the first tweepy.API throws a rate-limit exception, and there is another available api,
    it should try that other api immediately, with no calls to sleep() in between.
    """
    api_mock_1 = MagicMock()
    api_mock_2 = MagicMock()

    ut_mock_1 = Mock(side_effect=raise_error_once())
    api_mock_1.user_timeline = ut_mock_1

    ut_mock_2 = Mock(return_value=0)
    api_mock_2.user_timeline = ut_mock_2

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
    """
    If the underlying tweepe.API throws an 88 (rate limit) error, and there is no other api to use,
    it should call time.sleep().
    """
    api_mock = MagicMock(spec=tweepy.API)
    api_mock.return_value = api_mock
    ut_mock = Mock(return_value=0)
    api_mock.user_timeline = ut_mock

    api_mock.user_timeline.side_effect = raise_error_once()

    sleep_mock = MagicMock()

    with patch('tweepy.API', api_mock):
        with patch('time.sleep', sleep_mock):
            api_pool = tweepy_pool.APIPool([OAUTH_DICT], time_to_wait=15*60)
            api_pool.user_timeline(user_id=234)
    api_mock.user_timeline.assert_called_with(user_id=234)
    sleep_mock.assert_called_with(15*60+1)

def test_pick_api_with_shortest_wait_for_method_with_only_1_api():
    """
    When there is only 1 api in the pool, it should be picked.
    """
    api_mock = MagicMock()
    api_mock.return_value = api_mock

    with patch('tweepy.API', api_mock):
        api_pool = tweepy_pool.APIPool([OAUTH_DICT])
        picked_api = api_pool._pick_api_with_shortest_waiting_time_for_method('method')

    assert api_mock == picked_api[0]

def test_pick_api_with_shortest_wait_for_method_picks_the_right_one_of_2():
    """
    When apis[0] is throttled for METHOD_NAME at now(), it should pick apis[1] for that METHOD_NAME.
    """
    METHOD_NAME = 'twitter_method'

    api_mock = MagicMock()
    api_mock.return_value = api_mock
    api_mock2 = MagicMock()
    api_mock2.return_value = api_mock2

    with patch('tweepy.API', api_mock):
        api_pool = tweepy_pool.APIPool([OAUTH_DICT, OAUTH_DICT])
        api_pool._apis[0][0] = api_mock
        api_pool._apis[0][1][METHOD_NAME] = datetime.now() #first api throttled now, so should pick second api
        api_pool._apis[1][0] = api_mock2


        picked_api = api_pool._pick_api_with_shortest_waiting_time_for_method(METHOD_NAME)

    assert api_mock2 == picked_api[0]

def test_pick_api_with_shortest_wait_for_method_picks_different_api_for_each_method():
    """
    When apis[0] is throttled for METHOD_NAME_1 at now(),
    and apis[1] is throttled for METHOD_NAME_2 at now(),
     it should pick apis[1] for that METHOD_NAME_1
     and pick apis[0] for METHOD_NAME_2.
    """
    METHOD_NAME_1 = 'twitter_method_1'
    METHOD_NAME_2 = 'twitter_method_2'

    api_mock = MagicMock()
    api_mock.return_value = api_mock
    api_mock2 = MagicMock()
    api_mock2.return_value = api_mock2

    with patch('tweepy.API', api_mock):
        api_pool = tweepy_pool.APIPool([OAUTH_DICT, OAUTH_DICT])
        api_pool._apis[0][0] = api_mock
        api_pool._apis[0][1][METHOD_NAME_1] = datetime.now()
        api_pool._apis[1][0] = api_mock2
        api_pool._apis[1][1][METHOD_NAME_2] = datetime.now()


    picked_api_for_method_1 = api_pool._pick_api_with_shortest_waiting_time_for_method(METHOD_NAME_1)
    picked_api_for_method_2 = api_pool._pick_api_with_shortest_waiting_time_for_method(METHOD_NAME_2)

    assert api_mock2 == picked_api_for_method_1[0]
    assert api_mock == picked_api_for_method_2[0]

def test_with_per_method_throttling_calls_calls_the_right_api_for_each_method():
    """
    When apis[0] is throttled for METHOD_NAME_1 at now(),
    and apis[1] is throttled for METHOD_NAME_2 at now(),
     it should route METHOD_NAME_1 to apis[1],
     and METHOD_NAME_2 to apis[0].
    """

    METHOD_NAME_1 = 'followers_ids'
    METHOD_NAME_2 = 'user_timeline'

    api_mock = MagicMock()
    api_mock.return_value = api_mock
    ut_mock = Mock(return_value='called user_timeline on api_mock')
    api_mock.user_timeline = ut_mock

    api_mock2 = MagicMock()
    api_mock2.return_value = api_mock2
    fids_mock = Mock(return_value='called followers_ids on api_mock2')
    api_mock2.followers_ids = fids_mock

    with patch('tweepy.API', api_mock):
        api_pool = tweepy_pool.APIPool([OAUTH_DICT, OAUTH_DICT])
        api_pool._apis[0][0] = api_mock
        api_pool._apis[0][1][METHOD_NAME_1] = datetime.now()
        api_pool._apis[1][0] = api_mock2
        api_pool._apis[1][1][METHOD_NAME_2] = datetime.now()

    api_pool._call_with_throttling_per_method(METHOD_NAME_2, id=456)
    api_pool._call_with_throttling_per_method(METHOD_NAME_1, id=654)

    api_mock.user_timeline.assert_called_with(id=456)
    api_mock2.followers_ids.assert_called_with(id=654)

def test_with_per_method_throttling_sets_throttle_time_for_method_when_88_error():
    """
    When tweepy.API raises an 88 error,
    it should note that time in the throttle_dict,
    """
    METHOD_NAME = 'user_timeline'

    api_mock = MagicMock()
    api_mock.return_value = api_mock
    ut_mock = Mock(side_effect=raise_error_once())
    api_mock.user_timeline = ut_mock

    with patch('tweepy.API', api_mock):
        api_pool = tweepy_pool.APIPool([OAUTH_DICT, OAUTH_DICT], time_to_wait=0)

    api_pool._call_with_throttling_per_method(METHOD_NAME, id=666)

    assert api_pool._apis[0][1][METHOD_NAME] > datetime.min
