from classes.utils.Utils import Version


class TestVersion:

    def test_version(self):
        # Some basic stuff
        assert Version.v1_12_0 < Version.v1_12_1, '1.12.0 should be < 1.12.1'
        # Check for tuple
        assert Version.v1_12_0 < (1, 13, 0), '1.12.0 should be < 1.13.0'
        # Check for tuple
        assert (1, 12, 0) == Version.v1_12_0, '1.12.0 should be 1.12.0'

    def test_get_version(self):
        assert Version.get_version(340) == Version.v1_12_2

    def test_get_versions(self):
        for v in Version:
            assert Version.get_version(v.protocol) == v, 'protocol %d of version %d.%d.%d should return the same version' % (v.protocol, v.major, v.minor, v.version)
