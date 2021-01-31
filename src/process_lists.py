""" processing lists """

def img_processing(main_img_list, img_lib_main):
    """ takes the main_img_list and replace url with url from library """
    # loop through every picture
    for img_found in enumerate(main_img_list):
        index = img_found[0]
        search_url = img_found[1]['img_short']
        for img_in_lib in img_lib_main:
            for size in img_in_lib['sizes']:
                if size == search_url:
                    found_url = img_in_lib['main']
        main_img_list[index]['img_short'] = found_url
    # check if img is used
    main_img_list_short = [img['img_short'] for img in main_img_list]
    analyzed_img_list = []
    # loop through all imgs in library
    for img_lib in img_lib_main:
        main_url_lib = img_lib['main']
        # check if in use
        found = bool(main_url_lib in main_img_list_short)
        img_dict = {}
        img_dict["url"] = main_url_lib
        img_dict["found"] = found
        analyzed_img_list.append(img_dict)
    return analyzed_img_list
