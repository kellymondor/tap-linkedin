import requests
from requests.exceptions import ConnectionError, Timeout
from tap_linkedin.exceptions import raise_for_error, LinkedInError, ReadTimeoutError, Server5xxError, LinkedInTooManyRequestsError

import backoff
import singer

LOGGER = singer.get_logger()

REQUEST_TIMEOUT = 3000
BACKOFF_MAX_TRIES_REQUEST = 5

class LinkedInClient():

    BASE_URL = "https://www.linkedin.com"
    PEOPLE_URL_PREFIX = "sales-api/salesApiLeadSearch?q=searchQuery&query=(spellCorrectionEnabled:true"
    PEOPLE_URL_SUFFIX = "decorationId=com.linkedin.sales.deco.desktop.searchv2.LeadSearchResult-7"
    
    COMPANY_URL_PREFIX = "sales-api/salesApiCompanies"
    COMPANY_URL_SUFFIX = f"""decoration=%28entityUrn%2Cname%2Cdescription%2Cindustry%2CemployeeCount%2CemployeeDisplayCount%2CemployeeCountRange%2Clocation%2Cheadquarters%2Cwebsite%2Crevenue%2CformattedRevenue%2CemployeesSearchPageUrl%2CflagshipCompanyUrl%29"""

    def __init__(self, config):
        self.keyword = config.get("keyword")
        self.__cookie = config.get("cookie")
        self.__csrf_token = config.get("csrf_token")
        self.__li_identity = config.get("li_identity")
        self.__verified = False
        self.__session = requests.Session()

    def __enter__(self):
        self.__verified = self.check_access()
        
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.__session.close()
    
    def __headers(self):
        headers = {}
        headers["accept"] = "*/*"
        headers["accept-language"] = "en-US,en;q=0.9"
        headers["cache-control"] = "no-cache"
        headers["csrf-token"] = self.__csrf_token
        headers["pragma"] = "no-cache"
        headers["x-li-identity"] = self.__li_identity
        headers["cookie"] = self.__cookie
        headers["x-li-lang"] = "en_US"
        headers["x-restli-protocol-version"] = "2.0.0"
        headers["sec-ch-ua"] = "\"Google Chrome\";v=\"93\", \" Not;A Brand\";v=\"99\", \"Chromium\";v=\"93\""
        headers["sec-ch-ua-mobile"] = "?0"
        headers["sec-ch-ua-platform"] = "\"macOS\""
        headers["sec-fetch-dest"] = "empty"
        headers["sec-fetch-mode"] = "cors"
        headers["sec-fetch-site"] = "same-origin"
        headers["x-li-page-instance"] = "urn:li:page:d_sales2_search_people;h3m149w6RCqmiOtycNuBkA=="

        return headers
    
    def get_company_url(self, linkedin_id):
        url = f"{self.BASE_URL}/{self.COMPANY_URL_PREFIX}/{linkedin_id}?{self.COMPANY_URL_SUFFIX}"
        
        return url

    def get_people_search_url(self, company_size, region, years_of_experience, tenure):

        filters = f"filters:List((type:COMPANY_HEADCOUNT,values:List((id:{company_size}))),(type:REGION,values:List((id:{region}))),(type:YEARS_AT_CURRENT_COMPANY,values:List((id:{tenure}))),(type:YEARS_OF_EXPERIENCE,values:List((id:{years_of_experience})))),keywords:{self.keyword})"
        url = f"{self.BASE_URL}/{self.PEOPLE_URL_PREFIX},{filters}&{self.PEOPLE_URL_SUFFIX}"
        
        return url
    
    @backoff.on_exception(
        backoff.expo,
        (Server5xxError, ReadTimeoutError, ConnectionError, Timeout),
        max_tries=3,
        factor=2)
    def check_access(self):

        if self.__cookie is None:
            raise Exception('Error: Missing cookie in tap config.json.')
        
        url = f"{self.BASE_URL}/sales"

        try:
            response = self.__session.get(url=url, timeout=REQUEST_TIMEOUT, headers=self.__headers())
        except requests.exceptions.Timeout as err:
            LOGGER.error(f'TIMEOUT ERROR: {err}')
            raise ReadTimeoutError

        if response.status_code != 200:
            LOGGER.error(f'Error status_code = {response.status_code}')
            raise_for_error(response)
        else:
            return True

    @backoff.on_exception(
        backoff.expo,
        (Server5xxError, ReadTimeoutError, ConnectionError, Timeout, LinkedInTooManyRequestsError),
        max_tries=BACKOFF_MAX_TRIES_REQUEST,
        factor=10,
        logger=LOGGER)
    def perform_request(self,
                        method,
                        url=None,
                        params=None,
                        json=None,
                        stream=False,
                        **kwargs):
        
        try:
            response = self.__session.request(method=method,
                                              url=url,
                                              params=params,
                                              json=json,
                                              stream=stream,
                                              timeout=REQUEST_TIMEOUT,
                                              **kwargs)

            if response.status_code >= 500:
                LOGGER.error(f'Error status_code = {response.status_code}')
                raise Server5xxError()

            if response.status_code != 200:
                LOGGER.error(f'Error status_code = {response.status_code}')
                raise_for_error(response)
            
            return response

        except requests.exceptions.Timeout as err:
            LOGGER.error(f'TIMEOUT ERROR: {err}')
            raise ReadTimeoutError(err)

    def get_request(self, url, params=None, json=None, **kwargs):
        
        if not self.__verified:
            self.__verified = self.check_access()

        response = self.perform_request(method="get",
                                            url=url,
                                            params=params,
                                            json=json,
                                            headers=self.__headers(),
                                            **kwargs)

        response_json = response.json()

        return response_json
