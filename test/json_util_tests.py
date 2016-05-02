from nose.tools import *
import json
from StringIO import StringIO
from smappPy.json_util import StreamJsonListLoader

def test_returns_single_object_in_list():
    test_object = {'hello':'world'}

    stream = StringIO(json.dumps([test_object]))

    steram_list_loader = StreamJsonListLoader(stream)

    ret = [el for el in steram_list_loader][0]

    ok_(ret == test_object)

def test_returns_list_of_correct_length_with_3_objects():
    test_object = { 'ke' : 'val' }
    stream = StringIO(json.dumps([test_object]*3))

    steram_list_loader = StreamJsonListLoader(stream)

    ret = [el for el in steram_list_loader]

    ok_(len(ret) == 3)
