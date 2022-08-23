import singer

from tap_linkedin.streams.people_stream import PeopleStream
from tap_linkedin.streams.company_stream import CompanyStream
from tap_linkedin.context import Context
from tap_linkedin.utils import sleep
from tap_linkedin.filter_criteria import get_facet_combinations

LOGGER = singer.get_logger()

def sync(client):

    combination_list = get_facet_combinations()

    currently_syncing_stream = Context.state.get('currently_syncing_stream')
    currently_syncing_query = Context.state.get('currently_syncing_query')

    currently_syncing_query_company_size = None
    currently_syncing_query_facet = None
    
    LOGGER.info(currently_syncing_stream)
    LOGGER.info(currently_syncing_query)
    LOGGER.info(f"Starting sync...")

    if currently_syncing_query == "I-174":
        currently_syncing_query = None

    if currently_syncing_query:
        currently_syncing_query_split = currently_syncing_query.split("-")
        currently_syncing_query_company_size = currently_syncing_query_split[0]
        currently_syncing_query_facet = 0

    people_stream = PeopleStream(client)

    for key, value in combination_list.items():

        key_split = key.split("-")
        key_company_size = key_split[0]
        key_facet = int(key_split[1])

        if currently_syncing_query_company_size and key_company_size < currently_syncing_query_company_size:
            LOGGER.info(f"Skipping sync for: {key}:{value}.")
        elif currently_syncing_query_company_size and currently_syncing_query_facet and key_company_size == currently_syncing_query_company_size and key_facet < currently_syncing_query_facet:
            LOGGER.info(f"Skipping sync for: {key}:{value}.")
        else:
            LOGGER.info(f"Running sync for: {key}:{value}.")
            Context.set_state_property('currently_syncing_query', key)
            people_stream.sync(key = key, **value)
            sleep()
        
            if key_facet == 174:
                company_stream = CompanyStream(client)
                company_stream.sync()
                sleep()
    



    
