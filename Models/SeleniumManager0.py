import os
from collections.abc import Iterable
from datetime import datetime, timedelta
import time

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from attr import dataclass
from selenium.webdriver import Keys
from selenium.webdriver.remote.webelement import WebElement, BaseWebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import csv
from Models import ManagerBase
from selenium import webdriver
from selenium.webdriver.common.by import By

timeout = 10
REPEAT_INITIAL_VALUE = 5


@dataclass
class Listing:
    name: str
    url: str
    img_url: list[str]
    end_time: datetime
    last_price: float
    retail_price: float
    condition: str


class URLS:
    # auction

    site: str = "https://www.onlineliquidationauction.com/"
    auctions: str = '/html/body/div[2]/div[5]/div/div[1]/div[1]'
    auction_name: str = '/html/body/div[2]/div[5]/div/div[1]/div[1]/div[2]/h2/a'
    auction_url: str = '/html/body/div[2]/div[5]/div/div[1]/div[1]/div[2]/h2/a'
    auction_img: str = '/html/body/div[2]/div[5]/div/div[1]/div[1]/div[1]/div/div[1]/div/div[1]/div/a/img'

    # item

    select: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[3]/select'
    active_item: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[3]/select/optgroup[2]/option[2]'
    count: str = '//*[@id="many-items"]/div[3]/select/optgroup[2]/option[2]'
    first_item: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[1]/div/div/div/a'
    body: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div'
    items: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result'
    name: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[1]/div/div/div/a'
    listing_url: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[1]/div/div/div/a'
    img_elements: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[2]/div[1]/owl-carousel/div[1]/div/div[1]'
    img_src: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[2]/div[1]/owl-carousel/div[1]/div/div[1]/div/img'
    date: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[3]/div/item-status/div/div[1]/div[1]/b/span'
    last_price: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[3]/div/item-status/div/div[1]/div[2]/b'
    price_condition: str = '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[2]/div[2]/div'
    def subpath(src: str, dest: str):
        rel_path = dest.replace(src, '')
        if rel_path[0] == '[':
            rel_path = rel_path[2:rel_path.index(']')]
        return '.' + rel_path


def try_load_element(driver: WebDriver, xpath: str):

    # Load element with timeout set to x seconds

    element = None
    try:
        element = WebDriverWait(driver, timeout).until(
            ec.presence_of_element_located((By.XPATH, xpath))
        )
    finally:
        return element if element is not None else None


def try_load_elements(driver: WebDriver, xpath: str):

    # Load element with timeout set to x seconds

    elements = []
    try:
        WebDriverWait(driver, timeout).until(
            ec.presence_of_element_located((By.XPATH, xpath))
        )
        elements = driver.find_elements(By.XPATH, xpath)
    finally:
        return elements


