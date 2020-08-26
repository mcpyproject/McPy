# coding=utf-8


class Entity:
    """
    Basic class for a entity: designed to be subclassed, never instansiated directly
    """

    def __init__(self, x, y, z, x_rot, y_rot, x_vel, y_vel, z_vel, nbt_tags: dict):
        self.x = x
        self.y = y
        self.z = z
        self.x_rotation = x_rot
        self.y_rotation = y_rot
        self.x_velocity = x_vel
        self.y_velocity = y_vel
        self.z_velocity = z_vel
        self.nbt = nbt_tags

    def move_abs(self, x, y, z, x_rot=None, y_rot=None, x_vel=None, y_vel=None, z_vel=None):
        self.x = x
        self.y = y
        self.z = z
        if x_rot is not None:
            self.x_rotation = x_rot
        if y_rot is not None:
            self.y_rotation = y_rot
        if x_vel is not None:
            self.x_velocity = x_vel
        if y_vel is not None:
            self.y_velocity = y_vel
        if z_vel is not None:
            self.z_velocity = z_vel

    def move_rel(self, x, y, z):
        """
        Moves relative to current position
        :param x:
        :param y:
        :param z:
        """
        self.x = self.x + x
        self.y = self.y + y
        self.z = self.z + z

    def tick(self):
        """
        Ticks self: does nothing at root entity
        """
        pass  # TODO: add ticking function for all entities: will be subclassed if required
