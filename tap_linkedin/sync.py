import singer
import itertools

from tap_linkedin.streams.people_stream import PeopleStream
from tap_linkedin.streams.company_stream import CompanyStream
from tap_linkedin.client import LinkedInClient
from tap_linkedin.context import Context
from tap_linkedin.filter_criteria import REGIONS, COMPANY_SIZE, YEARS_OF_EXPERIENCE, TENURE

LOGGER = singer.get_logger()

def sync(client, config):

    combination_list = get_facet_combinations()

    currently_syncing_stream = Context.state.get('currently_syncing_stream')
    currently_syncing_query = Context.state.get('currently_syncing_query')
    
    LOGGER.info(f"Starting sync...")

    if currently_syncing_query:
        currently_syncing_query_split = currently_syncing_query.split("-")
        currently_syncing_query_company_size = currently_syncing_query_split[0]
        currently_syncing_query_facet = int(currently_syncing_query_split[1])

    if currently_syncing_stream == "companies":
        company_stream = CompanyStream(client)
        company_stream.sync()

    people_stream = PeopleStream(client)

    for key, value in combination_list.items():
        key_split = key.split("-")
        key_company_size = key_split[0]
        key_facet = int(key_split[1])
        
        if currently_syncing_query and key_company_size <= currently_syncing_query_company_size and key_facet < currently_syncing_query_facet:
            people_stream.write_state()
            LOGGER.info(f"Skipping sync for: {key}:{value}.")
            continue
        else:
            LOGGER.info(f"Running sync for: {key}:{value}.")
            Context.set_state_property('currently_syncing_query', key)
            people_stream.sync(key = key, **value)
        
        if key_facet == 174:
            company_stream = CompanyStream(client)
            company_stream.sync()



def get_facet_combinations():
    # create all combinations for searching sales nav
    # this allows us to segment search results and capture as many as possible without overlapping
    facets = []
    facets.append(list(REGIONS.values()))
    facets.append(list(YEARS_OF_EXPERIENCE.values()))
    facets.append(list(TENURE.values()))
    facet_combinations = list(itertools.product(*facets))
    
    # create a map of all combinations so we have a key for each combo
    # this will allow us to start up the sync again in the right spot in case it stops
    combo_list = {}

    # loop through with company_size first to try to avoid getting data for the same company twice
    # we use a set to capture company ids in the company stream context
    for key, value in COMPANY_SIZE.items():
        for idx, combination in enumerate(facet_combinations):
            combo_dict = {"company_size": value, "region": combination[0], "years_of_experience": combination[1], "tenure": combination[2]}
            combo_list[f"{value}-{idx}"] = combo_dict
    
    return combo_list
    



    