class SeleniumScraper:

    auctions: list[Listing]
    listings: list[Listing]
    filtered_listings: list[Listing]
    my_listings: list[Listing]
    driver: webdriver.firefox.webdriver.WebDriver
    auction_filters: list[str]
    item_filters: list[str]

    def __init__(self):

        # Init variables

        self.auctions = []
        self.listings = []
        self.filtered_listings = []
        self.my_listings = []
        self.auction_filters = []
        self.item_filters = []

    def create_driver(self, debug):
        options = FirefoxOptions()
        if not debug:
            options.add_argument("--headless")
        self.driver = webdriver.Firefox(options=options)

    def check_new_auctions(self):
        new_auctions: list[Listing] = self.get_auctions()
        new_auctions = self.filter_auctions(new_auctions)
        self.auctions.append(new_auctions)

    def get_auctions(self):

        new_auctions: list[Listing] = []
        old_auctions: list[str] = []

        # Get url

        if not hasattr(self, 'driver'):
            self.create_driver(False)

        self.driver.get("https://www.onlineliquidationauction.com/")

        # Grab all auction elements

        auction_elements = try_load_elements(self.driver, URLS.auctions)
        print("\nFound {num} auctions: ".format(num=len(auction_elements)))

        # Get data into Listing class from each auction

        for i in auction_elements:

            # Grab name

            name = i.find_element(By.XPATH, URLS.subpath(URLS.auctions, URLS.auction_name)).text
            print(name)

            # Get url and swap domain with bidding page url, keep ID

            bad_url = 'https://www.onlineliquidationauction.com/auctions/detail/bw'
            good_url = 'https://bid.onlineliquidationauction.com/bid/'
            url = i.find_element(By.XPATH, URLS.subpath(URLS.auctions, URLS.auction_name)).get_attribute("href") \
                .replace(bad_url, good_url)
            print(url)

            # Get image src url and save, not really needed

            img_url = [i.find_element(By.XPATH, URLS.subpath(URLS.auctions, URLS.auction_img)).get_attribute('src')]
            print(img_url)

            # Add to auctions list

            is_new_auction = True
            for auction in self.auctions:
                if auction is not [] and auction.name is name:
                    is_new_auction = False
            if is_new_auction:
                new_auctions.append(Listing(name, url, img_url, None, None, None, None))
            else:
                old_auctions.append(name)


        # Cleanup

        for auction in self.auctions:
            if auction.name not in old_auctions:
                self.auctions.remove(auction)

        return new_auctions

    def filter_auctions(self, auctions: list[Listing]):

        # Iterate through every auction and check for filter terms in name

        remove = []
        for i in auctions:
            for j in self.auction_filters:
                if j in i.name:
                    remove.append(i)

        # Remove every item chosen to be removed

        for i in remove:
            if i in auctions:
                auctions.remove(i)

        return auctions

    def get_items(self, auctions: [Listing]):

        # For each auction, does not care if filtered or not

        for auction in self.auctions:

            self.get_auction_items(auction)

        # Save data to file, so we don't need to reload

        f = open('listings.csv', 'w')
        w = csv.writer(f)
        for row in self.listings:
            print(row.name)
            print(row.url)
            for item in row.img_url:
                print(item)
            print(row.end_time.strftime("%m/%d/%Y, %H:%M:%S"))
            print(row.last_price)
            print(row.retail_price)
            print(row.condition)
            w.writerow([row.name, row.url, "*".join(row.img_url), row.end_time.strftime("%m/%d/%Y, %H:%M:%S"),
                        str(row.last_price), str(row.retail_price), row.condition])

    def get_auction_items(self, auction: Listing):

        # Get url

        self.driver.get(auction.url)

        # Set page up and scroll until elements are found

        time.sleep(5)
        names = []

        # TODO: fix this, execute_script does not work

        # self.driver.execute_script("document.body.style.zoom='50%'")

        # need to set to active items only, first load use try_load

        select = try_load_element(self.driver, URLS.select)
        select.find_element(By.XPATH, URLS.subpath(URLS.select, URLS.active_item)).click()

        # Get number of total items to search for, first load call try_load

        count = int(select.find_element(By.XPATH, URLS.subpath(URLS.select, URLS.active_item)).
                    text.replace("All > Active (", "").replace(")", ""))

        if count > 0:

            # Get body element so we can scroll

            try_load_element(self.driver, URLS.first_item)
            body = try_load_element(self.driver, URLS.body)

            print("There are {count} items.".format(count=count))

            # set repeat counter, so we exit if an item is missed but never accounted for

            repeat_counter = REPEAT_INITIAL_VALUE

            while len(names) < count and repeat_counter > 0:

                # Find current active items

                live_items = self.driver.find_elements(By.XPATH, URLS.items)

                for i in live_items:

                    # Get item name text

                    self.get_item_details(i, names)

                # Send page down and delay for a bit

                body.send_keys(Keys.PAGE_DOWN)

                repeat_counter -= 1

                time.sleep(.3)
                print("Found {l_count}/{t_count} listings. ".format(l_count=len(names), t_count=count))

        print("{count} items found. ".format(count=len(names)))

    def get_item_details(self, item: WebDriver, names: []):

        name = try_load_element(item, URLS.subpath(URLS.items, URLS.name)).text

        # If we have not already added this item to our item list

        if name not in names:

            # reset counter if new info

            repeat_counter = REPEAT_INITIAL_VALUE

            # TODO: fill out pricing and end date
            # Set name

            # name = name
            print(name)

            # Set listing url

            url = try_load_element(item, URLS.subpath(URLS.items, URLS.listing_url)).get_attribute("href")
            print(url)

            # Set src image urls

            img_url = []
            img_elements = try_load_elements(item, URLS.subpath(URLS.items, URLS.img_elements))
            for element in img_elements:
                img_url.append(try_load_element(element, URLS.subpath(URLS.img_elements,
                                                                      URLS.img_src)).get_attribute(
                    'owl-data-src'))
                print(img_url[-1])

            # Set date by splitting formatted date into elements it could be; a unit with 0 left is hidden.

            date_text = try_load_element(item, URLS.subpath(URLS.items, URLS.date)).text. \
                split(' ')
            if 'Ends' in date_text:
                date_text.remove('Ends')
                time_left = datetime.now()
                for segment in date_text:
                    if 'd' in segment:
                        time_left += timedelta(days=datetime.strptime(segment, '%dd').day)
                    elif 'h' in segment:
                        time_left += timedelta(hours=datetime.strptime(segment, '%Hh').hour)
                    elif 'm' in segment:
                        time_left += timedelta(minutes=datetime.strptime(segment, '%Mm').minute)
                    elif 's' in segment:
                        time_left += timedelta(seconds=datetime.strptime(segment, '%Ss').second)
                end_time = time_left
            else:
                end_time = datetime.now()
            print("End Date is {date}".format(date=end_time))

            # Set last price

            last_price = float(try_load_element(i, URLS.subpath(URLS.items, URLS.last_price)).
                               text.replace('[$', '').replace(']', ''))
            print("Last price is {price}".format(price=last_price))

            # Set retail price and condition text

            # TODO: FINISH THIS

            price_condition_text = try_load_element(i,
                                                    URLS.subpath(URLS.items, URLS.price_condition)).text
            words = price_condition_text.replace("Retail Price: ", "").split(" ")
            if 'Unknown' not in words[0]:
                retail_price = float(words[0].replace(',', '').replace('$', ''))
            else:
                retail_price = -1
            condition = ' '.join(words[1::])
            print("Retail price is {price}".format(price=retail_price))
            print("Condition is {condition}".format(condition=condition))

            # Add names to found list

            self.listings.append(
                Listing(name, url, img_url, end_time, last_price, retail_price, condition))
            names.append(name)

    def read_listings(self, f: Iterable[str]):

        if os.path.isfile('listings.csv'):
            f = open('listings.csv', 'r')
            r = csv.reader(f, delimiter=',')
            for row in r:
                self.listings.append(Listing(row[0], row[1], row[2].split("*"),
                                             datetime.strptime(row[3], "%m/%d/%Y, %H:%M:%S"),
                                             float(row[4]), float(row[5]), row[6]))
            f.close()

    def read_my_listings(self, f: Iterable[str]):

        if os.path.isfile('mylistings.csv'):
            f = open('mylistings.csv', 'r')
            r = csv.reader(f, delimiter=',')
            for row in r:
                self.listings.append(Listing(row[0], row[1], row[2].split("*"),
                                             datetime.strptime(row[3], "%m/%d/%Y, %H:%M:%S"),
                                             float(row[4]), float(row[5]), row[6]))
            f.close()

    def filter_items(self):

        # Find each listing that matches a keyword

        remove = []
        for i in self.listings:
            for j in self.item_filters:
                if j.lower() in i.name.lower():
                    print("\033[91mRemoving {name} from list\033[0m".format(name=i.name))
                    remove.append(i)

        # Remove items that match keywords

        self.filtered_listings = self.listings.copy()
        for i in remove:
            if i in self.filtered_listings:
                self.filtered_listings.remove(i)
        print("Keeping {num} listings. ".format(num=len(self.listings)))

    def refresh(self):

        self.get_auctions()
        self.filter_auctions()
        self.filter_items()

    def close_driver(self):
        if self.driver is not None:
            self.driver.close()


scraper = SeleniumScraper()
scraper.__init__()
scraper.create_driver(True)
while True:
    scraper.check_new_auctions()
