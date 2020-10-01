from math import fmod, fsum
from random import randint

from classes.utils.Position import Position


class TestPosition:

    def test_position(self):
        for x in range(-20, 20):
            for z in range(-20, 20):
                for y in range(-20, 20):
                    pos = Position(x, y, z)
                    assert pos.x == x, 'x should be {0}, instead it\'s {1}'.format(x, pos.x)
                    assert pos.y == y, 'y should be {0}, instead it\'s {1}'.format(y, pos.y)
                    assert pos.z == z, 'z should be {0}, instead it\'s {1}'.format(z, pos.z)

    def test_clone(self):
        for x in range(-20, 20):
            for z in range(-20, 20):
                for y in range(-20, 20):
                    pos = Position(x, y, z)
                    clone = pos.clone()
                    assert pos == clone, 'clone should be the same as the original'
                    assert pos.x == clone.x, 'x should be the same. Instead x is {0} for the original' \
                                             ' and {1} for the clone'.format(pos.x, clone.x)
                    assert pos.y == clone.y, 'y should be the same. Instead y is {0} for the original' \
                                             ' and {1} for the clone'.format(pos.y, clone.y)
                    assert pos.z == clone.z, 'z should be the same. Instead z is {0} for the original' \
                                             ' and {1} for the clone'.format(pos.z, clone.z)

    def test_clone_rounded(self):
        for x in range(-20, 20):
            for z in range(-20, 20):
                for y in range(-20, 20):
                    offset_x = randint(-10, 10) / 10
                    offset_y = randint(-10, 10) / 10
                    offset_z = randint(-10, 10) / 10
                    pos = Position(fsum((x, offset_x)), fsum((y, offset_y)), fsum((z, offset_z)))
                    block = pos.clone_rounded()
                    # TODO as soon as Position.py changes, test it with a `x = a + 0.5 | (a % 1 = 1)` instead
                    # TODO as soon as Position.py changes, test it with a `z = a + 0.5 | (a % 1 = 1)` instead
                    assert block.x <= pos.x, 'Unexpected value X, got {0} for clone and {1} for original.' \
                                             ' Clone should be smaller the original'.format(block.x, pos.x)
                    assert block.y <= pos.y, 'Unexpected value Y, got {0} for clone and {1} for original.' \
                                             ' Clone should be smaller the original'.format(block.y, pos.y)
                    assert block.z <= pos.z, 'Unexpected value Z, got {0} for clone and {1} for original.' \
                                             ' Clone should be smaller the original'.format(block.z, pos.z)
                    assert fmod(block.x, 1) == 0, 'Expected x to be round, instead got an offset of {}' \
                        .format(fmod(block.x, 1))
                    assert fmod(block.y, 1) == 0, 'Expected y to be round, instead got an offset of {}' \
                        .format(fmod(block.y, 1))
                    assert fmod(block.z, 1) == 0, 'Expected z to be round, instead got an offset of {}' \
                        .format(fmod(block.z, 1))
                    # Test already round rounded Positions
                    pos = Position(x, y, z)
                    clone = pos.clone_rounded()
                    assert clone.x == pos.x, 'Unexpected value X, got {0} for clone and {1} for original.' \
                                             ' Clone should be equal to the original'.format(clone.x, pos.x)
                    assert clone.y == pos.y, 'Unexpected value Y, got {0} for clone and {1} for original.' \
                                             ' Clone should be equal to the original'.format(clone.y, pos.y)
                    assert clone.z == pos.z, 'Unexpected value Z, got {0} for clone and {1} for original.' \
                                             ' Clone should be equal to the original'.format(clone.z, pos.z)
                    assert fmod(clone.x, 1) == 0, 'Expected x to be round, instead got an offset of {}' \
                        .format(fmod(clone.x, 1))
                    assert fmod(clone.y, 1) == 0, 'Expected y to be round, instead got an offset of {}' \
                        .format(fmod(clone.y, 1))
                    assert fmod(clone.z, 1) == 0, 'Expected z to be round, instead got an offset of {}' \
                        .format(fmod(clone.z, 1))

    @staticmethod
    def _get_random_position(lower: int, upper: int, granularity: int) -> Position:
        return Position(fsum((randint(lower, upper), randint(-granularity, granularity) / granularity)),
                        fsum((randint(lower, upper), randint(-granularity, granularity) / granularity)),
                        fsum((randint(lower, upper), randint(-granularity, granularity) / granularity)))

    def test_distance(self):
        for x in range(-20, 20):
            for z in range(-20, 20):
                for y in range(-20, 20):
                    offset_x = randint(-10, 10) / 10
                    offset_y = randint(-10, 10) / 10
                    offset_z = randint(-10, 10) / 10
                    pos = Position(fsum((x, offset_x)), fsum((y, offset_y)), fsum((z, offset_z)))
                    comparator: Position = self._get_random_position(-20, 20, 10)
                    assert pos.distance_squared(comparator) >= 0, 'Distance to two locations may not be under than 0,' \
                                                                  'yet its {0}'.format(pos.distance_squared(comparator))
                    assert (abs(pos.distance(comparator)*pos.distance(comparator) - pos.distance_squared(comparator))
                            < 1), 'The difference between Distance * Distance and distance_squared is too high; ' \
                                  'Distance is {0} and distance_squared is {1}'.format(pos.distance(comparator),
                                                                                       pos.distance_squared(comparator))
                    if pos.distance_squared(comparator) > 1:
                        assert pos.distance_squared(comparator) > pos.distance(comparator), 'Distance squared should ' \
                                                                                            'be higher than distance ' \
                                                                                            '{0}, squared is {1}' \
                            .format(pos.distance(comparator), pos.distance_squared(comparator))
                    else:
                        assert pos.distance_squared(comparator) <= pos.distance(comparator), 'Distance squared should' \
                                                                                             ' be lower than distance '\
                                                                                             '{0}, squared is {1}' \
                            .format(pos.distance(comparator), pos.distance_squared(comparator))
                    offset_x = randint(-1000, 1000) / 10
                    comparator = Position(pos.x + offset_x, pos.y, pos.z)
                    assert abs(pos.distance(comparator)-abs(offset_x)) < 0.0000000001, \
                        'Unexpected distance, expected {0}, got {1}'.format(abs(offset_x), pos.distance(comparator))
                    offset_y = randint(-1000, 1000) / 10
                    comparator = Position(pos.x, pos.y + offset_y, pos.z)
                    assert abs(pos.distance(comparator)-abs(offset_y)) < 0.0000000001, \
                        'Unexpected distance, expected {0}, got {1}'.format(abs(offset_y), pos.distance(comparator))
                    offset_z = randint(-1000, 1000) / 10
                    comparator = Position(pos.x, pos.y, pos.z + offset_z)
                    assert abs(pos.distance(comparator)-abs(offset_z)) < 0.0000000001, \
                        'Unexpected distance, expected {0}, got {1}'.format(abs(offset_z), pos.distance(comparator))
