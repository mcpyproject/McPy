from classes.utils.Utils import ChatColor


class TestColor:

    def test_strip_color(self):
        assert ChatColor.strip_color('Test') == 'Test'
        assert ChatColor.strip_color('&4Test') == '&4Test'
        assert ChatColor.strip_color('§4Test') == 'Test'
        assert ChatColor.strip_color('&4Te§4st') == '&4Test'
        assert ChatColor.strip_color('&0&1&2&3&4') == '&0&1&2&3&4'
        assert ChatColor.strip_color('§0§1§2§3§4') == ''
        assert ChatColor.strip_color('§yTest') == '§yTest'
