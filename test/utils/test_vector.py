from classes.utils.Vector import Vector2, Vector3


class TestVector2:

    def test_vector(self):
        vec = Vector2(1, 4)
        assert vec.x == 1, 'x should be 1'
        assert vec.y == 4, 'y should be 4'

    def test_clone(self):
        vec = Vector2(1, 4)
        clone = vec.clone()
        assert vec == clone, 'clone should be the same as the original'
        assert vec.x == clone.x, 'x should be the same'
        assert vec.y == clone.y, 'y should be the same'

        # Clone negative numbers
        vec = Vector2(-1, -4)
        clone = vec.clone()
        assert vec == clone, 'clone should be the same as the original'
        assert vec.x == clone.x, 'x should be the same'
        assert vec.y == clone.y, 'y should be the same'

    def test_clone_rounded(self):
        vec = Vector2(1.1, 4.5)
        block = vec.clone_rounded()
        assert vec != block, 'Vectors should be different'
        assert block.x == 1, 'x should be 1'
        assert block.y == 4, 'y should be 4'

        # Check for negatives number
        vec = Vector2(-1.1, -4.5)
        block = vec.clone_rounded()
        assert vec != block, 'Vectors should be different'
        assert block.x == -2, 'x should be -2'
        assert block.y == -5, 'y should be -5'

        # Check for negatives & positives number
        vec = Vector2(-1.1, 4.5)
        block = vec.clone_rounded()
        assert vec != block, 'Vectors should be different'
        assert block.x == -2, 'x should be -2'
        assert block.y == 4, 'y should be 4'

    def test_distance(self):
        vec = Vector2(1, 1)
        vec2 = Vector2(2, 3)
        assert vec.distance_squared(vec2) == 5, 'Squared distance between (1, 1) and (2, 3) should be 5'

    def test_add(self):
        assert Vector2(1, 1) + Vector2(2, 2) == Vector2(3, 3)
        assert Vector2(1, 1) + Vector2(-2, 2) == Vector2(-1, 3)
        assert Vector2(1, 1) + (2, 2) == Vector2(3, 3)
        assert Vector2(1, 1) + (-2, 2) == Vector2(-1, 3)

    def test_sub(self):
        assert Vector2(1, 1) - Vector2(2, 2) == Vector2(-1, -1)
        assert Vector2(1, 1) - Vector2(-2, 2) == Vector2(3, -1)
        assert Vector2(1, 1) - (2, 2) == Vector2(-1, -1)
        assert Vector2(1, 1) - (-2, 2) == Vector2(3, -1)

    def test_mult(self):
        assert Vector2(1, 1) * 2 == Vector2(2, 2)
        assert Vector2(1, 1) * -1 == Vector2(-1, -1)
        assert Vector2(1, 1) * 0.5 == Vector2(0.5, 0.5)


class TestVector3:

    def test_vector(self):
        vec = Vector3(1, 4, 5)
        assert vec.x == 1, 'x should be 1'
        assert vec.y == 4, 'y should be 4'
        assert vec.z == 5, 'z should be 5'

    def test_clone(self):
        vec = Vector3(1, 4, 5)
        clone = vec.clone()
        assert vec == clone, 'clone should be the same as the original'
        assert vec.x == clone.x, 'x should be the same'
        assert vec.y == clone.y, 'y should be the same'
        assert vec.z == clone.z, 'z should be the same'

        # Clone negative numbers
        vec = Vector3(-1, -4, -5)
        clone = vec.clone()
        assert vec == clone, 'clone should be the same as the original'
        assert vec.x == clone.x, 'x should be the same'
        assert vec.y == clone.y, 'y should be the same'
        assert vec.z == clone.z, 'z should be the same'

    def test_clone_rounded(self):
        vec = Vector3(1.1, 4.5, 5.4)
        block = vec.clone_rounded()
        assert vec != block, 'Vectors should be different'
        assert block.x == 1, 'x should be 1'
        assert block.y == 4, 'y should be 4'
        assert block.z == 5, 'z should be 5'

        # Check for negatives number
        vec = Vector3(-1.1, -4.5, -0.001)
        block = vec.clone_rounded()
        assert vec != block, 'Vectors should be different'
        assert block.x == -2, 'x should be -2'
        assert block.y == -5, 'y should be -5'
        assert block.z == -1, 'z should be -1'

        # Check for negatives & positives number
        vec = Vector3(-1.1, 4.5, 0.999)
        block = vec.clone_rounded()
        assert vec != block, 'Vectors should be different'
        assert block.x == -2, 'x should be -2'
        assert block.y == 4, 'y should be 4'
        assert block.z == 0, 'z should be 0'

    def test_distance(self):
        vec = Vector3(1, 1, 1)
        vec2 = Vector3(2, 3, 3)
        assert vec.distance_squared(vec2) == 9, 'Squared distance between (1, 1, 1) and (2, 3, 3) should be 9'

    def test_add(self):
        assert Vector3(1, 1, 1) + Vector3(2, 2, 2) == Vector3(3, 3, 3)
        assert Vector3(1, 1, 1) + Vector3(-2, 2, 0) == Vector3(-1, 3, 1)
        assert Vector3(1, 1, 1) + (2, 2, 0) == Vector3(3, 3, 1)
        assert Vector3(1, 1, 1) + (-2, 2, 1) == Vector3(-1, 3, 2)

    def test_sub(self):
        assert Vector3(1, 1, 1) - Vector3(2, 2, 2) == Vector3(-1, -1, -1)
        assert Vector3(1, 1, 1) - Vector3(-2, 2, 0) == Vector3(3, -1, 1)
        assert Vector3(1, 1, 1) - (2, 2, 0) == Vector3(-1, -1, 1)
        assert Vector3(1, 1, 1) - (-2, 2, 1) == Vector3(3, -1, 0)

    def test_mult(self):
        assert Vector3(1, 1, 1) * 2 == Vector3(2, 2, 2)
        assert Vector3(1, 1, 1) * -1 == Vector3(-1, -1, -1)
        assert Vector3(1, 1, 1) * 0.5 == Vector3(0.5, 0.5, 0.5)
