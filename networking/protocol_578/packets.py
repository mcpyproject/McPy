import string
import struct
import sys

from dataclasses import dataclass, fields
from networking.protocol_578 import packet_ids
from networking.util.datatypes import *
from typing import Dict, List, Optional, Tuple, Union


# Todo: At some point, fill in to_bytes() everywhere - ONLY if (stress)testing shows it's faster.
# Also; record a casual gameplay, and see what packets are the most common (eg. try beating the game)
# We can use that information to optimize those packet classes.


@dataclass
class Packet:
    @property
    def packet_id(self) -> str:
        value = getattr(self, "_packet_id", None)
        if value is not None:
            return value
        s = type(self).__name__  # Equivalent to self.__class__.__name__
        for char in string.ascii_uppercase:
            s = s.replace(char, f"_{char}")
        return packet_ids[s.replace("_", "", 1)]  # 2nd .replace() in there to rid leading _
    
    def to_bytes(self):
        """
        Default parent function to encode basic packet types. All variables must have the correct type indicated on
        them, using first the datatypes defined in networking.util.datatypes. Position types are default encoded
        using the new format. Bytes types will be directly inserted into the packet as-is; if more control is needed
        (see Encryption Request packet), then this method must be overridden. Raises NotImplemented upon any error,
        so that it can be seen what may need custom packet writing implementations. HOWEVER, this will not save you
        from an *incorrectly* formatted packet.
        
        :return: Best-guess encoded packet.
        """
        try:
            _fields: Tuple = fields(self)
            out = b""
            for item in _fields:
                value = getattr(self, item.name, None)
                if value is None:
                    raise LookupError("we are in a *seriously* invalid state here, yikes.")
                # Distant todo: Optimize loop by finding most common types in practice and order by that
                if isinstance(item.type, StructType):
                    out += struct.pack(">" + item.type.code, value)
                    continue
                if isinstance(item.type, bool):
                    out += b"\x01" if value else b"\x00"
                    continue
                if isinstance(item.type, VarInt):
                    out += VarInt.encode(value)
                    continue
                if isinstance(item.type, String) or isinstance(item.type, str):
                    out += String.encode(value)
                    continue
                if isinstance(item.type, Position):
                    out += value.encode()
                    continue
                if isinstance(item.type, UUID):
                    out += UUID.encode(value)
                    continue
                if isinstance(item.type, EntityVelocityType):
                    out += EntityVelocityType.encode(value)
                    continue
                if isinstance(item.type, VarLong):
                    out += VarLong.encode(value)
                    continue
                if isinstance(item.type, bytes):
                    out += value
                    continue
                raise NotImplemented
            
            return out
        except Exception as e:
            # log()
            pass
        raise NotImplemented
    
    @classmethod
    def from_bytes(cls, buffer: bytes):
        """
        Default parent function to decode simpler packet types. Will attempt to decode packets based on their given
        field types, then will return a new object of themselves with the provided data. This works based on the
        provided fields for dataclasses; if more control over decoding is needed, then this method must be
        overridden. Raises NotImplemented on any error.
        
        :param buffer: The data to read in from this packet.
        :return: Best guess decoded packet.
        """
        try:
            _fields: Tuple = fields(cls)
            data = {}
            for item in _fields:
                if isinstance(item.type, StructType):
                    data[item.name], = struct.unpack(">" + item.type.code, buffer[:item.type.size])
                    buffer = buffer[item.type.size:]
                    continue
                if isinstance(item.type, VarInt):
                    data[item.name], buffer = VarInt.decode(buffer)
                    continue
                if isinstance(item.type, String):
                    data[item.name], buffer = String.decode(buffer)
                    continue
                if isinstance(item.type, Position):
                    data[item.name] = Position.from_bytes(buffer[:8])
                    buffer = buffer[8:]
                    continue
                if isinstance(item.type, UUID):
                    data[item.name] = UUID.bytes_to_str(buffer[:16])
                    buffer = buffer[16:]
                    continue
                if isinstance(item.type, EntityVelocityType):
                    data[item.name] = EntityVelocityType.decode(buffer)
                    buffer = buffer[16:]
                    continue
                if isinstance(item.type, VarLong):
                    data[item.name], buffer = VarLong.decode(buffer)
                    continue
                if isinstance(item.type, bytes):
                    raise NotImplemented
            return cls(**data)  # This metaclass technically doesn't have anything so Python is just gonna complain
        except Exception as e:
            # log()
            pass


# There are no clientbound packets in the Handshaking state, since the protocol
# immediately switches to a different state after the client sends the first packet.
#  -- From wiki.vg editors (IRC #mcdevs @ chat.freenode.net)

# ----------------------
# Handshaking Mode Packets: Serverbound
# ----------------------


class Handshake(Packet):
    def __init__(self, data):
        self.protocol_version, data = VarInt.decode(data)
        self.server_address, data = String.decode(data)
        self.server_port = struct.unpack(">H", data[:2])
        self.next_state, _ = VarInt.decode(data[2:])


class LegacyServerListPing(Packet):
    pass


# ----------------------
# Status Mode Packets: Clientbound
# ----------------------


@dataclass
class Response(Packet):
    response: str


@dataclass
class Pong(Packet):
    payload: Long


# ----------------------
# Status Mode Packets: Serverbound
# ----------------------


class Request(Packet):
    def __init__(self, data):
        self.data = data


class Ping(Packet):
    def __init__(self, data):
        self.payload = struct.unpack(">q", data)[0]


# ----------------------
# Login Mode Packets: Clientbound
# ----------------------


@dataclass
class DisconnectLogin(Packet):
    reason: String


@dataclass
class EncryptionRequest(Packet):
    server_id: String
    pubkey: bytes
    verify_token: bytes
    
    def to_bytes(self):
        return String.encode(self.server_id) + \
               VarInt.encode(len(self.pubkey)) + \
               self.pubkey + \
               VarInt.encode(len(self.verify_token)) + \
               self.verify_token


@dataclass
class LoginSuccess(Packet):
    uuid: UUID
    username: String


@dataclass
class SetCompression(Packet):
    threshold: VarInt


@dataclass
class LoginPluginRequest(Packet):
    message_id: VarInt
    channel: Identifier
    data: bytes


# ----------------------
# Login Mode Packets: Serverbound
# ----------------------


class LoginStart(Packet):
    def __init__(self, packet):
        self.username, _ = String.decode(packet)


class EncryptionResponse(Packet):
    def __init__(self, packet):
        secret_len, packet = VarInt.decode(packet)
        self.secret = packet[:secret_len]
        token_len, packet = VarInt.decode(packet)
        self.token = packet[:token_len]


class LoginPluginResponse(Packet):
    def __init__(self, packet):
        self.message_id, packet = VarInt.decode(packet)
        self.successful = struct.unpack(">?", packet[0])
        self.data = packet[1:]


# ----------------------
# Play Mode Packets: Clientbound
# ----------------------


@dataclass
class SpawnEntity(Packet):
    entity_id: VarInt
    object_uuid: UUID
    entity_type: VarInt
    x: Double
    y: Double
    z: Double
    pitch: Angle
    yaw: Angle
    data: Int
    v_x: EntityVelocityType
    v_y: EntityVelocityType
    v_z: EntityVelocityType


