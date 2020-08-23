import pytest
from classes.utils.Location import Location


class TestPosition:

    def test_location(self):
        loc = Location(1, 4, 5, "world")
        assert loc.x == 1, 'x should be 1'
        assert loc.y == 4, 'y should be 4'
        assert loc.z == 5, 'z should be 5'
        assert loc.world == "world", 'world should be "world"'

    def test_clone(self):
        loc = Location(1, 4, 5, 'world')
        clone = loc.clone()
        assert loc == clone, 'clone should be the same as the original'
        assert loc.x == clone.x, 'x should be the same'
        assert loc.y == clone.y, 'y should be the same'
        assert loc.z == clone.z, 'z should be the same'
        assert loc.world == clone.world, 'world should be the same'

        # Clone negative numbers
        loc = Location(-1, -4, -5, 'world')
        clone = loc.clone()
        assert loc == clone, 'clone should be the same as the original'
        assert loc.x == clone.x, 'x should be the same'
        assert loc.y == clone.y, 'y should be the same'
        assert loc.z == clone.z, 'z should be the same'
        assert loc.world == clone.world, 'world should be the same'

    def test_clone_rounded(self):
        loc = Location(1.1, 4.5, 5.9, 'world')
        block = loc.clone_rounded()
        assert loc != block, 'Locations should be different'
        assert block.x == 1, 'x should be 1'
        assert block.y == 4, 'y should be 4'
        assert block.z == 5, 'z should be 5'
        assert block.world == 'world', 'world should be "world"'

        # Check for negatives number
        loc = Location(-1.1, -4.5, -5.9, 'world')
        block = loc.clone_rounded()
        assert loc != block, 'Locations should be different'
        assert block.x == -2, 'x should be -2'
        assert block.y == -5, 'y should be -5'
        assert block.z == -6, 'z should be -6'
        assert block.world == 'world', 'world should be "world"'

        # Check for negatives & positives number
        loc = Location(-1.1, 4.5, -5.9, 'world')
        block = loc.clone_rounded()
        assert loc != block, 'Locations should be different'
        assert block.x == -2, 'x should be -2'
        assert block.y == 4, 'y should be 4'
        assert block.z == -6, 'z should be -6'
        assert block.world == 'world', 'world should be "world"'

    def test_distance(self):
        loc = Location(1, 1, 1, 'world')
        loc2 = Location(2, 3, 3, 'world')
        assert loc.distance_squared(loc2) == 9, 'Squared distance between (1, 1, 1) and (2, 3, 3) should be 9'
        assert loc.distance(loc2) == 3, 'Distance between (1, 1, 1) and (2, 3, 3) should be 3'
        assert loc.distance(loc2) == loc2.distance(loc), 'Distance must be the same'

        loc = Location(1, 3, 1, 'world')
        loc2 = Location(2, 1, 3, 'world')
        assert loc.distance(loc2) == 3, 'Distance between (1, 3, 1) and (2, 1, 3) should be 3'

        loc = Location(10, 10, 10, 'world')
        loc2 = Location(10, 10, 10, 'world')
        assert loc.distance(loc2) == 0, 'Distance at same point should be 0'

        loc = Location(-1, -1, -1, 'world')
        loc2 = Location(1, 2, 4, 'world')
        dist = loc.distance(loc2)
        assert dist > 6.1644 and dist < 6.1645, 'Distance between (-1, -1, -1) and (1, 2, 4) should be about 6.164414'

        # Test for different worlds
        loc = Location(1, 1, 1, 'world')
        loc2 = Location(2, 3, 3, 'world_nether')
        with pytest.raises(AssertionError) as excinfo:
            loc.distance(loc2)
        assert "World must be the same" in str(excinfo.value)
