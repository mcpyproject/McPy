from classes.utils.Utils import Color


class TestColor:

    def test_strip_color(self):
        assert Color.strip_color('Test') == 'Test'
        assert Color.strip_color('&4Test') == '&4Test'
        assert Color.strip_color('§4Test') == 'Test'
        assert Color.strip_color('&4Te§4st') == '&4Test'
        assert Color.strip_color('&0&1&2&3&4') == '&0&1&2&3&4'
        assert Color.strip_color('§0§1§2§3§4') == ''
        assert Color.strip_color('§yTest') == '§yTest'