@dataclass
class SpawnExperienceOrb(Packet):
    entity_id: VarInt
    x: Double
    y: Double
    z: Double
    count: Short


@dataclass
class SpawnWeatherEntity(Packet):
    entity_id: VarInt
    entity_type: Byte
    x: Double
    y: Double
    z: Double


@dataclass
class SpawnLivingEntity(Packet):
    entity_id: VarInt
    entity_uuid: UUID
    entity_type: VarInt
    x: Double
    y: Double
    z: Double
    yaw: Angle
    pitch: Angle
    head_pitch: Angle
    v_x: EntityVelocityType
    v_y: EntityVelocityType
    v_z: EntityVelocityType


@dataclass
class SpawnPainting(Packet):
    entity_id: VarInt
    entity_uuid: UUID
    painting_id: VarInt
    location: Position
    direction: Byte


@dataclass
class SpawnPlayer(Packet):
    entity_id: VarInt
    player_uuid: UUID
    x: Double
    y: Double
    z: Double
    yaw: Angle
    pitch: Angle


@dataclass
class EntityAnimationClientbound(Packet):
    entity_id: VarInt
    animation: UnsignedByte


@dataclass
class Statistics(Packet):
    data: List[Dict[str, int]]  # A JSON array of {category: x, statistic: y, value: z}
    
    def to_bytes(self):
        data = b""
        data += VarInt.encode(len(self.data))
        for item in self.data:
            data += VarInt.encode(item["category"])  # Todo: Create JSON listing of statistic category namespaces
            data += VarInt.encode(item["statistic"])  # Todo: Create JSON listing of each stat. (JSON listings should
            data += VarInt.encode(item["value"])  # go in their own file)
        return data


@dataclass
class AcknowledgePlayerDigging(Packet):
    location: Position
    block: VarInt
    status: VarInt  # 0=started digging, 1=cancel digging, 2=finish digging
    success: Boolean


@dataclass
class BlockBreakAnimation(Packet):
    entity_id: VarInt
    location: Position
    stage: Byte


@dataclass
class BlockEntityData(Packet):
    location: Position
    action: UnsignedByte
    nbt_data: bytes
    
    def to_bytes(self):
        raise NotImplementedError("Todo: Figure out how NBT data works; who that should be handled by; if network "
                                  "implementation is different, etc")


@dataclass
class BlockAction(Packet):
    location: Position
    action_id: UnsignedByte
    action_param: UnsignedByte
    block_type: VarInt
    
    def to_bytes(self):
        raise NotImplementedError("Todo: Figure out block types lookup; that is probably something handled by either "
                                  "the calling function, or by us if we go and look it up vs. server's list of blocks")


@dataclass
class BlockChange(Packet):
    location: Position
    block_id: VarInt  # New block state ID for it
    
    def to_bytes(self):
        raise NotImplementedError("Todo: Figure out block types lookup; that is probably something handled by either "
                                  "the calling function, or by us if we go and look it up vs. server's list of blocks")


@dataclass
class BossBarMeta:
    def __post_init__(self):
        self._packet_id = 0x0d


@dataclass
class BossBarAdd(Packet, BossBarMeta):
    uuid: UUID
    title: Chat
    health: Float
    color: VarInt
    division: VarInt
    flags: UnsignedByte
    
    def to_bytes(self):
        return UUID.encode(self.uuid) + \
               b"\x00" + \
               Chat.encode(self.title) + \
               struct.pack(">f", self.health) + \
               VarInt.encode(self.color) + \
               VarInt.encode(self.division) + \
               struct.pack(">B", self.flags)


@dataclass
class BossBarRemove(Packet, BossBarMeta):
    uuid: UUID
    action: VarInt = 1


@dataclass
class BossBarUpdateHealth(Packet, BossBarMeta):
    uuid: UUID
    health: Float
    
    def to_bytes(self):
        return UUID.encode(self.uuid) + \
               b"\x02" + \
               struct.pack(">f", self.health)


@dataclass
class BossBarUpdateTitle(Packet, BossBarMeta):
    uuid: UUID
    title: Chat
    
    def to_bytes(self):
        return UUID.encode(self.uuid) + \
               b"\x03" + \
               Chat.encode(self.title)


@dataclass
class BossBarUpdateStyle(Packet, BossBarMeta):
    uuid: UUID
    color: VarInt
    dividers: VarInt
    
    def to_bytes(self):
        return UUID.encode(self.uuid) + \
               b"\x04" + \
               VarInt.encode(self.color) + \
               VarInt.encode(self.dividers)


@dataclass
class BossBarUpdateFlags(Packet, BossBarMeta):
    uuid: UUID
    flags: UnsignedByte
    
    def to_bytes(self):
        return UUID.encode(self.uuid) + \
               b"\x05" + \
               struct.pack(">B", self.flags)


@dataclass
class ServerDifficulty(Packet):
    difficulty: UnsignedByte
    locked: Boolean


@dataclass
class ChatMessageClientbound(Packet):
    message: Chat
    type: Byte


@dataclass
class MultiBlockChange(Packet):
    raise NotImplementedError


@dataclass
class TabCompleteClientbound(Packet):
    transaction_id: VarInt
    start_loc: VarInt
    replace_length: VarInt
    matches: List[Dict[str, str]]
    
    # [{"match": "stuff", "tooltip": "Chat Object Here"}]
    
    def to_bytes(self):
        data = VarInt.encode(self.transaction_id) + \
               VarInt.encode(self.start_loc) + \
               VarInt.encode(self.replace_length) + \
               VarInt.encode(len(self.matches))
        for match in self.matches:
            data += String.encode(match["match"])
            tooltip = match.get("tooltip", None)
            if tooltip is not None:
                data += b"\x01" + String.encode(tooltip)
            else:
                data += b"\x00"
        return data


@dataclass
class DeclareCommands(Packet):
    raise NotImplementedError


@dataclass
class WindowConfirmationClientbound(Packet):
    window_id: Byte
    action_number: Short
    accepted: Boolean


@dataclass
class CloseWindowClientbound(Packet):
    window_id: UnsignedByte


@dataclass
class WindowItems(Packet):
    def __post_init__(self):
        raise NotImplementedError


@dataclass
class WindowProperty(Packet):
    window_id: UnsignedByte
    property: Short
    value: Short


@dataclass
class SetSlot(Packet):
    # window_id: Byte
    # slot: Short
    # data: Slot
    def __post_init__(self):
        raise NotImplementedError


@dataclass
class SetCooldown(Packet):
    item_id: VarInt
    cooldown: VarInt


@dataclass
class PluginMessageClientbound(Packet):
    channel: Identifier
    data: bytes


@dataclass
class NamedSoundEffect(Packet):
    name: Identifier
    category: VarInt
    pos_x: float
    pos_y: float
    pos_z: float
    volume: Float = 1.0
    pitch: Float = 1.0
    
    def to_bytes(self):
        return Identifier.encode(self.name) + \
               VarInt.encode(self.category) + \
               struct.pack(">iiiff",
                           self.pos_x * 8,
                           self.pos_y * 8,
                           self.pos_z * 8,
                           self.volume,
                           self.pitch)


