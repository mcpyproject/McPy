import classes.Server as Server

from ..utils.Thread import AtomicInteger
from ..utils.Vector import Vector3D


class Entity:
    """
    Basic class for an entity: designed to be subclassed, never instansiated directly
    """

    def __init__(self, entity_id, entity_location: Vector3D, world, x_rot=0, y_rot=0, nbt_tags: dict = {}):
        self.entity_id = entity_id
        self.entity_location = entity_location
        self.world = world
        self.x_rotation = x_rot
        self.y_rotation = y_rot
        self.velocity = Vector3D(0, 0, 0)
        self.nbt = nbt_tags

    def move(self, entity_location, x_rot=None, y_rot=None):
        self.entity_location = entity_location
        if x_rot is not None:
            self.x_rotation = x_rot
        if y_rot is not None:
            self.y_rotation = y_rot

    def tick(self, current_tick):
        """
        Ticks self: does nothing at root entity
        """
        pass  # TODO: add ticking function for all entities: will be subclassed if required


class EntityManager():

    def __init__(self, server: Server):
        self.server = server
        self.atomic_id = AtomicInteger()
        self.entities: [int, Entity] = {}

    def make_entity(self, entity_class: Entity, entity_location: Vector3D, world, **kwargs):
        entity_id = self.atomic_id.get_and_increment()
        entity = entity_class(entity_id, entity_location, world, x_rot=0, y_rot=0, **kwargs)
        self.entities[str(entity_id)] = entity
        return entity

    def destroy_entity(self, entity_id):
        if entity_id in self.entities:
            entity = self.entities[str(entity_id)]
            del self.entities[str(entity_id)]
            # TODO Send destroy packet to near players

    def get_entity(self, entity_id):
        return self.entities[entity_id] if entity_id in self.entities else None

    def tick(self, current_tick):
        for entity in self.entities.values():
            entity.tick(current_tick)
