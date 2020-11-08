from classes.blocks.Materials import Material


class TestMaterial:

    def test_elem_flat(self):
        assert Material._elem_flat(['a', 'b', 'd', 'c']) == ['a', 'b', 'd', 'c']
        assert Material._elem_flat({'a': 1, 'b': 2, 'd': 3, 'c': 4}) == ['a', 'b', 'd', 'c']
        assert Material._elem_flat({
            'a': {
                'b': 'c'
            },
            'b': {
                'c': 'd'
            },
            'd': {
                'e': 'f'
            },
            'c': {
                'd': 'e'
            }}) == ['a', 'b', 'd', 'c']

    def test_properties(self):
        assert Material.NOTE_BLOCK.protocol['578']['flat_properties'] == ['instrument', 'note', 'powered']
        assert Material.NOTE_BLOCK.protocol['578']['properties'] == {
            "instrument": [
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
                "pling",
            ],
            "note": ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"],
            "powered": ["true", "false"]
        }

    def test_flat_properties_state(self):
        assert Material._flat_properties_state(['a', 'b', 'd', 'c'], {
            'a': '1',
            'b': '2',
            'd': '4',
            'c': '3',
        }) == ['1', '2', '4', '3']

    def test_flat_properties_state_unordered(self):
        assert Material._flat_properties_state(['a', 'b', 'd', 'c'], {
            'c': '3',
            'a': '1',
            'd': '4',
            'b': '2',
        }) == ['1', '2', '4', '3']

    def test_flat_properties_state_non_exist(self):
        assert Material._flat_properties_state(['a', 'b', 'd', 'c'], {
            'a': '1',
            'b': '2',
            'c': '3',
        }) == ['1', '2', None, '3']
        assert Material._flat_properties_state(['a', 'b', 'd', 'c'], {
            'a': '1',
            'b': '2',
            'c': '3',
        }, default='0') == ['1', '2', '0', '3']

    def test_flat_properties_state_non_exist_unordered(self):
        assert Material._flat_properties_state(['a', 'b', 'd', 'c'], {
            'c': '3',
            'b': '2',
            'a': '1',
        }) == ['1', '2', None, '3']
        assert Material._flat_properties_state(['a', 'b', 'd', 'c'], {
            'b': '2',
            'a': '1',
            'c': '3',
        }, default='0') == ['1', '2', '0', '3']

    def test_default(self):
        assert Material.AIR.protocol['578']['default'] == 0
        assert Material.NOTE_BLOCK.protocol['578']['default'] == 249

    def test_save_flat_state(self):
        save_struct = {}
        Material._save_flat_state(['1', '1', '1', '1'], 43, save_struct)
        assert save_struct == {
            '1': {
                '1': {
                    '1': {
                        '1': 43,
                    },
                },
            },
        }
        Material._save_flat_state(['1', '1', '1', '2'], 45, save_struct)
        assert save_struct == {
            '1': {
                '1': {
                    '1': {
                        '1': 43,
                        '2': 45,
                    },
                },
            },
        }
        a = Material._save_flat_state(['2', '4', '42', 'e'], 547, save_struct)
        assert save_struct == {
            '1': {
                '1': {
                    '1': {
                        '1': 43,
                        '2': 45,
                    },
                },
            },
            '2': {
                '4': {
                    '42': {
                        'e': 547,
                    },
                },
            },
        }

    def test_state(self):
        assert Material.AIR.protocol['578']['ids'] == {0: []}
        assert Material.AIR.protocol['578']['states'] == 0

        assert Material.GRASS_BLOCK.protocol['578']['ids'] == {
            8: ['true'],
            9: ['false']
        }
        assert Material.GRASS_BLOCK.protocol['578']['states'] == {
            'true': 8,
            'false': 9,
        }

    def test_post_load_blocks(self):
        Material.post_load_blocks()
        assert Material.protocol['578'][0] == Material.AIR
        assert Material.protocol['578'][3571] == Material.OAK_DOOR
        assert Material.protocol['578'][3577] == Material.OAK_DOOR
        assert Material.protocol['578'][4071] == Material.REPEATER

    def test_get_material_from_protocol_id(self):
        Material.post_load_blocks()
        assert Material.get_material_from_protocol_id(0, '578') == Material.AIR
        assert Material.get_material_from_protocol_id(3571, '578') == Material.OAK_DOOR
        assert Material.get_material_from_protocol_id(3577, '578') == Material.OAK_DOOR
        assert Material.get_material_from_protocol_id(4071, '578') == Material.REPEATER

    def test_get_material_state_from_protocol_id(self):
        Material.post_load_blocks()
        assert Material.AIR.get_material_state_from_protocol_id(0, '578') == []
        assert Material.OAK_DOOR.get_material_state_from_protocol_id(3571, '578') == ['north', 'upper', 'left', 'true', 'true']
        assert Material.OAK_DOOR.get_material_state_from_protocol_id(3577, '578') == ['north', 'upper', 'right', 'false', 'true']
        assert Material.REPEATER.get_material_state_from_protocol_id(4071, '578') == ['4', 'south', 'false', 'true']

    def test_get_default(self):
        Material.post_load_blocks()
        assert Material.AIR.get_default_id(578) == 0
        assert Material.BAMBOO.get_default_id(578) == 9116
        assert Material.MOSSY_COBBLESTONE_STAIRS.get_default_id(578) == 9464

        assert Material.AIR.get_default_state(578) == []
        assert Material.BAMBOO.get_default_state(578) == ['0', 'none', '0']
        assert Material.MOSSY_COBBLESTONE_STAIRS.get_default_state(578) == ['north', 'bottom', 'straight', 'false']

    def test_one_block(self):
        # Test properties
        assert Material.NOTE_BLOCK.protocol['578']['flat_properties'] == ['instrument', 'note', 'powered']
        assert Material.NOTE_BLOCK.protocol['578']['properties'] == {
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
        assert Material.NOTE_BLOCK.protocol['578']['default'] == 249

        assert Material.NOTE_BLOCK.protocol['578']['ids'][248] == ['harp', '0', 'true']
        assert Material.NOTE_BLOCK.protocol['578']['ids'][249] == ['harp', '0', 'false']
        assert Material.NOTE_BLOCK.protocol['578']['ids'][250] == ['harp', '1', 'true']
        assert Material.NOTE_BLOCK.protocol['578']['ids'][348] == ['snare', '0', 'true']

        assert Material.NOTE_BLOCK.protocol['578']['states']['harp']['0']['true'] == 248
        assert Material.NOTE_BLOCK.protocol['578']['states']['harp']['0']['false'] == 249
        assert Material.NOTE_BLOCK.protocol['578']['states']['harp']['1']['true'] == 250
        assert Material.NOTE_BLOCK.protocol['578']['states']['snare']['0']['true'] == 348