@dataclass
class DisconnectPlay(Packet):
    reason: Chat


@dataclass
class EntityStatus(Packet):
    entity_id: Int
    entity_status: Byte


@dataclass
class Explosion(Packet):
    x: Float
    y: Float
    z: Float
    strength: Float
    affected_blocks: List[Tuple[Byte, Byte, Byte]]
    player_v_x: Float
    player_v_y: Float
    player_v_z: Float
    
    def to_bytes(self):
        data = struct.pack(">ffffi",
                           self.x,
                           self.y,
                           self.z,
                           self.strength,
                           len(self.affected_blocks))
        for x, y, z in self.affected_blocks:
            data += struct.pack(">b", x, y, z)
        return data + struct.pack(">fff",
                                  self.player_v_x,
                                  self.player_v_y,
                                  self.player_v_z)


@dataclass
class UnloadChunk(Packet):
    chunk_x: Int
    chunk_z: Int


@dataclass
class ChangeGameState(Packet):
    reason: UnsignedByte
    value: Float


@dataclass
class OpenHorseWindow(Packet):
    window_id: Byte
    slot_count: VarInt
    entity_id: Int


class KeepAliveClientbound(Packet):
    # As this is obviously going to be a commonly sent packet, this one will not use the shared dataclass structure.
    def __init__(self, payload: int):
        self.payload = payload
    
    def to_bytes(self):
        return struct.pack(">q", self.payload)


class ChunkData(Packet):
    # this one should also be specially written
    raise NotImplementedError("god help us")


@dataclass
class Effect(Packet):
    effect_id: Int
    location: Position
    data: Int
    disable_relative_volume: Boolean


@dataclass
class Particle(Packet):
    particle_id: Int
    long_distance: Boolean
    x: Double
    y: Double
    z: Double
    offset_x: Float
    offset_y: Float
    offset_z: Float
    data: Float
    count: Int
    data: bytes
    
    def __post_init__(self):
        raise NotImplementedError("depends on particle-specific data (`data` field)")


@dataclass
class UpdateLight(Packet):
    raise NotImplementedError


@dataclass
class JoinGame(Packet):
    entity_id: Int
    gamemode: UnsignedByte
    dimension: Int
    seed_hash: Long
    max_players: UnsignedByte  # This field is ignored now
    level_type: String
    view_distance: VarInt
    reduced_debug_info: Boolean
    enable_respawn_screen: Boolean


@dataclass
class MapData(Packet):
    map_id: VarInt
    scale: Byte
    tracking_position: Boolean
    locked: Boolean
    icons: List[Tuple[VarInt, Byte, Byte, Byte, Optional[Chat]]]
    columns: UnsignedByte
    rows: Optional[Byte] = None
    x: Optional[Byte] = None
    z: Optional[Byte] = None
    data: Optional[bytes] = None
    
    def to_bytes(self):
        data = b""
        data += VarInt.encode(self.map_id)
        data += struct.pack(">b??",
                            self.scale,
                            self.tracking_position,
                            self.locked)
        data += VarInt.encode(len(self.icons))
        for icon in self.icons:
            data += VarInt.encode(icon[0])
            data += struct.pack(">bbb", icon[1], icon[2], icon[3])
            if len(icon) == 5:
                data += b"\x01" + Chat.encode(icon[4])
            else:
                data += b"\x00"
        
        data += struct.pack(">B", self.columns)
        if self.columns:
            data += struct.pack(">bbb", self.rows, self.x, self.z)
            data += VarInt.encode(len(self.data))
            data += self.data
        return data


@dataclass
class TradeList(Packet):
    def __post_init__(self):
        raise NotImplementedError


@dataclass
class EntityPosition(Packet):
    entity_id: VarInt
    dx: float
    dy: float
    dz: float
    on_ground: bool
    
    def to_bytes(self):
        return VarInt.encode(self.entity_id) + \
               struct.pack(">hhh?",
                           int(self.dx * 4096),
                           int(self.dy * 4096),
                           int(self.dz * 4096),
                           self.on_ground)


@dataclass
class EntityPositionAndRotation(Packet):
    entity_id: VarInt
    dx: float
    dy: float
    dz: float
    yaw: Angle
    pitch: Angle
    on_ground: bool
    
    def to_bytes(self):
        out = VarInt.encode(self.entity_id)
        out += struct.pack(">hhh",
                           int(self.dx * 4096),
                           int(self.dy * 4096),
                           int(self.dz * 4096),
                           self.on_ground)
        raise NotImplementedError("`Angle` datatypes")


@dataclass
class EntityRotation(Packet):
    entity_id: VarInt
    yaw: Angle
    pitch: Angle
    on_ground: Boolean


@dataclass
class EntityMovement(Packet):
    # is this packet even real? wiki.vg says it has no fields, which doesn't make sense...
    entity_id: VarInt


@dataclass
class VehicleMoveClientbound(Packet):
    x: Double
    y: Double
    z: Double
    yaw: Float
    pitch: Float


@dataclass
class OpenBook(Packet):
    hand: VarInt


@dataclass
class OpenWindow(Packet):
    window_id: VarInt
    window_type: VarInt
    window_title: Chat


@dataclass
class OpenSignEditor(Packet):
    location: Position


@dataclass
class CraftRecipeResponse(Packet):
    window_id: Byte
    recipe: Identifier


@dataclass
class PlayerAbilitiesClientbound(Packet):
    invulnerable: bool
    flying: bool
    allow_flight: bool
    creative_instant_break: bool
    fly_speed: Float
    fov_modifier: Float
    
    def to_bytes(self):
        return struct.pack(">Bff",
                           (self.creative_instant_break << 3) |
                           (self.allow_flight << 2) |
                           (self.flying << 1) |
                           self.invulnerable,
                           self.fly_speed,
                           self.fov_modifier)


@dataclass
class CombatEvent(Packet):
    victim_id: VarInt
    killer_id: Int
    death_message: Chat
    
    def to_bytes(self):
        return VarInt.encode(self.victim_id) + \
               struct.pack(">i", self.killer_id) + \
               Chat.encode(self.death_message)


