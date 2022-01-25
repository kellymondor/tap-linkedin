import singer
import itertools

from tap_linkedin.streams.people_stream import PeopleStream
from tap_linkedin.streams.company_stream import CompanyStream
from tap_linkedin.client import LinkedInClient
from tap_linkedin.context import Context

LOGGER = singer.get_logger()

REGIONS = {
    "northamerica": '102221843',
    "southamerica": '104514572',
    "europe": '100506914',
    "asia": '102393603',
    "australia": '101452733',
    "africa": '103537801',
    "antarctica": '100428639'
}

COMPANY_SIZE = {
    'selfemployed': 'A',  
    '1-10': 'B',
    '11-50': 'C',
    '51-200': 'D',
    '201-500': 'E',
    '501-1000': 'F',
    '1001-5000': 'G',
    '5001-10000': 'H',
    '10000plus': 'I'
}  

YEARS_OF_EXPERIENCE = {
    '10plus': '5',
    '6-10': '4',
    '3-5': '3',
    '1-2': '2',
    'under1': '1'
}

TENURE = {
    '10plus': '5',
    '6-10': '4',
    '3-5': '3',
    '1-2': '2',
    'under1': '1'
}

def sync(client, config):

    combination_list = get_facet_combinations()
    
    people_stream = PeopleStream(client)
    company_stream = CompanyStream(client)

    currently_syncing_stream = Context.state.get('currently_syncing_stream')
    currently_syncing_query = Context.state.get('currently_syncing_query')

    if currently_syncing_stream == "companies":
        company_stream.sync()

    for key, value in combination_list.items():
        if currently_syncing_query and key < currently_syncing_query:
            LOGGER.info(f"Skipping sync for: {key}:{value}.")
            continue
        else:
            LOGGER.info(f"Running sync for: {key}:{value}.")
            Context.set_state_property('currently_syncing_query', key)
            people_stream.sync(key = key, **value)
        
        if "174" in key:
            company_stream.sync()



def get_facet_combinations():
    # create all combinations for searching sales nav
    # this allows us to segment search results and capture as many as possible without overlapping
    facets = []
    facets.append(list(REGIONS.values()))
    facets.append(list(YEARS_OF_EXPERIENCE.values()))
    facets.append(list(TENURE.values()))
    facet_combinations = list(itertools.product(*facets))
    
    LOGGER.info(f"Starting sync...")
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
    



    
