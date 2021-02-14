import re, requests, csv
from bs4 import BeautifulSoup


# CLASSES:
class Website:
    """
    This class creates a website object that contains the url pattern and css selectors to obtain the desired data.
    """

    def __init__(self, targetPattern, titleTag, dateTag, subtitleTag, descriptionTag, package_nameTag, priceTag):
        self.targetPattern = targetPattern  # Pattern (regular expression), to find the urls we want (the ones that
        # contain articles and products), inside the site.
        self.titleTag = titleTag  # CSS selector to find the title for an article and product.
        self.dateTag = dateTag  # CSS selector to find the data for an article.
        self.subtitleTag = subtitleTag  # CSS selector to find the subtitle of a product.
        self.descriptionTag = descriptionTag  # CSS selector to find the description of a product.
        self.package_nameTag = package_nameTag  # CSS selector to find the package names of a product.
        self.priceTag = priceTag  # CSS selector to find the price(s) of a product.


class Webpage:
    """
    This class defines the main characteristics that both, articles and products have in common.
    """

    def __init__(self, url, title):
        self.url = url
        self.title = title


class Product(Webpage):
    """
    This class inherits from "Webpage" class and contains the respective characteristics of a product. This way, we can
    create a product object.
    """

    def __init__(self, url, title, name, subtitle, description, package_name, price):
        Webpage.__init__(self, url, title)
        self.name = name
        self.subtitle = subtitle
        self.description = description
        self.package_name = package_name
        self.price = price

    def print_data(self):
        """
        This method prints out the info from the respective object product.
        """

        print(f"URL:\n{self.url}\n")
        print(f"TITLE:\n{self.title}\n")
        print(f"SUBTITLE:\n{self.subtitle}\n")
        print(f"DESCRIPTION:\n{self.description}\n")
        print(f"PACKAGE NAME:\n{self.package_name}\n")
        print(f"PRICE:\n{self.price}\n")


class Article(Webpage):
    """
    This class inherits from "Webpage" class and contains the respective characteristics of an article. This way, we can
    create an article object.
    """

    def __init__(self, url, title, date):
        Webpage.__init__(self, url, title)
        self.date = date

    def print_data(self):
        """
        This method prints out the info from the respective object article.
        """

        print(f"URL:\n{self.url}\n")
        print(f"TITLE:\n{self.title}\n")
        print(f"DATE:\n{self.date}\n")