@dataclass
class PlayerInfo(Packet):
    """
    Sent by the server to update the user list. `player_data` is always a List type of the given Dict[]s.
    
    action = 0: Add Player
        player_data: {
            "uuid": UUID,
            "name": String,
            "properties": [
                {
                    "name": String,
                    "value": String,
                    "signature": String (optional)
                }
            ],
            "gamemode": VarInt,
            "ping": float (seconds),
            "display_name": Chat (optional)
        }
    
    action = 1: Update Gamemode
        player_data: {
            "uuid": UUID,
            "gamemode": VarInt
        }

    action = 2: Update Latency
        player_data: {
            "uuid": UUID,
            "ping": float (seconds)
        }

    action = 3: Update Display Name
        player_data: {
            "uuid": UUID,
            "display_name": Chat (optional)
        }

    action = 4: Remove Player
        player_data: {
            "uuid": UUID
        }
    """
    action: VarInt
    player_data: List
    
    def to_bytes(self):
        if self.action == 0:
            return self._action_0()
        if self.action == 1:
            return self._action_1()
        if self.action == 2:
            return self._action_2()
        if self.action == 3:
            return self._action_3()
        if self.action == 4:
            return self._action_4()
    
    def _action_0(self):
        out = b"\x00"
        out += VarInt.encode(len(self.player_data))
        for entry in self.player_data:
            out += UUID.encode(entry["uuid"])
            out += String.encode(entry["name"])
            out += VarInt.encode(len(entry["properties"]))
            for p in entry["properties"]:
                out += String.encode(p["name"])
                out += String.encode(p["value"])
                signature = p.get("signature", None)
                if signature is not None:
                    out += b"\x01" + String.encode(signature)
                else:
                    out += b"\x00"
            out += VarInt.encode(entry["gamemode"])
            out += VarInt.encode(int(entry["ping"] * 1000))
            disp = entry.get("display_name", None)
            if disp is not None:
                out += b"\x01" + Chat.encode(disp)
            else:
                out += b"\x00"
        return out
    
    def _action_1(self):
        out = b"\x01"
        out += VarInt.encode(len(self.player_data))
        for entry in self.player_data:
            out += UUID.encode(entry["uuid"])
            out += VarInt.encode(entry["gamemode"])
        return out
    
    def _action_2(self):
        out = b"\x02"
        out += VarInt.encode(len(self.player_data))
        for entry in self.player_data:
            out += UUID.encode(entry["uuid"])
            out += VarInt.encode(int(entry["ping"] * 1000))
        return out
    
    def _action_3(self):
        out = b"\x03"
        out += VarInt.encode(len(self.player_data))
        for entry in self.player_data:
            out += UUID.encode(entry["uuid"])
            disp = entry.get("display_name", None)
            if disp is not None:
                out += b"\x01" + Chat.encode(disp)
            else:
                out += b"\x00"
        return out
    
    def _action_4(self):
        out = b"\x04"
        out += VarInt.encode(len(self.player_data))
        out += b"".join([UUID.encode(x["uuid"]) for x in self.player_data])
        return out


@dataclass
class FacePlayer(Packet):
    feet_or_eyes: VarInt
    target_x: Double
    target_y: Double
    target_z: Double
    entity_id: VarInt = None
    entity_feet_or_eyes: VarInt = None
    
    def to_bytes(self):
        entity = (self.entity_id is not None) and (self.entity_feet_or_eyes is not None)
        data = VarInt.encode(self.feet_or_eyes) + \
            struct.pack(">ddd?",
                        self.target_x,
                        self.target_y,
                        self.target_z,
                        entity)
        if entity:
            data += VarInt.encode(self.entity_id)
            data += VarInt.encode(self.entity_feet_or_eyes)
        return data


@dataclass
class PlayerPositionAndLookClientbound(Packet):
    x: Double
    y: Double
    z: Double
    yaw: Float
    pitch: Float
    relative_x: bool
    relative_y: bool
    relative_z: bool
    relative_yaw: bool
    relative_pitch: bool
    teleport_id: VarInt
    
    def to_bytes(self):
        return struct.pack(">dddffB",
                           self.x,
                           self.y,
                           self.z,
                           self.yaw,
                           self.pitch,
                           self.relative_yaw << 4 |
                           self.relative_pitch << 3 |
                           self.relative_z << 2 |
                           self.relative_y << 1 |
                           self.relative_x) + \
               VarInt.encode(self.teleport_id)


@dataclass
class UnlockRecipes(Packet):
    """action: 0=init, 1=add, 2=remove; if action=0, array2 must be provided. See wiki.vg for details."""
    action: VarInt
    crafting_recipe_book_open: Boolean
    crafting_recipe_book_filter_active: Boolean
    smelting_recipe_book_open: Boolean
    smelting_recipe_book_filter_active: Boolean
    recipes: List[Identifier]
    recipes2: List[Identifier] = None
    
    def to_bytes(self):
        data = VarInt.encode(self.action)
        data += struct.pack(">????",
                            self.crafting_recipe_book_open,
                            self.crafting_recipe_book_filter_active,
                            self.smelting_recipe_book_open,
                            self.smelting_recipe_book_filter_active)
        data += VarInt.encode(len(self.recipes))
        for item in self.recipes:
            data += Identifier.encode(item)
        if self.action == 0:
            if self.recipes2 is None:
                raise RuntimeError("Packet UnlockRecipes: action=0 (init) but recipes2 not provided")
            data += VarInt.encode(len(self.recipes2))
            for item in self.recipes:
                data += Identifier.encode(item)
        return data


@dataclass
class DestroyEntities(Packet):
    entities: List[VarInt]
    
    def to_bytes(self):
        return VarInt.encode(len(self.entities)) + b"".join([VarInt.encode(x) for x in self.entities])


@dataclass
class RemoveEntityEffect(Packet):
    entity_id: VarInt
    effect_id: Byte  # May want this in an Enum (see wiki.vg)


@dataclass
class ResourcePackSend(Packet):
    url: str
    hash: str
    
    def to_bytes(self):
        return String.encode(self.url) + String.encode(self.hash.lower())


@dataclass
class Respawn(Packet):
    dimension: Int
    hashed_seed: Long
    gamemode: UnsignedByte
    level_type: String


@dataclass
class EntityHeadLook(Packet):
    entity_id: VarInt
    new_yaw: Angle


@dataclass
class SelectAdvancementTab(Packet):
    identifier: Identifier = None
    
    def to_bytes(self):
        if self.identifier is None:
            return b"\x00"
        else:
            return b"\x01" + Identifier.encode(self.identifier)


@dataclass
class WorldBorderMeta:
    def __post_init__(self):
        self._packet_id = 0x3e


@dataclass
class WorldBorderSetSize(Packet, WorldBorderMeta):
    diameter: Double
    
    def to_bytes(self):
        return b"\x00" + struct.pack(">d", self.diameter)


@dataclass
class WorldBorderChangeSize(Packet, WorldBorderMeta):
    old_diameter: Double
    new_diameter: Double
    speed: VarLong
    
    def to_bytes(self):
        return b"\x01" + \
               struct.pack(">dd",
                           self.old_diameter,
                           self.new_diameter) + \
               VarLong.encode(self.speed)


@dataclass
class WorldBorderSetCenter(Packet, WorldBorderMeta):
    x: Double
    z: Double
    
    def to_bytes(self):
        return b"\x02" + struct.pack(">dd", self.x, self.z)


@dataclass
class WorldBorderInitialize(Packet, WorldBorderMeta):
    x: Double
    z: Double
    old_diameter: Double
    new_diameter: Double
    speed: VarLong
    portal_teleport_boundary: VarInt
    warning_time: VarInt
    warning_blocks: VarInt
    
    def to_bytes(self):
        # data = b"\x03"
        # data += struct.pack(">dddd",
        #                     self.x,
        #                     self.z,
        #                     self.old_diameter,
        #                     self.new_diameter)
        # data += VarLong.encode(self.speed)
        # data += VarInt.encode(self.portal_teleport_boundary)
        # data += VarInt.encode(self.warning_time)
        # data += VarInt.encode(self.warning_blocks)
        # return data
        # Todo: Check this returns correct packets?
        return b"\x03" + super(WorldBorderInitialize, self).to_bytes()


