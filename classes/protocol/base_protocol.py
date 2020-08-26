from ..blocks.Materials import Material


class BlockMapping:

    def get_protocol_identifier(self, material: Material) -> int:
        raise NotImplementedError()
