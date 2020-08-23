from math import sqrt


class Position:

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return Position(self.x, self.y, self.z)

    def clone_rounded(self):
        clone = self.clone()
        clone.x = int(clone.x) - (1 if clone.x < 0 else 0)
        clone.y = int(clone.y) - (1 if clone.y < 0 else 0)
        clone.z = int(clone.z) - (1 if clone.z < 0 else 0)
        return clone

    def distance_squared(self, pos):
        return (self.x - pos.x)**2 + (self.y - pos.y)**2 + (self.z - pos.z)**2

    def distance(self, pos):
        return sqrt(self.distance_squared(pos))

    def __eq__(self, pos):
        return self.x == pos.x and self.y == pos.y and self.z == pos.z