@dataclass
class WorldBorderSetWarningTime(Packet, WorldBorderMeta):
    warning_time: VarInt
    
    def to_bytes(self):
        return b"\x04" + super(WorldBorderSetWarningTime, self).to_bytes()


@dataclass
class WorldBorderSetWarningBlocks(Packet, WorldBorderMeta):
    warning_blocks: VarInt
    
    def to_bytes(self):
        return b"\x05" + super(WorldBorderSetWarningBlocks, self).to_bytes()


@dataclass
class Camera(Packet):
    camera_entity_id: VarInt


@dataclass
class HeldItemChangeClientbound(Packet):
    slot: Byte


@dataclass
class UpdateViewPosition(Packet):
    chunk_x: VarInt
    chunk_z: VarInt


# @dataclass
# class UpdateViewDistance(Packet):
#     view_distance: VarInt


@dataclass
class DisplayScoreboard(Packet):
    position: Byte
    score_name: String


@dataclass
class EntityMetadata(Packet):
    entity_id: VarInt
    metadata: bytes
    
    def to_bytes(self):
        raise NotImplementedError("EntityMetadata type")


@dataclass
class AttachEntity(Packet):
    leashed_entity_id: Int  # should be me
    holding_entity_id: Int


@dataclass
class EntityVelocity(Packet):
    entity_id: VarInt
    v_x: EntityVelocityType
    v_y: EntityVelocityType
    v_Z: EntityVelocityType


@dataclass
class EntityEquipment(Packet):
    entity_id: VarInt
    slot: VarInt
    item: bytes  # Type: Slot
    
    def to_bytes(self):
        raise NotImplementedError("Slots datatype (requires NBT)")


@dataclass
class SetExperience(Packet):
    xp_bar: Float
    level: VarInt
    total_xp: VarInt


@dataclass
class UpdateHealth(Packet):
    health: Float
    hunger: VarInt
    saturation: Float


@dataclass
class ScoreboardObjective(Packet):
    objective_name: String
    mode: Byte
    objective_value: Chat = None
    type: VarInt = None
    
    def to_bytes(self):
        data = String.encode(self.objective_name)
        data += struct.pack(">b", self.mode)
        if self.mode in [0, 2]:
            if (self.objective_value is None) or (self.type is None):
                raise RuntimeError("Packet ScoreboardObjective: mode in {0, 2} but either objective_value or type was "
                                   "not passed")
            data += Chat.encode(self.objective_value)
            data += VarInt.encode(self.type)
        return data


@dataclass
class SetPassengers(Packet):
    entity_id: VarInt
    passengers: List[VarInt]
    
    def to_bytes(self):
        return VarInt.encode(self.entity_id) + \
            VarInt.encode(len(self.passengers)) + \
            b"".join([VarInt.encode(x) for x in self.passengers])


@dataclass
class Teams(Packet):
    team: String
    mode: Byte
    display_name: Chat = None
    allow_friendly_fire: bool = None
    can_see_invisible_teammates: bool = None
    nametag_visibility: String = None
    collision_rule: String = None
    color: VarInt = None
    prefix: Chat = None
    suffix: Chat = None
    entities: List[String] = None
    
    def to_bytes(self):
        data = String.encode(self.team)
        data += struct.pack(">b", self.mode)
        if self.mode in [0, 2]:
            data += Chat.encode(self.display_name)
            data += struct.pack(">b", self.can_see_invisible_teammates << 1 | self.allow_friendly_fire)
            data += String.encode(self.nametag_visibility)
            data += String.encode(self.collision_rule)
            data += VarInt.encode(self.color)
            data += String.encode(self.prefix)
            data += String.encode(self.suffix)
            if self.mode == 0:
                data += VarInt.encode(len(self.entities))
                data += b"".join([String.encode(x) for x in self.entities])
        if self.mode == 1:
            pass
        if self.mode in [3, 4]:
            data += VarInt.encode(len(self.entities))
            data += b"".join([String.encode(x) for x in self.entities])
        return data


@dataclass
class UpdateScore(Packet):
    entity_name: String
    action: Byte
    objective_name: String
    value: VarInt = None
    
    def to_bytes(self):
        data = String.encode(self.entity_name)
        data += struct.pack(">b", self.action)
        data += String.encode(self.objective_name)
        if self.action != 1:
            data += VarInt.encode(self.value)
        return data


@dataclass
class SpawnPosition(Packet):
    location: Position


@dataclass
class TimeUpdate(Packet):
    world_age: Long
    time_of_day: Long


@dataclass
class Title(Packet):
    action: VarInt
    title_text: Chat = None
    subtitle_text: Chat = None
    action_bar_text: Chat = None
    fade_in: Int = None
    stay: Int = None
    fade_out: Int = None
    
    def to_bytes(self):
        # Todo: Action could probably be an Enum, and reduce to a single text field
        data = VarInt.encode(self.action)
        if self.action == 0:
            data += Chat.encode(self.title_text)
        if self.action == 1:
            data += Chat.encode(self.subtitle_text)
        if self.action == 2:
            data += Chat.encode(self.action_bar_text)
        if self.action == 3:
            data += struct.pack(">iii", self.fade_in, self.stay, self.fade_out)
        # if self.action in [4, 5]:
        #     pass
        return data


@dataclass
class EntitySoundEffect(Packet):
    sound_id: VarInt
    sound_category: VarInt
    entity_id: VarInt
    volume: Float = 1.0
    pitch: Float = 1.0


@dataclass
class SoundEffect(Packet):
    sound_id: VarInt
    sound_category: VarInt
    pos_x: float
    pos_y: float
    pos_z: float
    volume: Float = 1.0
    pitch: Float = 1.0
    
    def to_bytes(self):
        return VarInt.encode(self.sound_id) + \
            VarInt.encode(self.sound_category) + \
            struct.pack(">iiiff",
                        int(self.pos_x*8),
                        int(self.pos_y*8),
                        int(self.pos_z*8),
                        self.volume,
                        self.pitch)


@dataclass
class StopSound(Packet):
    from_source: VarInt = None
    from_sound: Identifier = None
    
    def to_bytes(self):
        flags = 0
        if self.from_source is not None:
            flags |= 0x01
        if self.from_sound is not None:
            flags |= 0x02
        return flags.to_bytes(1, "big") + \
            (VarInt.encode(self.from_source) if self.from_source is not None else b"") + \
            (Identifier.encode(self.from_sound) if self.from_sound is not None else b"")


@dataclass
class PlayerListHeaderAndFooter(Packet):
    header: Chat = "{\"translate\": \"\"}"
    footer: Chat = "{\"translate\": \"\"}"


@dataclass
class NbtQueryResponse(Packet):
    transaction_id: VarInt
    nbt: bytes
    
    def to_bytes(self):
        raise NotImplementedError("NBT datatype")


@dataclass
class CollectItem(Packet):
    collected_entity_id: VarInt
    collector_entity_id: VarInt
    stack_count: VarInt


@dataclass
class EntityTeleport(Packet):
    entity_id: VarInt
    x: Double
    y: Double
    z: Double
    new_yaw: Angle
    new_pitch: Angle
    on_ground: Boolean


@dataclass
class Advancements(Packet):
    def __post_init__(self):
        raise NotImplementedError("this packet is a mess")


