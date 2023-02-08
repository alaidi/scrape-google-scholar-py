from serpapi import GoogleScholarSearch
from urllib.parse import urlsplit, parse_qsl
import itertools

#TODO: support pagination using `async` parameter

def serpapi_scrape_google_scholar_author_results(
        author_id: str,
        api_key: str = None,
        lang: str = 'en',
        parse_articles: bool = False,
        article_pagination: bool = False 
    ):
    
    '''
    Extracts all author data: author info, cited by (table, graph), co-authors, all articles.
    
    Arguments:
    - author_id: author id.
    - api_key: SerpApi api key, https://serpapi.com/manage-api-key
    - lang: language for the search, https://serpapi.com/google-languages
    - parse_articles: parses first page of authour articles. Defalul is False.
    - article_pagination: True of False. Enables to parse all articles. Default is False. 
    
    Usage:
    
    data = serpapi_scrape_google_scholar_author_results(
            author_id='4T5cjVIAAAAJ',
            api_key='serpapi_api_key',
            parse_articles=True,
            article_pagination=True
        )
    
    print(data.keys()) # show available keys

    # call articles key (see other  available keys)
    for article in data['articles']:
        print(article['title'])
    '''
    
    if api_key is None:
        raise Exception('Please enter a SerpApi API key to a `api_key` argument. https://serpapi.com/manage-api-key')
    
    if author_id is None:
        raise Exception('Please enter a author id.')
    
    if api_key and author_id is None:
        raise Exception('Please enter a SerpApi API key to a `api_key`, and a author id to `author_id` arguments.')
    
    params = {
        'api_key': api_key,                  # serpapi api key
        'engine': 'google_scholar_author',   # serpapi parsing engine
        'author_id': author_id,              # search by author id
        'hl': lang                           # language
    }
    
    search = GoogleScholarSearch(params)     # where data extracts on the backend
    
    if parse_articles and article_pagination:
        # parsing all articles along with author info
        params['start'] = 0          # page number: 0 is first page, 1 is second, etc.
        params['pagesize'] = 100     # number of articles per page
        
        author_all_articles = []
        
        while True:
            results = search.get_dict()
            
            if 'error' in results:
                print(results['error'])
                break
            
            author_all_articles.append(results['articles'])
            
            # check for the `next` page
            if 'next' in results.get('serpapi_pagination', {}):
                search.params_dict.update(dict(parse_qsl(urlsplit(results['serpapi_pagination']['next']).query)))
            else:
                break
        
        results.pop('articles')
        # flatten list of all articles
        author_all_articles_flatten = list(itertools.chain(*author_all_articles))
        results['articles'] = author_all_articles_flatten
        
        keys_to_delete = ['search_metadata', 'search_parameters']

        for key_to_delete in keys_to_delete:
            results.pop(key_to_delete)
        
        return results
    
    if parse_articles:
        # parsing articles along with author info
        
        search = GoogleScholarSearch(params)
        results = search.get_dict()             # JSON -> Python dict
        
        if 'error' in results:
            raise Exception(results['error'])
        
        keys_to_delete = ['search_metadata', 'search_parameters', 'serpapi_pagination']

        for key_to_delete in keys_to_delete:
            results.pop(key_to_delete)
        
        return results
        
    if (article_pagination or parse_articles is False) or \
        (article_pagination and parse_articles is False):
        search = GoogleScholarSearch(params)
        results = search.get_dict()
        
        if 'error' in results:
            raise Exception(results['error'])
        
        keys_to_delete = ['search_metadata', 'search_parameters', 'articles', 'serpapi_pagination']

        for key_to_delete in keys_to_delete:
            results.pop(key_to_delete)
            
        return results
