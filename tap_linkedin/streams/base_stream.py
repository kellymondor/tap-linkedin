import singer
from singer.schema import Schema
import os
from tap_linkedin.context import Context

LOGGER = singer.get_logger()

class BaseStream():
    
    stream_id = None
    stream_name = None
    replication_key = None
    key_properties = []
    state = {}
    
    def __init__(self, client):
        self.client = client
        self.schema = self.__load_schema()
    
    def __load_schema(self):
        
        schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "schemas")
        schema_json = singer.utils.load_json(f"{schema_path}/{self.stream_id}.json")
        # schema = schema_json
        
        return schema_json
    
    def write_record(self, record, time_extracted):  
        
        try:
            singer.write_record(self.stream_name, record, time_extracted=time_extracted)
        except OSError as err:
            LOGGER.error(f'OS Error writing record for: {self.stream_name}')
            raise err

    def write_schema(self):
        
        try:
            singer.write_schema(self.stream_name, self.schema.to_dict(), self.key_properties)
        except OSError as err:
            LOGGER.error(f'OS Error writing schema for: {self.stream_name}')
            raise err
    
    def write_state(self):
        
        try:
            singer.write_state(Context.state)
        except OSError as err:
            LOGGER.error(f'OS Error writing state for: {self.stream_name}')
            raise err

    def sync_records(self, **kwargs):
        pass

    def sync(self, **kwargs):
        LOGGER.info(f"Syncing stream: {self.stream_name}")
        Context.set_state_property('currently_syncing_stream', self.stream_id)
        self.write_schema()
        self.sync_records(**kwargs)
        Context.set_bookmark(self.stream_id, self.replication_key, 0)