from .Position import Position


class Location(Position):

    def __init__(self, x=0, y=0, z=0, world=None):
        assert world is not None, 'World should exist !'
        super(Location, self).__init__(x, y, z)
        self.world = world

    def clone(self):
        return Location(self.x, self.y, self.z, self.world)

    def clone_rounded(self):
        clone = super(Location, self).clone_rounded()
        clone.world = self.world
        return clone

    def distance_squared(self, pos):
        assert self.world == pos.world, 'World must be the same to calculate squared distance between two Location'
        return super(Location, self).distance_squared(pos)

    def distance(self, pos):
        assert self.world == pos.world, 'World must be the same to calculate distance between two Location'
        return super(Location, self).distance(pos)

    def __eq__(self, pos):
        return self.world == pos.world and super(Location, self).__eq__(pos)
