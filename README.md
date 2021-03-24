# wp-spider
## A spider to go through a Wordpress website.

## Usecase
Wordpress doesn't make it easy to keep the media library organized. On sites constantly changing, particularly when multiple users are involved, the media library can grow out of control fast. This can result in decreased performance, unnecessary disk storage usage, ever growing backup files and other potential problems in the future.

That's where **wp-spider** comes to the rescue: This Python script will go through every page on your site and compare the pictures visible with your pictures in your media library and then output the result into a set of convenient CSV files for you to further analyze with your favourite Spreadsheet software.

Additionally the spider will also check any link for dead links, going to ressources that don't exist. Same it will check if any images on the site are missing from your library.

**Disclaimer:** Don't run this script against a site you are not the owner of or you don't have permission to do so. Traffic like that might get interpreted as malicious and might result in throttling of your connection or even a ban. If you have any measures like that on your site, it might be a good idea to add your IP to the whitelist.


## How it works
The script will start from the *start_url* as defined in the config file, parse the html and look for every link and for every image either via *<img>* tag or via *background-image* CSS property.  
Then the script will follow every link on the same domain and parse the HTML. Links in the top nav and the footer will only get checked once assuming that the top nav and footer will be identical on every page.  
For links outside *start_url* the script will make a head request to check the validity of the link.  
After every visible page has been scraped, the script will look at the sitemap for any sites not indexed yet.  
Then the script will loop through all pages in your media library by calling the standard wordpress API path *https://www.example.com/wp-json/wp/v2/media* to index all pictures in the library.  
And as a last step, the script will compare the pictures visible with the pictures in the library, look at all the links and write the result to CSV.


## Limitations
BeautifulSoup needs to be able to parse the page correctly. Content loaded purely over javascript might not be readable by BeautifulSoup.  
Pages not publicly visible will not get parsed. Same for pages never linked on your site and not listed in the sitemap.  
Pictures not in use on the website but in use anywhere else like in email publications might show up as *not found*.


## Pros and Cons
There are other similar solutions that try to do the same thing with a different approach namely as a wordpress plugin. That approach is usually based on calling the wordpress database directly. Depending on how the site was built, that might result in a incomplete picture as the plugin in question might not consider that a sitebuilder is using a different database table as expected and therefore will not find the picture in use.  
That's how this approach is different: If the picture is visible in the HTML it will show as *in use*, so that is an implementation agnostic approach.  
The downside, additional to the limitations above is, that depending on the amount of pages, library size and more, it can take a long time to go through every page, particularly with a safe *request_timeout* value.


## Installation
Install required none standard Python libraries:  
**requests** to make the HTTP calls, [link](https://pypi.org/project/requests/)
* On Arch: `sudo pacman -S python-requests`
* Via Pip: `pip install requests`

**bs4** aka *BeautifulSoup4* to parse the html, [link](https://pypi.org/project/beautifulsoup4/)
* On Arch: `sudo pacman -S python-beautifulsoup4`
* Via Pip: `pip install beautifulsoup4`

or use `pip` to install the requirements:  
`pip install -r requirements.txt`

## Run
Make sure the `config` file is setup correctly, see bellow.  
Run the script from the *wp-spider* folder with `./spider.py`.  
After completion check the *csv* folder for the result.


## Interpret the result
After completion the script will create three CSV files in the csv folder, time stamped on date of completion:
1. href_list.csv: A list of every link on every page with the following columns:
    * **page**              : The page the link was found.
    * **url**               : Where the link is going to.
    * **local**             : *True* if the link is going to a page on the same domain, *False* if link is going out to another domain.
    * **href_status_code**  : HTML status code of the link.
2. img_lib.csv: A list of every image discovered in your wordpress library with the following columns:
    * **url**               : The shortened direct link to the picture, extend it with *upload_folder* to get the full link.
    * **found**             : *True* if the picture has been found anywhere on the website, *False* if the picture has not been found anywhere.
3. img_list.csv: A list of all images discovered anywhere on the website, with the following columns:
    * **page**              : Page the picture has been found.
    * **img_short**         : Shortened URL to the picture in the media library.
    * **img_status_code**   : HTTP status code of the image URL.

From there it is straight forward to further analyze the result by filtering the list by pictures not in use, links not resulting in a 200 HTTP response, pictures on the site that don't exist in the library and many other conclusions. 


## Config
Copy or rename the file *config.sample* to *config* and make sure you set all the variables.
The config file supports the following settings:
* *start_url*       : Fully qualified URL of the home page of the website to parse. Add *www* if your canonical website uses it to avoid landing in a redirect for every request.
    * example: `https://www.example.com/`
* *sitemap_url*     : Link to the sitemap, so pages not linked anywhere but indexed can get parsed too. Link can be direct link to your sitemap or link to a list of sitemaps.
    * example: `https://www.example.com/sitemap_index.xml`
    * example: `https://www.example.com/sitemap.xml`
* *upload_folder*   : Wordpress upload folder where the media library builds the folder tree.
    * example: `https://www.example.com/wp-content/uploads/` for a default wordpress installation.
* *valid_img_mime*  : A comma separated list of image [MIME types](https://www.iana.org/assignments/media-types/media-types.xhtml#image) you want to consider as a image to check for its existence. An easy way to exclude files like PDFs or other media files.
    * example: `image/jpeg, image/png`
* *top_nav_class*   : The CSS class of the top nav bar so the script doesn't have to re-check these links over and over for every page.
    * example: `top-nav-class`
* *footer_class*    : The CSS class of the footer, to avoid rechecking these links for every page.
    * example: `footer-class`
* *request_timeout* : Time out in **seconds** between every request to avoid overloading server resources. Particularly important if the site is hosted on shared hosting and / or if a rate limiter is in place.
    * example: `30`
