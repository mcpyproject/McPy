from enum import Enum

from classes.datafile.Parser import Parser


class ExampleModel(Enum):

    def __init__(self, namespace_id):
        self.namespace_id = namespace_id

    ID_1 = ('id1')
    ID_2 = ('id2')
    ID_3 = ('id3')
    ID_4 = ('id4')
    ID_5 = ('id5')
    ID_6 = ('id6')


class TestParser:

    def test_retrieve_versions(self):
        path = 'test/data/data1/'
        versions = Parser._retrieve_versions(path)
        assert len(versions) == 3, 'There should be only 3 differents versions'
        assert '1' in versions, 'Version 1 should be in the list'
        assert '2' in versions, 'Version 2 should be in the list'
        assert '3' in versions, 'Version 3 should be in the list'

    def test_retrieve_namespace_id(self):
        namespace_ids = Parser._retrieve_namespace_id(ExampleModel, 'namespace_id')
        assert len(namespace_ids) == 6, 'There should be 6 items'
        assert namespace_ids['id1'] == ExampleModel.ID_1, "namespace_ids['id1'] should be ID_1"
        assert namespace_ids['id2'] == ExampleModel.ID_2, "namespace_ids['id2'] should be ID_2"
        assert namespace_ids['id3'] == ExampleModel.ID_3, "namespace_ids['id3'] should be ID_3"
        assert namespace_ids['id4'] == ExampleModel.ID_4, "namespace_ids['id4'] should be ID_4"
        assert namespace_ids['id5'] == ExampleModel.ID_5, "namespace_ids['id5'] should be ID_5"
        assert namespace_ids['id6'] == ExampleModel.ID_6, "namespace_ids['id6'] should be ID_6"
