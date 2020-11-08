import pytest

from classes.blocks.Materials import Material
from classes.utils.Parser import Parser
from classes.utils.Utils import Version


@pytest.fixture(scope='session', autouse=True)
def execute_before_any_test(request):
    versions_string = [
        '1.15.2',
    ]
    parser = Parser(versions=versions_string)
    data, versions = parser.parse()
    Material.load_all_data(versions, data)


class TestMaterial:

    def test_protocol(self):
        version = Version.v1_15_2
        data_id = version.data_id
        assert Material.protocol[data_id][0] == Material.AIR
        assert Material.protocol[data_id][42] == Material.WATER
        assert Material.protocol[data_id][4000] == Material.NETHER_PORTAL
        assert Material.protocol[data_id][11330] == Material.BEEHIVE

    def test_get_material_from_protocol_id(self):
        version = Version.v1_15_2
        assert Material.get_material_from_protocol_id(0, version) == Material.AIR
        assert Material.get_material_from_protocol_id(3571, version) == Material.OAK_DOOR
        assert Material.get_material_from_protocol_id(3577, version) == Material.OAK_DOOR
        assert Material.get_material_from_protocol_id(4071, version) == Material.REPEATER

    def test_get_state_from_protocol_id(self):
        version = Version.v1_15_2
        assert Material.AIR.get_state_from_protocol_id(0, version) == ()
        assert Material.OAK_DOOR.get_state_from_protocol_id(3571, version) == ('north', 'upper', 'left', 'true', 'true')
        assert Material.OAK_DOOR.get_state_from_protocol_id(3577, version) == ('north', 'upper', 'right', 'false', 'true')
        assert Material.REPEATER.get_state_from_protocol_id(4071, version) == ('4', 'south', 'false', 'true')

    def test_get_default(self):
        version = Version.v1_15_2
        assert Material.AIR.get_default_id(version) == 0
        assert Material.BAMBOO.get_default_id(version) == 9116
        assert Material.MOSSY_COBBLESTONE_STAIRS.get_default_id(version) == 9464

        assert Material.AIR.get_default_state(version) == ()
        assert Material.BAMBOO.get_default_state(version) == ('0', 'none', '0')
        assert Material.MOSSY_COBBLESTONE_STAIRS.get_default_state(version) == ('north', 'bottom', 'straight', 'false')

    def test_one_block(self):
        version = Version.v1_15_2
        data_id = version.data_id
        # Test properties
        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_list'] == ['instrument', 'note', 'powered']
        assert Material.NOTE_BLOCK.data['versions'][data_id]['block_states'] == {
            'instrument': [
                "harp",
                "basedrum",
                "snare",
                "hat",
                "bass",
                "flute",
                "bell",
                "guitar",
                "chime",
                "xylophone",
                "iron_xylophone",
                "cow_bell",
                "didgeridoo",
                "bit",
                "banjo",
                "pling"
            ],
            'note': [
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "10",
                "11",
                "12",
                "13",
                "14",
                "15",
                "16",
                "17",
                "18",
                "19",
                "20",
                "21",
                "22",
                "23",
                "24"
            ],
            'powered': ['true', 'false']
        }

        # Test default block
        assert Material.NOTE_BLOCK.data['versions'][data_id]['default_id'] == 249

        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_all'][248] == ('harp', '0', 'true')
        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_all'][249] == ('harp', '0', 'false')
        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_all'][250] == ('harp', '1', 'true')
        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_all'][348] == ('snare', '0', 'true')

        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_all_reversed']['harp,0,true'] == 248
        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_all_reversed']['harp,0,false'] == 249
        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_all_reversed']['harp,1,true'] == 250
        assert Material.NOTE_BLOCK.data['versions'][data_id]['states_all_reversed']['snare,0,true'] == 348
