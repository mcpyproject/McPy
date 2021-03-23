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

    def test_translate_alternate_color(self):
        assert ChatColor.translate_alternate_color('&', 'Test') == 'Test'
        assert ChatColor.translate_alternate_color('&', '&4Test') == '§4Test'
        assert ChatColor.translate_alternate_color('&', '&fTest') == '§fTest'
        assert ChatColor.translate_alternate_color('&', '&FTest') == '§fTest'
        assert ChatColor.translate_alternate_color('&', '&4&lTest') == '§4§lTest'
        assert ChatColor.translate_alternate_color('&', '&4Test &5Test2') == '§4Test §5Test2'
        assert ChatColor.translate_alternate_color('&', '&pTest') == '&pTest'
        assert ChatColor.translate_alternate_color('&', '&00&11&22&33&44&55&66&77&pp&88&99&aa&bb&cc&dd&ee&ff') == '§00§11§22§33§44§55§66§77&pp§88§99§aa§bb§cc§dd§ee§ff'
        assert ChatColor.translate_alternate_color('&', '') == ''
        assert ChatColor.translate_alternate_color('&', '&') == '&'
        assert ChatColor.translate_alternate_color('&', 'Test&') == 'Test&'