@dataclass
class EntityProperties(Packet):
    """
    Example properties:
    {
        "key": String,
        "value": Double,
        "modifiers": [
            {
                "uuid": UUID,
                "amount": Double,
                "operation": Byte
            }
        ]
    }
    """
    entity_id: VarInt
    properties: List[Dict]
    
    def to_bytes(self):
        data = VarInt.encode(self.entity_id)
        data += struct.pack(">i", len(self.properties))
        for item in self.properties:
            data += String.encode(item['key'])
            data += struct.pack(">d", item['value'])
            data += VarInt.encode(len(item['modifiers']))
            for mod in item['modifiers']:
                data += UUID.encode(mod['uuid'])
                data += struct.pack(">db", mod['amount'], mod['operation'])
        return data


@dataclass
class EntityEffect(Packet):
    entity_id: VarInt
    effect_id: Byte
    amplifier: Byte
    duration: VarInt
    is_ambient: bool
    show_particles: bool
    show_icon: bool
    
    def to_bytes(self):
        return VarInt.encode(self.entity_id) + \
            struct.pack(">bb",
                        self.effect_id,
                        self.amplifier) + \
            VarInt.encode(self.duration) + \
            struct.pack(">b", self.show_icon << 2 | self.show_particles << 1 | self.is_ambient)


@dataclass
class DeclareRecipes(Packet):
    """
    recipes: {
        "type": Identifier,
        "recipe_id": String,
        "data": {  # Type: crafting_shapeless
            "group": String,
            (count)
            "ingredients": [Ingredient],
            "result": Slot
        }
        "data": {  # Type: crafting_shaped
            "width": VarInt,
            "height": VarInt,
            "group": String,
            (count)  # <-- Not present on wiki.vg, though it must be implied...?
            "ingredients": [Ingredient],
            "result": Slot
        }
        "data": {  # Type: [smelting, blasting, smoking, campfire_cooking]
            "group": String,
            "ingredient": Ingredient,
            "result": Slot,
            "experience": Float,
            "cooking_time": VarInt
        }
        "data": {  # Type: stonecutting
            "group": String,
            "ingredient": Ingredient,
            "result": Slot
        }
    }
    
    `data` may be completely missing for any other `type`.
    
    Ingredient: [Slot] (implicit length-prefixed)
    """
    recipes: List[Dict]
    
    # Ingredients fields appear to be an array of `Ingredient`s, which are themselves arrays of `Slot`s...
    # Is this accidental duplication?, or should this be flattened into a single array of `Slot`s?
    
    def to_bytes(self):
        raise NotImplementedError("Slot datatype")
        data = VarInt.encode(len(self.recipes))
        for recipe in self.recipes:
            data += Identifier.encode(recipe["type"])
            data += String.encode(recipe["recipe_id"])
            if recipe["type"] == "crafting_shapeless":
                data += self._data_shapeless(recipe["data"])
            if recipe["type"] == "crafting_shaped":
                data += self._data_shaped(recipe["data"])
            if recipe["type"] in ["smelting", "blasting", "smoking", "campfire_cooking"]:
                data += self._data_furnace(recipe["data"])
            if recipe["type"] == "stonecutting":
                data += self._data_stonecutter(recipe["data"])
        return data
    
    @staticmethod
    def _data_shapeless(data):
        ret = b""
        ret += String.encode(data["group"])
        ret += VarInt.encode(len(data["ingredients"]))
        # for item in data["ingredients"]:
        #     ret += Slot.encode()
        # ret += Slot.encode(data["result"])
        return ret
    
    @staticmethod
    def _data_shaped(data):
        ret = VarInt.encode(data["width"])
        ret += VarInt.encode(data["height"])
        ret += String.encode(data["group"])
        # ret += b"".join([Slot.encode(x) for x in data["ingredients"]])
        # ret += Slot.encode(data["result"])
        return ret
    
    @staticmethod
    def _data_furnace(data):
        ret = String.encode(data["group"])
        # ret += b"".join([Slot.encode(x) for x in data["ingredients"]])
        # ret += Slot.encode(data["result"])
        ret += struct.pack(">f", data["experience"])
        ret += VarInt.encode(data["cooking_time"])
        return ret
    
    @staticmethod
    def _data_stonecutter(data):
        ret = String.encode(data["group"])
        # ret += b"".join([Slot.encode(x) for x in data["ingredients"]])
        # ret += Slot.encode(data["result"])
        return ret


@dataclass
class Tags(Packet):
    block_tags: List[Dict]
    item_tags: List[Dict]
    fluid_tags: List[Dict]
    entity_tags: List[Dict]
    
    def to_bytes(self):
        data = b""
        for tags in [self.block_tags, self.item_tags, self.fluid_tags, self.entity_tags]:
            data += VarInt.encode(len(tags))
            for tag in tags:
                data += Identifier.encode(tag["name"])
                data += VarInt.encode(len(tag["entries"]))
                data += b"".join([VarInt.encode(x) for x in tag["entries"]])
        return data

# ----------------------
# Play Mode Packets: Serverbound
# ----------------------


@dataclass
class TeleportConfirm(Packet):
    teleport_id: VarInt


@dataclass
class QueryBlockNbt(Packet):
    transaction_id: VarInt
    location: Position


# @dataclass
# class SetDifficulty(Packet):
#     new_difficulty: Byte


@dataclass
class ChatMessageServerbound(Packet):
    message: String


@dataclass
class ClientStatus(Packet):
    """0: Request Respawn, 1: Request Statistics"""
    action_id: VarInt


@dataclass
class ClientSettings(Packet):
    """main_hand: 0=Left, 1=Right"""
    locale: str
    view_distance: int
    chat_mode: int
    chat_colors: bool
    main_hand: int
    cape: bool
    jacket: bool
    left_sleeve: bool
    right_sleeve: bool
    left_pants: bool
    right_pants: bool
    hat: bool
    
    @classmethod
    def from_bytes(cls, buffer: bytes):
        locale, buffer = String.decode(buffer)
        view_dist, = struct.unpack(">b", buffer[:1])
        chat_mode, buffer = VarInt.decode(buffer[1:])
        chat_colors = bool(buffer[:1])
        skin_parts, = struct.unpack(">B", buffer[1:2])
        main_hand, _ = VarInt.decode(buffer[2:])

        # Bit 0(0x01): Cape enabled
        # Bit 1(0x02): Jacket enabled
        # Bit 2(0x04): Left Sleeve enabled
        # Bit 3(0x08): Right Sleeve enabled
        # Bit 4(0x10): Left Pants Leg enabled
        # Bit 5(0x20): Right Pants Leg enabled
        # Bit 6(0x40): Hat enabled
        
        cape = skin_parts & 0x01
        jacket = skin_parts & 0x02
        left_sleeve = skin_parts & 0x04
        right_sleeve = skin_parts & 0x08
        left_pants = skin_parts & 0x10
        right_pants = skin_parts & 0x20
        hat = skin_parts & 0x40
        
        return cls(locale=locale,
                   view_distance=view_dist,
                   chat_mode=chat_mode,
                   chat_colors=chat_colors,
                   main_hand=main_hand,
                   cape=bool(cape),
                   jacket=bool(jacket),
                   left_sleeve=bool(left_sleeve),
                   right_sleeve=bool(right_sleeve),
                   left_pants=bool(left_pants),
                   right_pants=bool(right_pants),
                   hat=bool(hat))


