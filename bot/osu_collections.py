import struct, zlib
from io import BytesIO
from typing import List, Set
from dataclasses import dataclass

class StreamEncoder:
    @staticmethod
    def byte(value, buffer) -> None:
        r = struct.pack('<B', value)
        buffer.write(r)

    @staticmethod
    def int(value, buffer) -> None:
        r = struct.pack('<I', value)
        buffer.write(r)

    @staticmethod
    def double(value, buffer) -> None:
        r = struct.pack('<d', value)
        buffer.write(r)

    @staticmethod
    def uleb128(value, buffer) -> None:
        r = []
        while True:
            byte = value & 0x7f
            value = value >> 7
            if value == 0:
                r.append(byte)
                buffer.write(bytearray(r))
                return
            r.append(0x80 | byte)

    @staticmethod
    def string(value, buffer) -> None:
        encoded_value = value.encode('utf-8')
        r = struct.pack('<B', len(encoded_value))
        buffer.write(r)
        r = struct.pack(f'<{len(encoded_value)}s', encoded_value)
        buffer.write(r)

    @staticmethod
    def ulebstring(value, buffer) -> None:
        if value == "":
            StreamEncoder.byte(0x00, buffer)
        StreamEncoder.byte(0x0b, buffer)
        encoded_value = value.encode('utf-8')
        StreamEncoder.uleb128(len(encoded_value), buffer)
        r = struct.pack(f'<{len(encoded_value)}s', encoded_value)
        buffer.write(r)

@dataclass
class CollectionBeatmap:
    hash: str
    beatmap_id: int = 0
    beatmapset_id: int = 0
    artist: str = ""
    title: str = ""
    version: str = ""
    mode: int = 0
    stars: float = 0

    def __hash__(self) -> int:
        return int(self.hash, 16)

    def encode_beatmap_db(self, bytestream) -> None:
        StreamEncoder.ulebstring(self.hash, bytestream)

    def encode_beatmap_osdb(self, bytestream) -> None:
        StreamEncoder.int(self.beatmap_id, bytestream)
        StreamEncoder.int(self.beatmapset_id, bytestream)
        StreamEncoder.string(self.artist, bytestream)
        StreamEncoder.string(self.title, bytestream)
        StreamEncoder.string(self.version, bytestream)
        StreamEncoder.string(self.hash, bytestream)
        StreamEncoder.byte(0, bytestream)
        StreamEncoder.byte(self.mode, bytestream)
        StreamEncoder.double(self.stars, bytestream)

@dataclass
class CollectionSingle:
    name: str
    beatmaps: Set[CollectionBeatmap]

    def __len__(self) -> int:
        return len(self.beatmaps)

    def encode_beatmaps_db(self, bytestream) -> None:
        '''
        Encodes only the beatmaps portion of the collection in .db format.
        '''
        StreamEncoder.ulebstring(self.name, bytestream)
        StreamEncoder.int(len(self.beatmaps), bytestream)
        for beatmap in self.beatmaps:
            beatmap.encode_beatmap_db(bytestream)

    def encode_beatmaps_osdb(self, bytestream) -> None:
        '''
        Encodes only the beatmaps portion of the collection in .osdb format.
        '''
        StreamEncoder.string(self.name, bytestream)
        StreamEncoder.int(0, bytestream)
        StreamEncoder.int(len(self.beatmaps), bytestream)
        for beatmap in self.beatmaps:
            beatmap.encode_beatmap_osdb(bytestream)
        StreamEncoder.int(0, bytestream)

@dataclass
class CollectionDatabase:
    collections: List[CollectionSingle]

    def __len__(self) -> int:
        return len(self.collections)

    def encode_collections_db(self, bytestream) -> None:
        '''
        Encodes this `CollectionDatabase` as a standalone .db file.
        '''
        StreamEncoder.int(20230727, bytestream)
        StreamEncoder.int(len(self.collections), bytestream)
        for collection in self.collections:
            collection.encode_beatmaps_db(bytestream)

    def encode_collections_osdb(self, bytestream) -> None:
        '''
        Encodes this `CollectionDatabase` as a standalone .osdb file.
        '''
        StreamEncoder.string("o!dm8", bytestream)
        gzip_bytestream = BytesIO(b'')
        StreamEncoder.string("o!dm8", gzip_bytestream)
        StreamEncoder.int(0, gzip_bytestream)
        StreamEncoder.int(0, gzip_bytestream)
        StreamEncoder.string("N/A", gzip_bytestream)
        StreamEncoder.int(len(self.collections), gzip_bytestream)
        for collection in self.collections:
            collection.encode_beatmaps_osdb(gzip_bytestream)
        StreamEncoder.string("By Piotrekol", gzip_bytestream)
        gzip = zlib.compressobj(9, zlib.DEFLATED, zlib.MAX_WBITS | 16)
        gzip_data = gzip.compress(gzip_bytestream.getvalue()) + gzip.flush()
        bytestream.write(gzip_data)
