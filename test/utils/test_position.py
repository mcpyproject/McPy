from classes.utils.Position import Position


class TestPosition:

    def test_position(self):
        pos = Position(1, 4, 5)
        assert pos.x == 1, 'x should be 1'
        assert pos.y == 4, 'y should be 4'
        assert pos.z == 5, 'z should be 5'

    def test_clone(self):
        pos = Position(1, 4, 5)
        clone = pos.clone()
        assert pos == clone, 'clone should be the same as the original'
        assert pos.x == clone.x, 'x should be the same'
        assert pos.y == clone.y, 'y should be the same'
        assert pos.z == clone.z, 'z should be the same'

        # Clone negative numbers
        pos = Position(-1, -4, -5)
        clone = pos.clone()
        assert pos == clone, 'clone should be the same as the original'
        assert pos.x == clone.x, 'x should be the same'
        assert pos.y == clone.y, 'y should be the same'
        assert pos.z == clone.z, 'z should be the same'

    def test_clone_rounded(self):
        pos = Position(1.1, 4.5, 5.9)
        block = pos.clone_rounded()
        assert pos != block, 'Positions should be different'
        assert block.x == 1, 'x should be 1'
        assert block.y == 4, 'y should be 4'
        assert block.z == 5, 'z should be 5'

        # Check for negatives number
        pos = Position(-1.1, -4.5, -5.9)
        block = pos.clone_rounded()
        assert pos != block, 'Positions should be different'
        assert block.x == -2, 'x should be -2'
        assert block.y == -5, 'y should be -5'
        assert block.z == -6, 'z should be -6'

        # Check for negatives & positives number
        pos = Position(-1.1, 4.5, -5.9)
        block = pos.clone_rounded()
        assert pos != block, 'Positions should be different'
        assert block.x == -2, 'x should be -2'
        assert block.y == 4, 'y should be 4'
        assert block.z == -6, 'z should be -6'

    def test_distance(self):
        pos = Position(1, 1, 1)
        pos2 = Position(2, 3, 3)
        assert pos.distance_squared(pos2) == 9, 'Squared distance between (1, 1, 1) and (2, 3, 3) should be 9'
        assert pos.distance(pos2) == 3, 'Distance between (1, 1, 1) and (2, 3, 3) should be 3'
        assert pos.distance(pos2) == pos2.distance(pos), 'Distance must be the same'

        pos = Position(1, 3, 1)
        pos2 = Position(2, 1, 3)
        assert pos.distance(pos2) == 3, 'Distance between (1, 3, 1) and (2, 1, 3) should be 3'

        pos = Position(10, 10, 10)
        pos2 = Position(10, 10, 10)
        assert pos.distance(pos2) == 0, 'Distance at same point should be 0'

        pos = Position(-1, -1, -1)
        pos2 = Position(1, 2, 4)
        dist = pos.distance(pos2)
        assert dist > 6.1644 and dist < 6.1645, 'Distance between (-1, -1, -1) and (1, 2, 4) should be about 6.164414'