@dataclass
class TabCompleteServerbound(Packet):
    transaction_id: VarInt
    text: String


@dataclass
class WindowConfirmationServerbound(Packet):
    window_id: Byte
    action_number: Short
    accepted: Boolean


@dataclass
class ClickWindowButton(Packet):
    """
    window_id: that sent by Open Window
    ETable enchantments: 0-1-2 for enchantments
    lectern: 1: Previous page, 2: Next page, 3: Take book, 100+page=open <page>
    Stonecutter: recipe button number = 4*row + col
    loom: 4*row + col
    """
    window_id: Byte
    button_id: Byte


@dataclass
class ClickWindow(Packet):
    window_id: UnsignedByte
    slot: Short
    button: Byte
    action_number: Short
    mode: VarInt
    clicked_item: "Slot"


@dataclass
class CloseWindowServerbound(Packet):
    window_id: UnsignedByte


@dataclass
class PluginMessageServerbound(Packet):
    channel: str
    data: bytes

    @classmethod
    def from_bytes(cls, buffer: bytes):
        return cls(*Identifier.decode(buffer))


@dataclass
class EditBook(Packet):
    new_book: "Slot"
    is_signing: Boolean
    hand: VarInt


@dataclass
class EntityNbtRequest(Packet):
    transaction_id: VarInt
    entity_id: VarInt


@dataclass
class InteractEntity(Packet):
    entity_id: VarInt
    type: VarInt
    target_x: Float = None
    target_y: Float = None
    target_z: Float = None
    hand: VarInt = None
    
    @classmethod
    def from_bytes(cls, buffer: bytes):
        data = {}
        data["entity_id"], buffer = VarInt.decode(buffer)
        data["type"], buffer = VarInt.decode(buffer)
        if data["type"] == 2:
            data["target_x"], data["target_y"], data["target_z"] = struct.unpack(">fff", buffer[:12])
            data["hand"], _ = VarInt.decode(buffer[12:])
        return cls(**data)


class KeepAliveServerbound(Packet):
    def __init__(self, buffer: bytes):
        self.payload, = struct.unpack(">q", buffer)


# @dataclass
# class LockDifficulty(Packet):
#     locked: Boolean
        

@dataclass
class PlayerPosition(Packet):
    """
    Updates the player's XYZ position on the server.

    Checking for moving too fast is achieved like this:

     - Each server tick, the player's current position is stored
     - When a player moves, the changes in x, y, and z coordinates are compared with the positions from the previous
     tick (Δx, Δy, Δz)
     - Total movement distance squared is computed as Δx² + Δy² + Δz²
     - The expected movement distance squared is computed as velocityX² + veloctyY² + velocityZ²
     - If the total movement distance squared value minus the expected movement distance squared value is more than
     100 (300 if the player is using an elytra), they are moving too fast.

    If the player is moving too fast, it will be logged that "<player> moved too quickly! " followed by the change
    in x, y, and z, and the player will be teleported back to their current (before this packet) serverside position.

    Also, if the absolute value of X or the absolute value of Z is a value greater than 3.2×107, or X, Y,
    or Z are not finite (either positive infinity, negative infinity, or NaN), the client will be kicked for “Invalid move player packet received”.
    """
    x: Double
    y: Double
    z: Double
    on_ground: Boolean


@dataclass
class PlayerPositionAndRotationServerbound(Packet):
    x: Double
    y: Double
    z: Double
    yaw: Float
    pitch: Float
    on_ground: Boolean


@dataclass
class PlayerRotation(Packet):
    yaw: Float
    pitch: Float
    on_ground: Boolean


@dataclass
class PlayerMovement(Packet):
    on_ground: Boolean


@dataclass
class VehicleMoveServerbound(Packet):
    x: Double
    y: Double
    z: Double
    yaw: Float
    pitch: Float


@dataclass
class SteerBoat(Packet):
    left_paddle_turning: Boolean
    right_paddle_turning: Boolean


@dataclass
class PickItem(Packet):
    slot_to_use: VarInt


@dataclass
class CraftRecipeRequest(Packet):
    window_id: Byte
    recipe: Identifier
    make_all: Boolean


@dataclass
class PlayerAbilitiesServerbound(Packet):
    is_flying: bool
    
    @classmethod
    def from_bytes(cls, buffer: bytes):
        return cls(bool(buffer[0] & 0x02))


@dataclass
class PlayerDigging(Packet):
    """
    Status:
    0 	Started digging
    1 	Cancelled digging 	Sent when the player lets go of the Mine Block key (default: left click)
    2 	Finished digging 	Sent when the client thinks it is finished
    3 	Drop item stack 	Triggered by using the Drop Item key (default: Q) with the modifier to drop the entire selected stack (default: depends on OS). Location is always set to 0/0/0, Face is always set to -Y.
    4 	Drop item 	Triggered by using the Drop Item key (default: Q). Location is always set to 0/0/0, Face is always set to -Y.
    5 	Shoot arrow / finish eating 	Indicates that the currently held item should have its state updated such as eating food, pulling back bows, using buckets, etc. Location is always set to 0/0/0, Face is always set to -Y.
    6 	Swap item in hand 	Used to swap or assign an item to the second hand. Location is always set to 0/0/0, Face is always set to -Y.
    
    block_face:
    0 	-Y 	Bottom
    1 	+Y 	Top
    2 	-Z 	North
    3 	+Z 	South
    4 	-X 	West
    5 	+X 	East
    
    """
    status: VarInt
    location: Position
    block_face: Byte
    

@dataclass
class EntityAction(Packet):
    """
    Sent by the client to indicate that it has performed certain actions: sneaking (crouching), sprinting,
    exiting a bed, jumping with a horse, and opening a horse's inventory while riding it.

    action_id:
    0 	Start sneaking
    1 	Stop sneaking
    2 	Leave bed
    3 	Start sprinting
    4 	Stop sprinting
    5 	Start jump with horse
    6 	Stop jump with horse
    7 	Open horse inventory
    8 	Start flying with elytra
    
    Leave bed is only sent when the “Leave Bed” button is clicked on the sleep GUI, not when waking up due today time.

    Open horse inventory is only sent when pressing the inventory key (default: E) while on a horse — all other
    methods of opening a horse's inventory (involving right-clicking or shift-right-clicking it) do not use this packet.
    """
    entity_id: VarInt
    action_id: VarInt
    jump_boost: VarInt
    

@dataclass
class SteerVehicle(Packet):
    """
    Sideways 	Float 	Positive to the left of the player
    Forward 	Float 	Positive forward
    Flags 	Unsigned Byte 	Bit mask. 0x1: jump, 0x2: unmount
    
    Also known as 'Input' packet.
    """
    sideways: Float
    forward: Float
    flags: UnsignedByte


@dataclass
class RecipeBookData(Packet):
    def __post_init__(self):
        raise NotImplementedError("too complex for me right now")


