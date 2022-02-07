import singer
from .base_stream import BaseStream
from tap_linkedin.context import Context
from tap_linkedin.exceptions import LinkedInNotFoundError

LOGGER = singer.get_logger()

class CompanyStream(BaseStream):
    stream_id = 'companies'
    stream_name = 'companies'
    key_properties = ["id"]
    replication_key = "id"
    count = 0

    def sync_records(self, **kwargs):
        people_stream = Context.stream_objects['people'](self.client)
        company_ids = people_stream.get_company_ids()

        for company_id in company_ids:
            time_extracted = singer.utils.now()
            url = self.client.get_company_url(company_id)
            try:
                record = self.client.get_request(url)
            except LinkedInNotFoundError as e:
                # occassionaly a company page will be removed but we don't want that to stop the sync
                # not sure why this happens, maybe clean up on linkedin's side
                LOGGER.info(e)
            
            record["id"] = company_id
            self.write_record(record, time_extracted=time_extracted)
            Context.set_bookmark(self.stream_id, self.replication_key, company_id)
            CompanyStream.count += 1
        
        LOGGER.info(f"{CompanyStream.count} companies found using GraphQL.")
