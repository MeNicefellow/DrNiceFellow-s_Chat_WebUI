import json
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
import requests

def retrieve_web_data(search_terms, max_results=3):
    results = []
    with DDGS() as search_engine:
        for result in search_engine.text(search_terms, safesearch="Off", max_results=max_results):
            title = result["title"]
            url = result["href"]
            result_text = f' *Title*: {title} *Body*: {result["body"]}\n*Scraped_text*: {extract_site_content(url)}'
            results.append(result_text)
    return '\n'.join(results)

def extract_site_content(web_url):
    try:
        response = requests.get(web_url, timeout=3)
        soup = BeautifulSoup(response.text, "lxml")
        raw_text = soup.get_text()
        cleaned_text = ''.join(line.strip() for line in raw_text.split('\n'))
        return cleaned_text
    except Exception as e:
        print(e)
        return "Error: Requested site couldn't be viewed. Please inform in your response that the informations may not be up to date or correct."

def extract_json(content):
    # Initialize counters for curly braces
    open_brace_count = 0
    close_brace_count = 0
    json_start_index = None
    json_end_index = None

    # Iterate over the content by index and character
    for index, char in enumerate(content):
        if char == '{':
            open_brace_count += 1
            # Mark the start of JSON content
            if json_start_index is None:
                json_start_index = index
        elif char == '}':
            close_brace_count += 1
            # If the counts match, we've found the end of the JSON content
            if open_brace_count == close_brace_count:
                json_end_index = index + 1  # Include the closing brace
                break

    # If we found a start and end, extract and parse the JSON
    if json_start_index is not None and json_end_index is not None:
        json_str = content[json_start_index:json_end_index]
        try:
            json_data = json.loads(json_str)
            return json_data
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON content") from e
    else:
        raise ValueError("No JSON content found")
