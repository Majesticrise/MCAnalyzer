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


def read_string(data, offset):
    length = struct.unpack(">H", data[offset:offset+2])[0]
    string = data[offset+2:offset+2+length].decode('utf-8')
    return string, offset + 2 + length


def skip_payload(data, offset, tag_type):
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
    """返回 (entity_count, block_entity_count)"""
    offset = 0
    tag = data[offset]
    if tag != TAG_COMPOUND:
        raise ValueError("Root tag is not compound")
    offset += 1
    _, offset = read_string(data, offset)  # skip root name
    # 先尝试获取顶层的内容，看是否有 "Level" 复合标签
    level_offset = None
    save_offset = offset
    # 快速扫描一遍找出 "Level" 复合标签的起始
    temp_offset = offset
    while True:
        if temp_offset >= len(data):
            break
        sub_tag = data[temp_offset]
        if sub_tag == TAG_END:
            break
        temp_offset += 1
        name, temp_offset = read_string(data, temp_offset)
        if name == "Level" and sub_tag == TAG_COMPOUND:
            # 记录 Level 复合标签的起始位置（这个位置是跳过 name 后的位置）
            level_offset = temp_offset
            break
        else:
            temp_offset = skip_payload(data, temp_offset, sub_tag)
    if level_offset is not None:
        # 直接解析 Level 复合标签
        offset = level_offset
        # 注意：此时 data[offset] 应该是 TAG_COMPOUND，我们已经知道是复合，直接进入其内部
        # 跳过复合标签本身的类型（已经确认是TAG_COMPOUND）和名称（已经跳过），直接解析内容
        # 实际上 offset 已经指向复合标签的 payload 起始，直接进入循环
        pass  # offset 已经正确设置

    # 解析当前复合标签内部（可能是根或 Level）
    entity_count = 0
    tile_count = 0
    while True:
        if offset >= len(data):
            break
        tag = data[offset]
        if tag == TAG_END:
            break
        offset += 1
        name, offset = read_string(data, offset)
        if name == "entities" and tag == TAG_LIST:
            # 解析列表长度（列表头: 元素类型(1字节) + 长度(4字节)）
            list_type = data[offset]
            length = struct.unpack(">I", data[offset+1:offset+5])[0]
            entity_count = length
            offset = skip_payload(data, offset, TAG_LIST)
        elif name in ("block_entities", "TileEntities") and tag == TAG_LIST:
            list_type = data[offset]
            length = struct.unpack(">I", data[offset+1:offset+5])[0]
            tile_count = length
            offset = skip_payload(data, offset, TAG_LIST)
        else:
            offset = skip_payload(data, offset, tag)
    return entity_count, tile_count