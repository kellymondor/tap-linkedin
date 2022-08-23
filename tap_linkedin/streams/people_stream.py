import singer
from .base_stream import BaseStream
from tap_linkedin.context import Context
from tap_linkedin.utils import sleep

LOGGER = singer.get_logger()

PAGE_SIZE = 100

class PeopleStream(BaseStream):
    stream_id = 'people'
    stream_name = 'people'
    key_properties = ["id"]
    replication_key = "start"
    count = 0
    company_ids = set()

    def get_company_ids(self):

        if PeopleStream.company_ids:
            for company_id in sorted(PeopleStream.company_ids):
                yield company_id
        else:
            pass
    
    def sync_page(self, url, page_size, company_size, region, years_of_experience, tenure, start):
    
        params = {"count": page_size, "start": start}
        time_extracted = singer.utils.now()
        
        response = self.client.get_request(url, params)
        result_count = response.get('paging').get("total")
        records = response.get('elements')
        
        for idx, record in enumerate(records):
            record["id"] = int(record.get("objectUrn").replace("urn:li:member:", ""))
            record["searchRegion"] = region
            record["searchCompanySize"] = company_size
            record["searchYearsOfExperience"] = years_of_experience
            record["searchTenure"] = tenure
            
            self.write_record(record, time_extracted)
            Context.set_bookmark(self.stream_id, self.replication_key, start + idx)

            PeopleStream.count += 1
            
            if record.get("currentPositions", None):
                for companies in record.get("currentPositions"):
                    if companies.get("companyUrn", None):
                        PeopleStream.company_ids.add(int(companies["companyUrn"].replace("urn:li:fs_salesCompany:", "")))
            
            if record.get("pastPositions", None):
                for companies in record.get("pastPositions"):
                    if companies.get("companyUrn", None):
                        PeopleStream.company_ids.add(int(companies["companyUrn"].replace("urn:li:fs_salesCompany:", "")))
        
        start += len(records)

        Context.set_bookmark(self.stream_id, self.replication_key, start)
        self.write_state()

        if start >= result_count or len(records) == 0: 
            start = None
 
        return start

    def sync_records(self, **kwargs):

        start = 0
        self.write_state()

        region = kwargs.get("region")
        company_size = kwargs.get("company_size")
        years_of_experience = kwargs.get("years_of_experience")
        tenure = kwargs.get("tenure")

        url = self.client.get_people_search_url(company_size, region, years_of_experience, tenure)
        start = self.sync_page(url, PAGE_SIZE, company_size, region, years_of_experience, tenure, start)

        while start:
            start = self.sync_page(url, PAGE_SIZE, company_size, region, years_of_experience, tenure, start)
            sleep(3, 10)

        LOGGER.info(f"{PeopleStream.count} people found with GraphQL skills.")

Context.stream_objects['people'] = PeopleStream