class Crawler:
    """
    The object created from this class, crawls every article links inside the desired url to obtain the products and
    more articles.
    """

    def __init__(self, site):
        self.site = site  # We pass a "Website" object, in order to access to the website object methods, attribs, etc.
        self.visited_articles = list()  # To store the article links we have visited.
        self.visited_products = list()  # To store the product links we have visited.

    def getPage(self, url):
        """
        This method requests the html tree and turn it into a BeautifulSoup object.
        """

        try:
            req = requests.get(url)
        except requests.exceptions.RequestException as e:
            print(f"Failed when requesting the html tree from the URL:\n{url}")
            print(f"Error:\n{e}\n")
            return None
        return BeautifulSoup(req.text, 'lxml')

    def safeGet(self, bs_obj, selector):
        """
        This method retrieves the data from the BeautifulSoup object created using CSS selectors. Once the data
        is retrieved, we proceed to clean it out.
        """

        selectedElems = bs_obj.select(selector)  # The desired data is retrieved here using the respective selector.
        if selectedElems is not None and len(selectedElems) > 0:
            return '\n'.join([elem.get_text().replace('\n','').replace('\r','').replace('\t','').strip()
                              for elem in selectedElems])  # We clean every element obtained and join them using '\n'.
        return ''  # In case the above condition isn't met, we return an empty string.

    def parse(self, url):
        """
        This method creates an object article or product, (depending on the data retrieved using the method "safeGet()").
        """

        bs = self.getPage(url)  # We use the method "getPage()" to turn the html tree into a BeautifulSoup object.
        if bs is not None:  # In case we successfully turn the html tree into a BeautifulSoup object. Otherwise, we
            # won't create any object.
            # We retrieve the main data that make up an article:
            title = self.safeGet(bs, self.site.titleTag).split('\n')[0]
            date = self.safeGet(bs, self.site.dateTag)
            # We retrieve the main data that make up a product:
            subtitle = self.safeGet(bs, self.site.subtitleTag)
            package_name = self.safeGet(bs, self.site.package_nameTag)

            try:
                # We check whether the data retrieved corresponds to an article, product, or none of them:
                if title != '' and date != '':  # IN CASE WE ARE DEALING WITH AN ARTICLE.
                    article = Article(url, title, date)  # Creating the article object.
                    articles_stored.append(article)  # We store every article object created.
                    article.print_data()  # We print out the data that belongs the article object.

                elif subtitle != '' and package_name != '':  # IN CASE IT IS A PRODUCT.
                    description = self.safeGet(bs, self.site.descriptionTag)  # We get the description.
                    description = description if description else "No Description Contained."  # Verifying whether
                    # there's a description or not. If there's no a description we pass "No Description Contained".
                    prices = self.safeGet(bs, self.site.priceTag)  # We get the price(s).
                    prices = cleaning_prices(prices)  # We clean the price(s) obtained. We get rid of signs like '$',
                    # white spaces, etc. Except (obviously), for the period that divides the decimal ones.
                    # We create a product object:
                    product = Product(url, title, url.split('/')[-2], subtitle, description, package_name, prices)
                    products_stored.append(product)  # We store every product object created.
                    product.print_data()  # We print out the data that belongs the product object.

                else:  # IN CASE THE WEBSITE DO NOT CONTAIN ANY ARTICLE OR PRODUCT.
                    print("THE URL DON'T CONTAIN ANY ARTICLE OR PRODUCT.")
                print("#" * 60)

            except Exception as e:
                print("Something went wrong when working with the actual page. The error is the following:")
                print(f"Error:\n{e}")
                print("\nLet's continue with the next url.")

    def crawl(self, url):
        """
        Get pages from website home page.
        """

        bs = self.getPage(url)  # We use the method "getPage()" to turn the html tree into a BeautifulSoup object.
        bs = bs if bs else self.getPage(self.visited_articles[-1])  # In case we weren't able to turn the current url
        # into a BeautifulSoup object, we go back and take the last url in the list.
        # We retrieve the pages inside the main content that we are interested in:
        targetPages = bs.find("div", {"class":"entry-content"}).find_all('a', href=re.compile(self.site.targetPattern))
        pattern = re.compile(r"/\w+/\w+/\w+/")  # We create a pattern to get the articles.

        for targetPage in targetPages:
            targetPage = targetPage.attrs['href']  # We retrieve the URL itself from the attribute "href".
            if pattern.search(targetPage):  # If the pattern returns match, it means this is an article.
                url_content = storing_article_urls(targetPage)  # We obtain the url content after the domains (
                # "www.pyimagesearch.com" or "pyimagesearch.com"), cause some articles are repeated with different
                # domains.
                if url_content not in self.visited_articles:  # Checking whether the url content after the domain has
                    # been visited. If the site has already been visited, we don't proceed, since we only want to visit
                    # every article once.
                    self.visited_articles.append(url_content)  # Appending every site visited, to avoid visit them twice.
                    self.parse(targetPage)  # EXTRACTING THE DATA FROM THE CURRENT ARTICLE.
                    self.crawl(targetPage)  # CRAWLING THROUGH EVERY ARTICLE LINK FOUND.

            else:  # In case this is a product.
                url_content = storing_product_urls(targetPage)  # We obtain the url content after the domains (
                # "www.pyimagesearch.com" or "pyimagesearch.com"), cause some products are repeated with different
                # domains.
                if url_content not in self.visited_products:  # Checking whether the url content after the domain has
                    # been visited. If the site has already been visited, we don't proceed, since we only want to visit
                    # every product once.
                    self.visited_products.append(url_content)  # Appending every site visited, to avoid visit them twice.
                    self.parse(targetPage)  # EXTRACTING THE PRODUCT(S) FROM THE CURRENT ARTICLE.


# FUNCTION(S):
def cleaning_prices(prices):
    """This function cleans every price to keep only the numbers and the respective period (if applicable)."""

    price_chars = ''
    for price in prices.split('\n'):
        for p in filter(lambda x: x.isdigit() or x == '.', price):
            price_chars += p
        price_chars += '\n'
    return price_chars


def storing_article_urls(url):
    """This functions stores the url content of an article after the domain, to avoid visit the same site twice."""

    split_1 = url.split('//')
    split_2 = split_1[-1].split('/')[1:]
    split_2 = "/".join(split_2)
    return split_2


def storing_product_urls(url):
    """This functions stores the url content of a product after the domain, to avoid visit the same site twice."""

    split_1 = url.split('//')
    split_2 = split_1[-1].split('/')[1]
    return split_2


