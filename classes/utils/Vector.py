from math import sqrt, floor


class Vector2D:

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def clone(self):
        return Vector2D(self.x, self.y)

    def clone_rounded(self):
        return Vector2D(floor(self.x), floor(self.y))

    def distance_squared(self, pos):
        if type(pos) is tuple:
            return (self.x - pos[0])**2 + (self.y - pos[1])**2
        return (self.x - pos.x)**2 + (self.y - pos.y)**2

    def distance(self, pos):
        return sqrt(self.distance_squared(pos))

    def __add__(self, other):
        if type(other) is tuple:
            return Vector2D(self.x + other[0], self.y + other[1])
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if type(other) is tuple:
            return Vector2D(self.x - other[0], self.y - other[1])
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, mult):
        return Vector2D(self.x * mult, self.y * mult)

    def __truediv__(self, div):
        return Vector2D(self.x / div, self.y / div)

    def __floordiv__(self, div):
        return Vector2D(self.x // div, self.y // div)

    def __eq__(self, other):
        if type(other) is tuple:
            return self.x == other[0] and self.y == other[1]
        return self.x == other.x and self.y == other.y


class Vector3D:

    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def clone(self):
        return Vector3D(self.x, self.y, self.z)

    def clone_rounded(self):
        return Vector3D(floor(self.x), floor(self.y), floor(self.z))

    def distance_squared(self, pos):
        if type(pos) is tuple:
            return (self.x - pos[0])**2 + (self.y - pos[1])**2 + (self.z - pos[2])**2
        return (self.x - pos.x)**2 + (self.y - pos.y)**2 + (self.z - pos.z)**2

    def distance(self, pos):
        return sqrt(self.distance_squared(pos))

    def __add__(self, other):
        if type(other) is tuple:
            return Vector3D(self.x + other[0], self.y + other[1], self.z + other[2])
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if type(other) is tuple:
            return Vector3D(self.x - other[0], self.y - other[1], self.z - other[2])
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, mult):
        return Vector3D(self.x * mult, self.y * mult, self.z * mult)

    def __truediv__(self, div):
        return Vector3D(self.x / div, self.y / div, self.z / div)

    def __floordiv__(self, div):
        return Vector3D(self.x // div, self.y // div, self.z // div)

    def __eq__(self, pos):
        return self.x == pos.x and self.y == pos.y and self.z == pos.z
