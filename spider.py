#!/usr/bin/env python3
""" spiderman """

import configparser
from time import sleep

import requests
from bs4 import BeautifulSoup

import src.parse_html as parse_html
import src.second_stage as second_stage
import src.process_lists as process_lists
import src.write_output as write_output


def get_config():
    """ read out the config file and return config dict """
    # parse
    config_parser = configparser.ConfigParser()
    config_parser.read('config')
    # create dict
    config = {}
    config["start_url"] = config_parser.get('setup', "start_url")
    config["sitemap_url"] = config_parser.get('setup', "sitemap_url")
    config["upload_folder"] = config_parser.get('setup', "upload_folder")
    config["top_nav_class"] = config_parser.get('setup', "top_nav_class")
    config["footer_class"] = config_parser.get('setup', "footer_class")
    config["request_timeout"] = int(config_parser.get('setup', "request_timeout"))
    mime_list = config_parser.get('setup', "valid_img_mime").split(',')
    config["valid_img_mime"] = [mime.strip() for mime in mime_list]
    return config


def main():
    """ start the whole spider process from here """
    # get config
    config = get_config()
    # controll progress
    discovered = []
    indexed = []
    # main lists to collect results
    main_img_list = []
    main_href_list = []
    # poor man's caching
    connectivity_cache = []
    # start with start_url
    start_url = config['start_url']
    discovered.append(start_url)
    page_processing(discovered, indexed, main_img_list,
               main_href_list, connectivity_cache, config)
    # add from sitemap and restart
    second_stage.discover_sitemap(config, discovered)
    page_processing(discovered, indexed, main_img_list,
               main_href_list, connectivity_cache, config)
    # read out library
    img_lib_main = second_stage.get_media_lib(config)
    # compare
    analyzed_img_list = process_lists.img_processing(main_img_list, img_lib_main)
    # write csv files
    write_output.write_csv(main_img_list, main_href_list, analyzed_img_list, config)



def page_processing(discovered, indexed, main_img_list, main_href_list, connectivity_cache, config):
    """ start the main loop to discover new pages """
    request_timeout = config['request_timeout']
    for page in discovered:
        if page not in indexed:
            print(f'parsing [{len(indexed)}]/[{len(discovered)}] {page}')
            img_list, href_list = parse_page(page, connectivity_cache, config)
            for img in img_list:
                main_img_list.append(img)
            for href in href_list:
                main_href_list.append(href)
                url = href['url']
                # add to discovered if al match
                is_local = href['local']
                not_discovered = url not in discovered
                not_hash_link = '#' not in url
                not_bad_ending = url.lower().split('.')[-1] not in ['pdf', 'jpeg']
                if is_local and not_discovered and not_hash_link and not_bad_ending:
                    discovered.append(url)
            # done
            indexed.append(page)
            # take it easy
            sleep(request_timeout)


def connectivity(url, connectivity_cache):
    """ returns html status code from url """
    # look if its already in the list
    already_found = next((item for item in connectivity_cache if item["url"] == url), None)
    user_agent = ( "Mozilla/5.0 (Windows NT 10.0; Win64; x64), "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/70.0.3538.77 Safari/537.36" )
    headers = { 'User-Agent': user_agent }
    if not already_found:
        try:
            request = requests.head(url, timeout=5, headers=headers)
            status_code = request.status_code
            connectivity_cache.append({"url": url, "status_code": status_code})
        except requests.exceptions.RequestException:
            print('failed at: ' + url)
            status_code = 404
    else:
        status_code = already_found["status_code"]
    return status_code


def parse_page(page, connectivity_cache, config):
    """ takes the page url and returns all img and href """
    request_timeout = config['request_timeout']
    start_url = config['start_url']
    upload_folder = config['upload_folder']
    try:
        response = requests.get(page)
    except ConnectionError:
        sleep(request_timeout)
        response = requests.get(page)
    soup = BeautifulSoup(response.text,'lxml')
    img_url_list = parse_html.get_images(soup, config)
    # do full scan on homepage, else ignore topnav and footer
    if page == start_url:
        href_url_list = parse_html.get_hrefs(soup, home_pass=False)
    else:
        href_url_list = parse_html.get_hrefs(soup)
    # parse imgs
    img_list = []
    for url in img_url_list:
        img_short = url.lstrip(upload_folder)
        img_status_code = connectivity(url, connectivity_cache)
        img_line_dict = {}
        img_line_dict["page"] = page
        img_line_dict["img_short"] = img_short
        img_line_dict["img_status_code"] = img_status_code
        img_list.append(img_line_dict)
    # parse hrefs
    href_list = []
    for url in href_url_list:
        href_status_code = connectivity(url, connectivity_cache)
        local = bool(url.startswith(start_url.rstrip('/')))
        href_line_dict = {}
        href_line_dict["page"] = page
        href_line_dict["url"] = url
        href_line_dict["local"] = local
        href_line_dict["href_status_code"] = href_status_code
        href_list.append(href_line_dict)
    return img_list, href_list


# lunch from here
if __name__ == '__main__':
    main()
