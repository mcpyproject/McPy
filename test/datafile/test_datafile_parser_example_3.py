from enum import Enum

from classes.datafile.Parser import Parser


@Parser.Parser(
    directory='test/data/data1/{version}/',
    file='example3.json',
    namespace_id='another_namespace_id',
    array_path='ids',
    struct={
        "name": {
            "_action": {
                "type": "save",
                "id": "name"
            }
        },
        "description": {
            "_action": {
                "type": "save",
                "id": "description"
            }
        }
    }
)
class ExampleModel(Enum):

    def __init__(self, another_namespace_id):
        self.another_namespace_id = another_namespace_id

    ID_1 = ('id1')
    ID_2 = ('id2')
    ID_3 = ('id3')
    ID_4 = ('id4')
    ID_5 = ('id5')
    ID_6 = ('id6')


Parser.parse_enums()


class TestParser:

    def test_init_called(self):
        assert ExampleModel.ID_1.another_namespace_id == 'id1'
        assert ExampleModel.ID_2.another_namespace_id == 'id2'
        assert ExampleModel.ID_3.another_namespace_id == 'id3'
        assert ExampleModel.ID_4.another_namespace_id == 'id4'
        assert ExampleModel.ID_5.another_namespace_id == 'id5'
        assert ExampleModel.ID_6.another_namespace_id == 'id6'

    def test_protocol(self):
        assert ExampleModel.ID_1.protocol['1']['name'] == "Name 1"
        assert ExampleModel.ID_1.protocol['1']['description'] == "Description 1"
        assert ExampleModel.ID_2.protocol['1']['name'] == "Name 2"
        assert ExampleModel.ID_2.protocol['1']['description'] == "Description 2"
        assert ExampleModel.ID_3.protocol['1']['name'] == "Name 3"
        assert ExampleModel.ID_3.protocol['1']['description'] == "Description 3"
        assert ExampleModel.ID_4.protocol['1']['name'] == "Name 4"
        assert ExampleModel.ID_4.protocol['1']['description'] == "Description 4"
        assert ExampleModel.ID_5.protocol['1']['name'] == "Name 5"
        assert ExampleModel.ID_5.protocol['1']['description'] == "Description 5"
        assert ExampleModel.ID_6.protocol['1']['name'] == "Name 6"
        assert ExampleModel.ID_6.protocol['1']['description'] == "Description 6"

    def test_protocol_2(self):
        assert ExampleModel.ID_1.protocol['2']['name'] == "Name 1"
        assert ExampleModel.ID_1.protocol['2']['description'] == "Description 1"
        assert ExampleModel.ID_2.protocol['2']['name'] == "Name 2"
        assert ExampleModel.ID_2.protocol['2']['description'] == "Description 2"
        assert ExampleModel.ID_3.protocol['2']['name'] == "Name 3"
        assert ExampleModel.ID_3.protocol['2']['description'] == "Description 3"
        assert ExampleModel.ID_4.protocol['2']['name'] == "Name 4"
        assert ExampleModel.ID_4.protocol['2']['description'] == "Description 4"
        assert ExampleModel.ID_5.protocol['2']['name'] == "Name 6"
        assert ExampleModel.ID_5.protocol['2']['description'] == "Description 6"
        assert ExampleModel.ID_6.protocol['2']['name'] == "Name 5"
        assert ExampleModel.ID_6.protocol['2']['description'] == "Description 5"

    def test_protocol_3(self):
        assert ExampleModel.ID_1.protocol['3']['name'] == "Name 1"
        assert ExampleModel.ID_1.protocol['3']['description'] == "Description 1"
        assert ExampleModel.ID_2.protocol['3']['name'] == "Name 2"
        assert ExampleModel.ID_2.protocol['3']['description'] == "Description 2"
        assert ExampleModel.ID_3.protocol['3']['name'] == "Name 3"
        assert ExampleModel.ID_3.protocol['3']['description'] == "Description 3"
        assert ExampleModel.ID_4.protocol['3']['name'] == "Name 4"
        assert ExampleModel.ID_4.protocol['3']['description'] == "Description 4"
        assert ExampleModel.ID_5.protocol['3']['name'] == "Name 5"
        assert ExampleModel.ID_5.protocol['3']['description'] == "Description 5"
        assert ExampleModel.ID_6.protocol['3']['name'] == "Name 6"
        assert ExampleModel.ID_6.protocol['3']['description'] == "Description 6"
