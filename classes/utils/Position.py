from math import sqrt, floor


class Position:

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return Position(self.x, self.y, self.z)

    def clone_rounded(self):
        clone = self.clone()
        clone.x = floor(clone.x)
        clone.y = floor(clone.y)
        clone.z = floor(clone.z)
        return clone

    def distance_squared(self, pos):
        return (self.x - pos.x)**2 + (self.y - pos.y)**2 + (self.z - pos.z)**2

    def distance(self, pos):
        return sqrt(self.distance_squared(pos))

    def __eq__(self, pos):
        return self.x == pos.x and self.y == pos.y and self.z == pos.z
