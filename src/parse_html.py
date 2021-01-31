""" parses and processes the html for each page """

from time import sleep
import requests

def get_hrefs(soup, home_pass=True):
    """ takes the soup and returns all href found
    excludes # links and links to jpg files """
    url_set = set()
    # loop through soup
    all_links = soup.find_all("a")
    for link in all_links:
        try:
            url = link["href"]
        except KeyError:
            continue
        if url.startswith('http') and not url.endswith('#') and not url.lower().endswith('.jpg'):
            url_set.add(url)
    href_url_list = list(url_set)
    # remove top nav items if not homepage
    if home_pass:
        # split soop
        soup_nav = soup.find("nav", {"role": "navigation"})
        soup_footer = soup.find("div", {"class": "elementor-location-footer"})
        # get links links
        try:
            all_nav_links = list(set([x["href"] for x in soup_nav.find_all("a")]))
            all_footer_links = list(set([x["href"] for x in soup_footer.find_all("a")]))
            href_url_list = [link for link in href_url_list if link not in all_nav_links]
            href_url_list = [link for link in href_url_list if link not in all_footer_links]
        except:
            pass
    href_url_list.sort()
    return href_url_list


def get_images(soup, config):
    """ takes the soup and returns all images from
    img html tags, inline css and external CSS files """
    upload_folder = config['upload_folder']
    request_timeout = config['request_timeout']
    img_url_set = set()
    # from img tag
    all_imgs = soup.find_all("img")
    for img in all_imgs:
        url = img["src"]
        if upload_folder in url:
            img_url_set.add(url)
    # from inline style tag
    all_divs = soup.find_all('div')
    for div in all_divs:
        try:
            style = div["style"]
            if 'background-image' in style:
                url = style.split('(')[1].split(')')[0]
                img_url_set.add(url)
        except:
            continue
    # external
    all_external_css = soup.find_all("link", {"rel": "stylesheet"})
    for css_file in all_external_css:
        remote_file = all_external_css[0]["href"]
        try:
            remote_css = requests.get(remote_file).text
        except ConnectionError:
            sleep(request_timeout)
            remote_css = requests.get(remote_file).text
        css_rules = remote_css.split(';')
        for rule in css_rules:
            if upload_folder in rule:
                url = rule.split('(')[1].split(')')[0]
                img_url_set.add(url)
    img_url_list = list(img_url_set)
    img_url_list.sort()
    return img_url_list
