import struct
from typing import Tuple

TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12


def read_string(data: bytes, offset: int) -> Tuple[str, int]:
    length = struct.unpack(">H", data[offset:offset+2])[0]
    string = data[offset+2:offset+2+length].decode('utf-8')
    return string, offset + 2 + length


def skip_payload(data: bytes, offset: int, tag_type: int) -> int:
    if tag_type == TAG_END:
        return offset
    elif tag_type == TAG_BYTE:
        return offset + 1
    elif tag_type == TAG_SHORT:
        return offset + 2
    elif tag_type == TAG_INT:
        return offset + 4
    elif tag_type == TAG_LONG:
        return offset + 8
    elif tag_type == TAG_FLOAT:
        return offset + 4
    elif tag_type == TAG_DOUBLE:
        return offset + 8
    elif tag_type == TAG_BYTE_ARRAY:
        length = struct.unpack(">I", data[offset:offset+4])[0]
        return offset + 4 + length
    elif tag_type == TAG_STRING:
        length = struct.unpack(">H", data[offset:offset+2])[0]
        return offset + 2 + length
    elif tag_type == TAG_LIST:
        list_type = data[offset]
        length = struct.unpack(">I", data[offset+1:offset+5])[0]
        offset += 5
        for _ in range(length):
            offset = skip_payload(data, offset, list_type)
        return offset
    elif tag_type == TAG_COMPOUND:
        while True:
            tag = data[offset]
            if tag == TAG_END:
                return offset + 1
            offset += 1
            _, offset = read_string(data, offset)
            offset = skip_payload(data, offset, tag)
    elif tag_type == TAG_INT_ARRAY:
        length = struct.unpack(">I", data[offset:offset+4])[0]
        return offset + 4 + length * 4
    elif tag_type == TAG_LONG_ARRAY:
        length = struct.unpack(">I", data[offset:offset+4])[0]
        return offset + 4 + length * 8
    else:
        raise ValueError(f"Unknown tag type: {tag_type}")


def parse_nbt(data: bytes) -> Tuple[int, int]:
    offset = 0
    tag = data[offset]
    if tag != TAG_COMPOUND:
        raise ValueError("Root tag is not compound")
    offset += 1
    _, offset = read_string(data, offset)  # skip root name
    entity_count = 0
    tile_count = 0
    while True:
        tag = data[offset]
        if tag == TAG_END:
            break
        offset += 1
        name, offset = read_string(data, offset)
        if name == "Entities" and tag == TAG_LIST:
            # 解析列表长度
            list_type = data[offset]  # noqa: F841
            length = struct.unpack(">I", data[offset+1:offset+5])[0]
            entity_count = length
            offset = skip_payload(data, offset, TAG_LIST)
        elif name in ("TileEntities", "block_entities") and tag == TAG_LIST:
            list_type = data[offset]  # noqa: F841
            length = struct.unpack(">I", data[offset+1:offset+5])[0]
            tile_count = length
            offset = skip_payload(data, offset, TAG_LIST)
        else:
            offset = skip_payload(data, offset, tag)
    return entity_count, tile_count