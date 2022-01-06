import singer
from singer import metadata

LOGGER = singer.get_logger()

class Context():
    config = {}
    state = {}
    catalog = {}
    stream_map = {}
    stream_objects = {}

    @classmethod
    def get_catalog_entry(cls, stream_name):
        if not cls.stream_map:
            cls.stream_map = {stream["stream_id"]: stream for stream in cls.catalog['streams']}
        return cls.stream_map[stream_name]

    @classmethod
    def is_selected(cls, stream_name):
        stream = cls.get_catalog_entry(stream_name)
        stream_metadata = metadata.to_map(stream['metadata'])
        return metadata.get(stream_metadata, (), 'selected')
    
    @classmethod
    def bookmarks(cls):
        if "bookmarks" not in cls.state:
            cls.state["bookmarks"] = {}
        return cls.state["bookmarks"]
    
    @classmethod
    def bookmark(cls, stream_id):
        bookmark = cls.bookmarks()
        if stream_id not in bookmark:
            cls.state["bookmarks"][stream_id] = {}
        return cls.state["bookmarks"][stream_id]  
    
    @classmethod
    def set_bookmark(cls, stream_id, replication_key, val):
        cls.bookmark(stream_id)
        cls.state["bookmarks"][stream_id][replication_key] = val
    
    @classmethod
    def get_bookmark(cls, stream_id):
        return cls.bookmark(stream_id)

    @classmethod
    def set_state_property(cls, key, value):
        cls.state[key] = value
    
