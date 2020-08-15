# coding=utf-8


class Entity:
    def __init__(self, x, y, z, xRot, yRot, xVel, yVel, zVel, nbtTags: dict):
        self.x = x
        self.y = y
        self.z = z
        self.xRotation = xRot
        self.yRotation = yRot
        self.xVelocity = xVel
        self.yVelocity = yVel
        self.zVelocity = zVel
        self.nbt = nbtTags

    def moveAbs(self, x, y, z, xRot=None, yRot=None, xVel=None, yVel=None, zVel=None):
        self.x = x
        self.y = y
        self.z = z
        if xRot is not None:
            self.xRotation = xRot
        if yRot is not None:
            self.yRotation = yRot
        if xVel is not None:
            self.xVelocity = xVel
        if yVel is not None:
            self.yVelocity = yVel
        if zVel is not None:
            self.zVelocity = zVel

    def moveRel(self, x, y, z):
        self.x = self.x + x
        self.y = self.y + y
        self.z = self.z + z

    def tick(self):
        pass  # TODO: add ticking function for all entities: will be subclassed if required
