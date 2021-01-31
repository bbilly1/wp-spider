""" write csv output files """

from time import strftime
import csv

def write_csv(main_img_list, main_href_list, analyzed_img_list, config):
    """ takes the list and writes proper csv files for further processing """
    start_url = config['start_url']
    timestamp = strftime('%Y-%m-%d')
    domain = start_url.split('//')[-1].split('/')[0].lstrip('www.').split('.')[0]
    filename = f'{domain}_{timestamp}_'
    # write main image csv
    with open('csv/' + filename + 'img_list.csv', 'w', newline='') as csvfile:
        fieldnames = ['page', 'img_short', 'img_status_code']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # write
        writer.writeheader()
        for row in main_img_list:
            writer.writerow(row)
    # write image library csv
    with open('csv/' + filename + 'img_lib.csv', 'w', newline='') as csvfile:
        fieldnames = ['url', 'found']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # write
        writer.writeheader()
        for row in analyzed_img_list:
            writer.writerow(row)
    # write href csv
    with open('csv/' + filename + 'href_list.csv', 'w', newline='') as csvfile:
        fieldnames = ['page', 'url', 'local', 'href_status_code']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # write
        writer.writeheader()
        for row in main_href_list:
            writer.writerow(row)
