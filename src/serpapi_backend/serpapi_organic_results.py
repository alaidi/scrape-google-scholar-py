from serpapi import GoogleScholarSearch
from urllib.parse import urlsplit, parse_qsl
import pandas as pd
import itertools

#TODO: support pagination using `async` parameter

def serpapi_scrape_google_scholar_organic_results(
        query: str,
        api_key: str = None,
        lang: str = 'en',
        pagination: bool = False
    ):
    
    '''
    This function extracts data from organic results. With or without pagination.
    
    Arguments:
    - query: search query
    - api_key: SerpApi api key, https://serpapi.com/manage-api-key
    - lang: language for the search, https://serpapi.com/google-languages
    - pagination: True of False. Enables pagination from all pages. 
    
    Usage:
    
    data = serpapi_scrape_google_scholar_organic_results(query='minecraft', api_key='serpapi_api_key', pagination=True)
    
    print(data[0].keys()) # show available keys
    
    for result in data:
        print(result['title'])
        # get other data
    '''
    
    if api_key is None:
        raise Exception('Please enter a SerpApi API key to a `api_key` argument. https://serpapi.com/manage-api-key')
    
    if api_key and query is None:
        raise Exception('Please enter a SerpApi API key to a `api_key`, and a search query to `query` arguments.')
    
    params = {
        'api_key': api_key,              # serpapi api key: https://serpapi.com/manage-api-key
        'engine': 'google_scholar',      # serpapi parsing engine
        'q': query,                      # search query
        'hl': lang,                      # language
        'start': 0                       # first page. Used for pagination: https://serpapi.com/google-scholar-api#api-parameters-pagination-start
    }
    
    search = GoogleScholarSearch(params) # where data extracts on the backend
    
    if pagination:
        organic_results_data = []
        
        while True:
            results = search.get_dict()  # JSON -> Python dict
            
            if 'error' in results:
                print(results['error'])
                break
            
            organic_results_data.append(results['organic_results'])
            
            # check for `serpapi_pagination` and then for `next` page
            if 'next' in results.get('serpapi_pagination', {}):
                search.params_dict.update(dict(parse_qsl(urlsplit(results['serpapi_pagination']['next']).query)))
            else:
                break

        # flatten list
        return list(itertools.chain(*organic_results_data))
    else:
        # remove page number key from the JSON response
        params.pop('start')
        
        search = GoogleScholarSearch(params)
        results = search.get_dict()
        
        if 'error' in results:
            raise Exception(results['error'])
        
        return results['organic_results']