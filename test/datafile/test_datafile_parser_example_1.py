from enum import Enum

from classes.datafile.Parser import Parser


@Parser.Parser(
    directory='test/data/data1/{version}/',
    file='example1.json',
    struct={
        "_action": {
            "type": "save",
            "id": "_id"
        }
    }
)
class ExampleModel(Enum):

    def __init__(self, namespace_id):
        self.namespace_id = namespace_id

    ID_1 = ('id1')
    ID_2 = ('id2')
    ID_3 = ('id3')
    ID_4 = ('id4')
    ID_5 = ('id5')
    ID_6 = ('id6')


Parser.parse_enums()


class TestParser:

    def test_init_called(self):
        assert ExampleModel.ID_1.namespace_id == 'id1'
        assert ExampleModel.ID_2.namespace_id == 'id2'
        assert ExampleModel.ID_3.namespace_id == 'id3'
        assert ExampleModel.ID_4.namespace_id == 'id4'
        assert ExampleModel.ID_5.namespace_id == 'id5'
        assert ExampleModel.ID_6.namespace_id == 'id6'

    def test_protocol(self):
        assert ExampleModel.ID_1.protocol['1']['_id'] == 1
        assert ExampleModel.ID_2.protocol['1']['_id'] == 2
        assert ExampleModel.ID_3.protocol['1']['_id'] == 3
        assert ExampleModel.ID_4.protocol['1']['_id'] == 4
        assert ExampleModel.ID_5.protocol['1']['_id'] == 5
        assert ExampleModel.ID_6.protocol['1']['_id'] == 6

    def test_protocol_2(self):
        assert ExampleModel.ID_1.protocol['2']['_id'] == 1
        assert ExampleModel.ID_2.protocol['2']['_id'] == 2
        assert ExampleModel.ID_3.protocol['2']['_id'] == 3
        assert ExampleModel.ID_4.protocol['2']['_id'] == 4
        assert ExampleModel.ID_5.protocol['2']['_id'] == 6
        assert ExampleModel.ID_6.protocol['2']['_id'] == 5

    def test_protocol_3(self):
        assert ExampleModel.ID_1.protocol['3']['_id'] == 'id1'
        assert ExampleModel.ID_2.protocol['3']['_id'] == 'id2'
        assert ExampleModel.ID_3.protocol['3']['_id'] == 'id3'
        assert ExampleModel.ID_4.protocol['3']['_id'] == 'id4'
        assert ExampleModel.ID_5.protocol['3']['_id'] == 'id5'
        assert ExampleModel.ID_6.protocol['3']['_id'] == 'id6'
