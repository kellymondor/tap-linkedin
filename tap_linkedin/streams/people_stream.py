import singer
from .base_stream import BaseStream
from tap_linkedin.context import Context

LOGGER = singer.get_logger()

PAGE_SIZE = 100

class PeopleStream(BaseStream):
    stream_id = 'people'
    stream_name = 'people'
    key_properties = ["id"]
    replication_key = "start"
    company_ids = set()

    def get_company_ids(self):

        if PeopleStream.company_ids:
            for company_id in sorted(PeopleStream.company_ids):
                yield company_id
        else:
            pass
    
    def sync_page(self, url, page_size, start):
    
        params = {"count": page_size, "start": start}
        time_extracted = singer.utils.now()
        
        response = self.client.get_request(url, params)
        records = response.get('elements')
        
        for record in records:
            r = {}
            r["id"] = int(record.get("objectUrn").replace("urn:li:member:", ""))
            self.write_record(r, time_extracted)
            
            # if record.get("currentPositions", None):
            #     for companies in record.get("currentPositions"):
            #         if companies.get("companyUrn", None):
            #             PeopleStream.company_ids.add(int(companies["companyUrn"].replace("urn:li:fs_salesCompany:", "")))
            
            # if record.get("pastPositions", None):
            #     for companies in record.get("pastPositions"):
            #         if companies.get("companyUrn", None):
            #             PeopleStream.company_ids.add(int(companies["companyUrn"].replace("urn:li:fs_salesCompany:", "")))
        
        start += len(records)

        Context.set_bookmark(self.stream_id, self.replication_key, start)
        self.write_state()

        if len(records) < page_size: 
            start = None
 
        return start

    def sync_records(self, **kwargs):

        start = Context.get_bookmark(PeopleStream.stream_id).get(PeopleStream.replication_key, 0)
        self.write_state()

        url = self.client.get_people_search_url(kwargs.get("company_size"), kwargs.get("region"), kwargs.get("years_of_experience"), kwargs.get("tenure"))
        start = self.sync_page(url, PAGE_SIZE, start)

        while start:
            start = self.sync_page(url, PAGE_SIZE, start)

Context.stream_objects['people'] = PeopleStream