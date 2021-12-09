from main import make_update
from main import remove_update

def test_make_update():
    assert make_update('test', '23:59', 'repeat', 'data', 'news')

def test_remove_update():
    assert remove_update('test')
