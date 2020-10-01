from pytest import raises

from math import fmod, fsum
from random import choices, randint
from string import ascii_letters, digits, whitespace

from classes.utils.Location import Location


class TestPosition:

    def test_location(self):
        for x in range(-20, 20):
            for z in range(-20, 20):
                for y in range(-20, 20):
                    world = ''.join(choices(ascii_letters + digits + whitespace, k=20))
                    loc = Location(x, y, z, world)
                    assert loc.x == x, 'x should be {0} instead it\'s {1}'.format(x, loc.x)
                    assert loc.y == y, 'y should be {0} instead it\'s {1}'.format(y, loc.y)
                    assert loc.z == z, 'z should be {0} instead it\'s {1}'.format(z, loc.z)
                    assert loc.world == world, 'world should be {0} instead it\'s {1}'.format(world, loc.world)

    def test_clone(self):
        for x in range(-20, 20):
            for z in range(-20, 20):
                for y in range(-20, 20):
                    loc = Location(x, y, z, ''.join(choices(ascii_letters + digits + whitespace, k=20)))
                    clone = loc.clone()
                    assert loc == clone, 'clone should be the same as the original'
                    assert loc.x == clone.x, 'x should be the same. Instead x is {0} for the original' \
                                             ' and {1} for the clone'.format(loc.x, clone.x)
                    assert loc.y == clone.y, 'y should be the same. Instead y is {0} for the original' \
                                             ' and {1} for the clone'.format(loc.y, clone.y)
                    assert loc.z == clone.z, 'z should be the same. Instead z is {0} for the original' \
                                             ' and {1} for the clone'.format(loc.z, clone.z)
                    assert loc.world == clone.world, 'World should be the same. Instead it is {0} for the original' \
                                                     ' and {1} for the clone'.format(loc.world, clone.world)

    def test_clone_rounded(self):
        for x in range(-20, 20):
            for z in range(-20, 20):
                for y in range(-20, 20):
                    world = ''.join(choices(ascii_letters + digits + whitespace, k=20))
                    offset_x = randint(-10, 10) / 10
                    offset_y = randint(-10, 10) / 10
                    offset_z = randint(-10, 10) / 10
                    loc = Location(fsum((x, offset_x)), fsum((y, offset_y)), fsum((z, offset_z)), world)
                    clone = loc.clone_rounded()
                    # TODO as soon as Position.py changes, test it with a `x = a + 0.5 | (a % 1 = 1)` instead
                    # TODO as soon as Position.py changes, test it with a `z = a + 0.5 | (a % 1 = 1)` instead
                    assert clone.x <= loc.x, 'Unexpected value X, got {0} for clone and {1} for original.' \
                                             ' Clone should be smaller the original'.format(clone.x, loc.x)
                    assert clone.y <= loc.y, 'Unexpected value Y, got {0} for clone and {1} for original.' \
                                             ' Clone should be smaller the original'.format(clone.y, loc.y)
                    assert clone.z <= loc.z, 'Unexpected value Z, got {0} for clone and {1} for original.' \
                                             ' Clone should be smaller the original'.format(clone.z, loc.z)
                    assert loc.world == clone.world, 'World should be the same. Instead it is {0} for the original' \
                                                     ' and {1} for the clone'.format(loc.world, clone.world)
                    assert fmod(clone.x, 1) == 0, 'Expected x to be round, instead got an offset of {}' \
                        .format(fmod(clone.x, 1))
                    assert fmod(clone.y, 1) == 0, 'Expected y to be round, instead got an offset of {}' \
                        .format(fmod(clone.y, 1))
                    assert fmod(clone.z, 1) == 0, 'Expected z to be round, instead got an offset of {}' \
                        .format(fmod(clone.z, 1))
                    # Test already round rounded Locations
                    loc = Location(x, y, z, world)
                    clone = loc.clone_rounded()
                    assert clone.x == loc.x, 'Unexpected value X, got {0} for clone and {1} for original.' \
                                             ' Clone should be equal to the original'.format(clone.x, loc.x)
                    assert clone.y == loc.y, 'Unexpected value Y, got {0} for clone and {1} for original.' \
                                             ' Clone should be equal to the original'.format(clone.y, loc.y)
                    assert clone.z == loc.z, 'Unexpected value Z, got {0} for clone and {1} for original.' \
                                             ' Clone should be equal to the original'.format(clone.z, loc.z)
                    assert loc.world == clone.world, 'World should be the same. Instead it is {0} for the original' \
                                                     ' and {1} for the clone'.format(loc.world, clone.world)
                    assert fmod(clone.x, 1) == 0, 'Expected x to be round, instead got an offset of {}' \
                        .format(fmod(clone.x, 1))
                    assert fmod(clone.y, 1) == 0, 'Expected y to be round, instead got an offset of {}' \
                        .format(fmod(clone.y, 1))
                    assert fmod(clone.z, 1) == 0, 'Expected z to be round, instead got an offset of {}' \
                        .format(fmod(clone.z, 1))

    @staticmethod
    def _get_random_location(lower: int, upper: int, granularity: int, world: str) -> Location:
        return Location(fsum((randint(lower, upper), randint(-granularity, granularity) / granularity)),
                        fsum((randint(lower, upper), randint(-granularity, granularity) / granularity)),
                        fsum((randint(lower, upper), randint(-granularity, granularity) / granularity)),
                        world)

    def test_distance(self):
        for x in range(-20, 20):
            for z in range(-20, 20):
                for y in range(-20, 20):
                    world = ''.join(choices(ascii_letters + digits + whitespace, k=20))
                    offset_x = randint(-10, 10) / 10
                    offset_y = randint(-10, 10) / 10
                    offset_z = randint(-10, 10) / 10
                    loc = Location(fsum((x, offset_x)), fsum((y, offset_y)), fsum((z, offset_z)), world)
                    comparator: Location = self._get_random_location(-20, 20, 10, world)
                    assert loc.distance_squared(comparator) >= 0, 'Distance to two locations may not be under than 0,' \
                                                                  'yet its {0}'.format(loc.distance_squared(comparator))
                    assert (abs(loc.distance(comparator)*loc.distance(comparator) - loc.distance_squared(comparator))
                            < 1), 'The difference between Distance * Distance and distance_squared is too high; ' \
                                  'Distance is {0} and distance_squared is {1}'.format(loc.distance(comparator),
                                                                                       loc.distance_squared(comparator))
                    if loc.distance_squared(comparator) > 1:
                        assert loc.distance_squared(comparator) > loc.distance(comparator), 'Distance squared should ' \
                                                                                            'be higher than distance ' \
                                                                                            '{0}, squared is {1}' \
                            .format(loc.distance(comparator), loc.distance_squared(comparator))
                    else:
                        assert loc.distance_squared(comparator) <= loc.distance(comparator), 'Distance squared should' \
                                                                                             ' be lower than distance '\
                                                                                             '{0}, squared is {1}' \
                            .format(loc.distance(comparator), loc.distance_squared(comparator))
                    offset_x = randint(-1000, 1000) / 10
                    comparator = Location(loc.x + offset_x, loc.y, loc.z, world)
                    assert abs(loc.distance(comparator)-abs(offset_x)) < 0.0000000001, \
                        'Unexpected distance, expected {0}, got {1}'.format(abs(offset_x), loc.distance(comparator))
                    offset_y = randint(-1000, 1000) / 10
                    comparator = Location(loc.x, loc.y + offset_y, loc.z, world)
                    assert abs(loc.distance(comparator)-abs(offset_y)) < 0.0000000001, \
                        'Unexpected distance, expected {0}, got {1}'.format(abs(offset_y), loc.distance(comparator))
                    offset_z = randint(-1000, 1000) / 10
                    comparator = Location(loc.x, loc.y, loc.z + offset_z, world)
                    assert abs(loc.distance(comparator)-abs(offset_z)) < 0.0000000001, \
                        'Unexpected distance, expected {0}, got {1}'.format(abs(offset_z), loc.distance(comparator))
        # Test for different worlds
        loc = Location(1, 1, 1, 'world')
        loc2 = Location(2, 3, 3, 'world_nether')
        with raises(ValueError) as excinfo:
            loc.distance(loc2)
        assert "World must be the same" in str(excinfo.value)
        with raises(ValueError) as excinfo:
            loc.distance_squared(loc2)
        assert "World must be the same" in str(excinfo.value)
