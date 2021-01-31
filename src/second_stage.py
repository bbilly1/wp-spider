""" collection of functions to gather additional information as a second stage """

import json
from time import sleep

import requests
from bs4 import BeautifulSoup


def discover_sitemap(config, discovered):
    """ returns a list of pages indexed in the sitemap """
    sitemap_url = config['sitemap_url']
    request_timeout = config['request_timeout']
    # get main
    print("look at sitemap")
    try:
        response = requests.get(sitemap_url)
    except ConnectionError:
        sleep(request_timeout)
        response = requests.get(sitemap_url)
    xml = response.text
    soup = BeautifulSoup(xml, features="lxml")
    sitemap_tags = soup.find_all("sitemap")
    sitemap_list = [map.findNext("loc").text for map in sitemap_tags]
    # loop through all list and get map by map
    all_sitemap_pages = []
    for sitemap in sitemap_list:
        try:
            response = requests.get(sitemap)
        except ConnectionError:
            sleep(request_timeout)
            response = requests.get(sitemap)
        xml = response.text
        soup = BeautifulSoup(xml, features="lxml")
        page_tags = soup.find_all("url")
        page_list = [map.findNext("loc").text for map in page_tags]
        # add every page to list
        for page in page_list:
            all_sitemap_pages.append(page)
    # sort and return
    all_sitemap_pages.sort()
    # add to discovered list if new
    discovered = [discovered.append(page) for page in all_sitemap_pages if page not in discovered]



def get_media_lib(config):
    """ returns a list of dics of media files in library """
    # first call
    start_url = config['start_url']
    valid_img_mime = config['valid_img_mime']
    request_timeout = config['request_timeout']
    upload_folder = config['upload_folder']
    try:
        response = requests.get(start_url + '/wp-json/wp/v2/media?per_page=100&page=1')
    except ConnectionError:
        sleep(request_timeout)
        response = requests.get(start_url + '/wp-json/wp/v2/media?per_page=100&page=1')
    total_pages = int(response.headers['X-WP-TotalPages'])
    img_lib_main = []
    # loop through pages
    for page in range(total_pages):
        page_nr = str(page + 1)
        print(f'parsing page {page_nr}/{total_pages}')
        try:
            response = requests.get(start_url + '/wp-json/wp/v2/media?per_page=100&page=' + page_nr)
        except ConnectionError:
            sleep(request_timeout)
            response = requests.get(start_url + '/wp-json/wp/v2/media?per_page=100&page=' + page_nr)
        img_json_list = json.loads(response.text)
        for img in img_json_list:
            mime_type = img['mime_type']
            if mime_type in valid_img_mime:
                img_dict = {}
                img_dict['main'] = img['media_details']['file']
                all_sizes = img['media_details']['sizes']
                sizes_list = []
                for size in all_sizes.values():
                    url = size['source_url'].lstrip(upload_folder)
                    sizes_list.append(url)
                img_dict['sizes'] = sizes_list
                img_lib_main.append(img_dict)
        # take it easy
        sleep(request_timeout)
    # return list at end
    return img_lib_main
