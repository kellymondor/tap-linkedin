import singer
from .base_stream import BaseStream
from tap_linkedin.context import Context
from tap_linkedin.filter_criteria import REGIONS

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
    
    def sync_page(self, url, page_size, region, start):
    
        params = {"count": page_size, "start": start}
        time_extracted = singer.utils.now()
        
        response = self.client.get_request(url, params)
        records = response.get('elements')
        
        for record in records:
            record["id"] = int(record.get("objectUrn").replace("urn:li:member:", ""))
            record["searchRegion"] = region

            entity_urn = record.get("entityUrn").split(":")[3].split(",")
            profile_id = entity_urn[0].strip("(")
            auth_type = entity_urn[1]
            auth_token = entity_urn[2].strip(")")

            profile_url = self.client.get_person_profile_url(profile_id, auth_type, auth_token)
            response = self.client.get_request(profile_url)
            record.update(response)
            
            self.write_record(record, time_extracted)
            
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

        if len(records) < page_size: 
            start = None
 
        return start

    def sync_records(self, **kwargs):

        start = Context.get_bookmark(PeopleStream.stream_id).get(PeopleStream.replication_key, 0)
        self.write_state()

        region = kwargs.get("region")
        company_size = kwargs.get("company_size")
        years_of_experience = kwargs.get("years_of_experience")
        tenure = kwargs.get("tenure")

        url = self.client.get_people_search_url(company_size, region, years_of_experience, tenure)
        start = self.sync_page(url, PAGE_SIZE, region, start)

        while start:
            start = self.sync_page(url, PAGE_SIZE, region, start)

Context.stream_objects['people'] = PeopleStream