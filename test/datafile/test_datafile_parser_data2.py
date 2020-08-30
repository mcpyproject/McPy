from enum import Enum

from classes.datafile.Parser import Parser


@Parser.Parser(
    directory='test/data/data2/{version}/anotherdirectory/',
    file='registries.json',
    namespace_id='not_a_random_field',
    array_path='minecraft:menu/entries',
    struct={
        "protocol_id": {
            "_action": {
                "type": "save",
                "id": "protocol_id"
            }
        }
    },
    key_pattern='minecraft:{key}'
)
class MenuModel(Enum):

    def __init__(self, not_a_random_field):
        self.not_a_random_field = not_a_random_field

    GENERIC_9_1 = ('generic_9x1')
    GENERIC_9_2 = ('generic_9x2')
    GENERIC_9_3 = ('generic_9x3')
    GENERIC_9_4 = ('generic_9x4')
    GENERIC_9_5 = ('generic_9x5')
    GENERIC_9_6 = ('generic_9x6')
    GENERIC_3_3 = ('generic_3x3')
    ANVIL = ('anvil')
    BEACON = ('beacon')
    BLAST_FURNACE = ('blast_furnace')
    BREWING_STAND = ('brewing_stand')
    CRAFTING = ('crafting')
    ENCHANTMENT = ('enchantment')
    FURNACE = ('furnace')
    GRINDSTONE = ('grindstone')
    HOPPER = ('hopper')
    LECTERN = ('lectern')
    LOOM = ('loom')
    MERCHANT = ('merchant')
    SHULKER_BOX = ('shulker_box')
    SMOKER = ('smoker')
    CARTOGRAPHY_TABLE = ('cartography_table')
    STONECUTTER = ('stonecutter')


Parser.parse_enums()


class TestParser:

    def test_protocol(self):
        assert MenuModel.GENERIC_9_1.protocol['V1']['protocol_id'] == 0
        assert MenuModel.GENERIC_9_2.protocol['V1']['protocol_id'] == 1
        assert MenuModel.GENERIC_9_3.protocol['V1']['protocol_id'] == 2
        assert MenuModel.GENERIC_9_4.protocol['V1']['protocol_id'] == 3
        assert MenuModel.GENERIC_9_5.protocol['V1']['protocol_id'] == 4
        assert MenuModel.GENERIC_9_6.protocol['V1']['protocol_id'] == 5
        assert MenuModel.GENERIC_3_3.protocol['V1']['protocol_id'] == 6
        assert MenuModel.ANVIL.protocol['V1']['protocol_id'] == 7
        assert MenuModel.BEACON.protocol['V1']['protocol_id'] == 8
        assert MenuModel.BLAST_FURNACE.protocol['V1']['protocol_id'] == 9
        assert MenuModel.BREWING_STAND.protocol['V1']['protocol_id'] == 10
        assert MenuModel.CRAFTING.protocol['V1']['protocol_id'] == 11
        assert MenuModel.ENCHANTMENT.protocol['V1']['protocol_id'] == 12
        assert MenuModel.FURNACE.protocol['V1']['protocol_id'] == 13
        assert MenuModel.GRINDSTONE.protocol['V1']['protocol_id'] == 14
        assert MenuModel.HOPPER.protocol['V1']['protocol_id'] == 15
        assert MenuModel.LECTERN.protocol['V1']['protocol_id'] == 16
        assert MenuModel.LOOM.protocol['V1']['protocol_id'] == 17
        assert MenuModel.MERCHANT.protocol['V1']['protocol_id'] == 18
        assert MenuModel.SHULKER_BOX.protocol['V1']['protocol_id'] == 19
        assert MenuModel.SMOKER.protocol['V1']['protocol_id'] == 20
        assert MenuModel.CARTOGRAPHY_TABLE.protocol['V1']['protocol_id'] == 21
        assert MenuModel.STONECUTTER.protocol['V1']['protocol_id'] == 22