def save_data_articles(file_name, content_list):
    """This function saves the retrieved data."""

    assert file_name.split('.')[-1] == "csv", "THE FILE EXTENSION MUST BE 'csv'."

    with open(f"{file_name}", "a") as csv_outfile:
        field_names = ("ARTICLE", "DATE", "URL")
        csv_writer = csv.DictWriter(csv_outfile, fieldnames=field_names, lineterminator='\n')
        csv_writer.writeheader()
        for article_obj in content_list:
            try:
                csv_writer.writerow({"ARTICLE":article_obj.title, "DATE":article_obj.date, "URL":article_obj.url})
            except Exception as e:
                print("There was something wrong when saving the data. Let's try with the next one.")
                print(f"By the way, the error is the following: \n{e}\n")


def save_data_products(file_name, content_list):
    """This function saves the retrieved data."""

    assert file_name.split('.')[-1] == "csv", "THE FILE EXTENSION MUST BE 'csv'."

    with open(f"{file_name}", "a") as csv_outfile:
        field_names = ("PRODUCT", "TITLE", "SUBTITLE", "DESCRIPTION", "PACKAGE_NAME", "PRICE", "URL")
        csv_writer = csv.DictWriter(csv_outfile, fieldnames=field_names, lineterminator='\n')
        csv_writer.writeheader()
        for product_obj in content_list:
            try:
                if len(product_obj.package_name.split('\n')) >= 2:  # If the product has more than 1 presentation.
                    for package,price in zip(product_obj.package_name.split('\n'), product_obj.price.split('\n')):
                        csv_writer.writerow({"PRODUCT": product_obj.name, "TITLE": product_obj.title,
                                             "SUBTITLE": product_obj.subtitle, "DESCRIPTION": product_obj.description,
                                             "PACKAGE_NAME":package, "PRICE":price, "URL": product_obj.url})

                else:  # The product just has one price and one presentation.
                    csv_writer.writerow({"PRODUCT":product_obj.name, "TITLE":product_obj.title,
                                         "SUBTITLE":product_obj.subtitle, "DESCRIPTION":product_obj.description,
                                         "PACKAGE_NAME":product_obj.package_name, "PRICE":product_obj.price,
                                         "URL":product_obj.url})

            except Exception as e:
                print("There was something wrong when saving the data. Let's try with the next one.")
                print(f"By the way, the error is the following: \n{e}\n")

########################################################################################################################
# ALGORITHM I CAME UP WITH TO CRAWL AND EXTRACT DATA FROM "pyimagesearch.com":
"""
1. Select the website we want to scrape on. Then, choose an article to start with.
2. Extract "title", "date" and "url" from the current article. The articles mustn't be repeated.
3. Inside the current article, extract product info ("title", "subtitle", "description", "package", "price(s)"). 
   Do not repeat them. If an article has the same products than an old one, do not store them. The products mustn't 
   be repeated.
4. Crawl every article's link inside the current article.
5. Repeat the process from 2 to 4 until work with every article and product on the website.
"""
########################################################################################################################
# DEFINING THE WEBSITE DATA NEEDED TO CREATE AN OBJECT WEBSITE:

# WEBSITE MAIN CHARACTERISTICS:
article_seed_url = "https://www.pyimagesearch.com/2021/01/18/contrastive-loss-for-siamese-\
networks-with-keras-and-tensorflow/"
articles_pattern = r"https://(pyimagesearch.com|www.pyimagesearch.com)(((?!reviews)(?!contact)(?!tag)" \
                   r"(?!\?)(?!category)(?!uploads)(?!faqs)(?!wp-content)(?!jpg)(?!gif)).)*$"

# ARTICLE (CSS Selectors):
title_selector = "h1"
date_selector = "time.entry-time"

# PRODUCT (CSS Selectors):
subtitle_selector = "section#banner div.one_half > h2, section#banner > div > div > p, div#banner > div > div > p"
description_selector = "section#banner div.one_half > p, div#banner div.hero-desc > p"
package_name_selector = "div#pricing_table div.pricing_header > h4, div.pricing-table div.bundle-heading"
price_selector = "div#pricing_table p.price, div.pricing-table > div[class*='bundle'] span.bundle-price"

Pyimagesearch_website = Website(articles_pattern, title_selector, date_selector, subtitle_selector, description_selector,
                                package_name_selector, price_selector)  # Creating the object Website.
########################################################################################################################
# STARTING TASKS:
articles_stored = list()  # To store the article objects created.
products_stored = list()  # To store the product objects created.
crawler = Crawler(Pyimagesearch_website)  # We create the object crawler.
crawler.crawl(article_seed_url)  # We start to extract data and crawl websites.

########################################################################################################################
# SAVING DATA:
save_data_articles("articles_pyimagesearch.csv", articles_stored)
save_data_products("products_pyimagesearch.csv", products_stored)

########################################################################################################################
print('\r')
print("Articles visited:", len(crawler.visited_articles))
print("Products visited:", len(crawler.visited_products))