@dataclass
class NameItem(Packet):
    """
    Sent as a player is renaming an item in an anvil (each keypress in the anvil UI sends a new Name Item packet).
    If the new name is empty, then the item loses its custom name (this is different from setting the custom name to
    the normal name of the item). The item name may be no longer than 35 characters long, and if it is longer than
    that, then the rename is silently ignored.
    """
    new_name: String


@dataclass
class ResourcePackStatus(Packet):
    result: VarInt


@dataclass
class AdvancementTab(Packet):
    action: VarInt
    tab_id: Identifier = None
    
    @classmethod
    def from_bytes(cls, buffer: bytes):
        action, buffer = VarInt.decode(buffer)
        if action == 0:
            tab_id, buffer = Identifier.decode(buffer)
        else:
            tab_id = None
        return cls(action, tab_id)


@dataclass
class SelectTrade(Packet):
    slot: VarInt


@dataclass
class SetBeaconEffect(Packet):
    primary_effect: VarInt
    secondary_effect: VarInt


@dataclass
class HeldItemChangeServerbound(Packet):
    slot: Short


@dataclass
class UpdateCommandBlock(Packet):
    """
    Mode 	VarInt enum 	One of SEQUENCE (0), AUTO (1), or REDSTONE (2)
    Flags 	Byte
    0x01: Track Output (if false, the output of the previous command will not be stored within the command block);
    0x02: Is conditional;
    0x04: Automatic
    """
    location: Position
    command: String
    mode: VarInt
    flags: Byte


@dataclass
class UpdateCommandBlockMinecart(Packet):
    entity_id: VarInt
    command: String
    track_output: Boolean


@dataclass
class CreativeInventoryAction(Packet):
    """
    While the user is in the standard inventory (i.e., not a crafting bench) in Creative mode, the player will send
    this packet.

    Clicking in the creative inventory menu is quite different from non-creative inventory management. Picking up an
    item with the mouse actually deletes the item from the server, and placing an item into a slot or dropping it out
    of the inventory actually tells the server to create the item from scratch. (This can be verified by clicking an
    item that you don't mind deleting, then severing the connection to the server; the item will be nowhere to be found
    when you log back in.) As a result of this implementation strategy, the "Destroy Item" slot is just a client-side
    implementation detail that means "I don't intend to recreate this item.". Additionally, the long listings of items
    (by category, etc.) are a client-side interface for choosing which item to create. Picking up an item from such
    listings sends no packets to the server; only when you put it somewhere does it tell the server to create the item
    in that location.

    This action can be described as "set inventory slot". Picking up an item sets the slot to item ID -1. Placing an
    item into an inventory slot sets the slot to the specified item. Dropping an item (by clicking outside the window)
    effectively sets slot -1 to the specified item, which causes the server to spawn the item entity, etc.. All other
    inventory slots are numbered the same as the non-creative inventory (including slots for the 2x2 crafting menu, even
    though they aren't visible in the vanilla client).
    """
    slot: Short
    clicked_item: "Slot"


@dataclass
class UpdateJigsawBlock(Packet):
    location: Position
    attachment_type: Identifier
    target_pool: Identifier
    final_state: String


@dataclass
class UpdateStructureBlock(Packet):
    """
    Location 	Position 	Block entity location
    Action 	VarInt enum 	An additional action to perform beyond simply saving the given data; see below
    Mode 	VarInt enum 	One of SAVE (0), LOAD (1), CORNER (2), DATA (3).
    Name 	String
    Offset X 	Byte 	Between -32 and 32
    Offset Y 	Byte 	Between -32 and 32
    Offset Z 	Byte 	Between -32 and 32
    Size X 	Byte 	Between 0 and 32
    Size Y 	Byte 	Between 0 and 32
    Size Z 	Byte 	Between 0 and 32
    Mirror 	VarInt enum 	One of NONE (0), LEFT_RIGHT (1), FRONT_BACK (2).
    Rotation 	VarInt enum 	One of NONE (0), CLOCKWISE_90 (1), CLOCKWISE_180 (2), COUNTERCLOCKWISE_90 (3).
    Metadata 	String
    Integrity 	Float 	Between 0 and 1
    Seed 	VarLong
    Flags 	Byte 	0x01: Ignore entities; 0x02: Show air; 0x04: Show bounding box
    
    Possible actions:

    0 - Update data
    1 - Save the structure
    2 - Load the structure
    3 - Detect size

    The Notchian client uses update data to indicate no special action should be taken (i.e. the done button).
    """
    location: Position
    action: VarInt
    mode: VarInt
    name: String
    offset_x: Byte
    offset_y: Byte
    offset_z: Byte
    size_x: Byte
    size_y: Byte
    size_z: Byte
    mirror: VarInt
    rotation: VarInt
    metadata: String
    integrity: Float
    seed: VarLong
    flags: Byte


@dataclass
class UpdateSign(Packet):
    location: Position
    line_1: String
    line_2: String
    line_3: String
    line_4: String


@dataclass
class AnimationServerbound(Packet):
    hand: VarInt


@dataclass
class Spectate(Packet):
    target_player: UUID


@dataclass
class PlayerBlockPlacement(Packet):
    """
    Hand 	VarInt Enum 	The hand from which the block is placed; 0: main hand, 1: off hand
    Location 	Position 	Block position
    Face 	VarInt Enum 	The face on which the block is placed (as documented at Player Digging)
    Cursor Position X 	Float 	The position of the crosshair on the block, from 0 to 1 increasing from west to east
    Cursor Position Y 	Float 	The position of the crosshair on the block, from 0 to 1 increasing from bottom to top
    Cursor Position Z 	Float 	The position of the crosshair on the block, from 0 to 1 increasing from north to south
    Inside block 	Boolean 	True when the player's head is inside of a block.
    
    Upon placing a block, this packet is sent once.

    The Cursor Position X/Y/Z fields (also known as in-block coordinates) are calculated using raytracing. The unit
    corresponds to sixteen pixels in the default resource pack. For example, let's say a slab is being placed against
    the south face of a full block. The Cursor Position X will be higher if the player was pointing near the right
    (east) edge of the face, lower if pointing near the left. The Cursor Position Y will be used to determine whether
    it will appear as a bottom slab (values 0.0–0.5) or as a top slab (values 0.5-1.0). The Cursor Position Z should be
    1.0 since the player was looking at the southernmost part of the block.

    Inside block is true when a player's head (specifically eyes) are inside of a block's collision. In 1.13 and later
    versions, collision is rather complicated and individual blocks can have multiple collision boxes. For instance, a
    ring of vines has a non-colliding hole in the middle. This value is only true when the player is directly in the
    box. In practice, though, this value is only used by scaffolding to place in front of the player when sneaking
    inside of it (other blocks will place behind when you intersect with them -- try with glass for instance).
    """
    hand: VarInt
    location: Position
    face: VarInt
    cursor_pos_x: Float
    cursor_pos_y: Float
    cursor_pos_z: Float
    inside_block: Boolean


@dataclass
class UseItem(Packet):
    """
    Hand 	VarInt Enum 	Hand used for the animation. 0: main hand, 1: off hand.
    """
    hand: VarInt

# Next Steps: Take a second pass through all packets:
#  - Add documentation for more packets (copy/paste from wiki.vg page)
#  - Split fields-kinds of things into specific variables
#  - Enum types should list in the __doc__ their types
#  - Implement more packets where possible
