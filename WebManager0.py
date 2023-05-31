from datetime import datetime, timedelta
import time
import selenium.webdriver.firefox.webdriver
from attr import dataclass
from selenium.webdriver import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
import csv
import ManagerBase
from selenium import webdriver
from selenium.webdriver.common.by import By


@dataclass
class Listing:
    name: str
    url: str
    img_url: list[str]
    end_time: datetime
    last_price: float
    retail_price: float


def try_load_element(driver: selenium.webdriver.firefox.webdriver.WebDriver, xpath: str):
    # Load element with timeout set to x seconds
    timeout = 10
    element = WebDriverWait(driver, timeout).until(
        ec.presence_of_element_located((By.XPATH, xpath))
    )
    return element



class WebManager0(ManagerBase.ManagerBase):

    def __init__(self):
        self.manager_name = "WebManager0"
        super().__init__()
        self.auctions = []
        self.listings = []

    def dispose(self):
        super().dispose()
        # self.driver.close()

    def get_auctions(self):
        super().get_auctions()
        driver = webdriver.Firefox()
        driver.get("https://www.onlineliquidationauction.com/")
        # row blog margin-bottom-40 //*[@id="main-content-top"]/div/div[1]/div[1]
        auction_elements = driver.find_elements(By.XPATH, './html/body/div[2]/div[5]/div/div[1]/div')
        print("\nFound {num} auctions: ".format(num=len(auction_elements)))
        for i in auction_elements:
            name = i.find_element(By.XPATH, "./div[2]/h2/a").text
            print(name)
            bad_url = 'https://www.onlineliquidationauction.com/auctions/detail/bw'
            good_url = 'https://bid.onlineliquidationauction.com/bid/'
            url = i.find_element(By.XPATH, "./div[2]/h2/a").get_attribute("href").replace(bad_url, good_url)
            print(url)
            img_url = [i.find_element(By.XPATH, "./div[1]/div/div/div/div/div/a/img").get_attribute('src')]
            print(img_url)
            self.auctions.append(Listing(name, url, img_url, None, None, None))
        driver.close()
        print()

    def filter_auctions(self, auctions_to_remove: list[str]):
        super().filter_auctions(auctions_to_remove)
        remove = []
        for i in self.auctions:
            for j in auctions_to_remove:
                # print("Checking for '{loc}' in ({auction})".format(loc=j, auction=i.name))
                if j in i.name:
                    print("\033[91mRemoving {name} from list\033[0m".format(name=i.name))
                    remove.append(i)
        for i in remove:
            if i in self.auctions:
                self.auctions.remove(i)
        print("Keeping {num} auctions. ".format(num=len(self.auctions)))

    def get_items_raw(self, is_my_items: bool):

        # top level console output

        super().get_items_raw(is_my_items)

        # For each auction, does not care if filtered or not

        for auction in self.auctions:

            # Create new Selenium driver per auction at its url

            auction_driver = webdriver.Firefox()
            auction_driver.get(auction.url)

            # Set page up and scroll until elements are found

            time.sleep(5)
            names = []

            # TODO: fix this, execute_script does not work

            auction_driver.execute_script("document.body.style.zoom='50%'")

            # need to set to active items only, first load use try_load

            select = try_load_element(auction_driver, '/html/body/div[3]/div[3]/div/div/div[2]/div[3]/select')
            select.find_element(By.XPATH, './optgroup[2]/option[2]').click()

            # Get body element so we can scroll

            try_load_element(auction_driver, '/html/body/div[3]/div[3]/div/div/div[2]/div[4]/div/div[2]/item-result/div/div[1]/div/div/div/a')
            body = try_load_element(auction_driver, '//*[@id="all-items"]')

            # Get number of total items to search for, first load call try_load

            count = int(
                try_load_element(auction_driver, '//*[@id="many-items"]/div[3]/select/optgroup[2]/option[2]').text.replace(
                    "All > Active (", "").replace(")", ""))
            print("There are {count} items.".format(count=count))
            while len(names) < count:

                # Find current active items

                live_items = auction_driver.find_elements(By.TAG_NAME, 'item-result')

                for i in live_items:

                    # Get item name text

                    name = try_load_element(i, "./div/div/div/div/div/a").text

                    # If we have not already added this item to our item list

                    if name not in names:

                        # TODO: fill out pricing and end date
                        # Set name

                        # name = name
                        print(name)

                        # Set listing url

                        url = try_load_element(i, "./div/div/div/div/div/a").get_attribute("href")
                        print(url)

                        # Set src image urls

                        img_url = []
                        img_elements = i.find_elements(By.XPATH, "./div/div[2]/div/owl-carousel/div/div/div/div")
                        for element in img_elements:
                            img_url.append(element.get_attribute('src'))

                        # Set date by splitting formatted date into elements it could be; a unit with 0 left is hidden.

                        date_text = try_load_element(i, './div/div[3]/div/item-status/div/div[1]/div[1]/b/span').text.split(' ')
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

                        last_price = float(try_load_element(i, './div/div[3]/div/item-status/div/div[1]/div[2]/b').text.replace('[$', '').replace(']', ''))
                        print("Last price is {price}".format(price=last_price))

                        # Set retail price

                        # TODO: FINISH THIS
                        retail_price = float(try_load_element(i, './div/div[3]/div/item-status/div/div[1]/div[2]/b').text.replace('[$', '').replace(']', ''))
                        print("Last price is {price}".format(price=last_price))

                        # Add names to found list

                        self.listings.append(Listing(name, url, img_url, end_time, last_price, retail_price))
                        names.append(name)

                # Send page down and delay for a bit

                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(.2)
                print("Found {l_count}/{t_count} listings. ".format(l_count=len(self.listings), t_count=len(names)))

            # Cleanup driver

            print("{count} items found. ".format(count=len(names)))
            auction_driver.close()

            # Save data to file, so we don't need to reload

            with open('listings.csv', 'w') as f:
                w = csv.writer(f)
                for row in self.listings:
                    w.writerow([row.name, row.url, row.img_url, row.end_time, row.last_price, row.retail_price])
            f.close()

    def load_from_file(self):
        super().load_from_file()

        with open('listings.csv', "r") as f:
            r = csv.reader(f, delimiter=',')
            for row in r:
                self.listings.append(Listing(row[0], row[1], row[2], row[3], row[4], row[5]))
        f.close()

    def filter_items(self, keywords_to_filter: list[str]):
        super().filter_items(keywords_to_filter)
        remove = []
        for i in self.listings:
            for j in keywords_to_filter:
                # print("Checking for '{loc}' in ({listing})".format(loc=j, listing=i.name))
                if j.lower() in i.name.lower():
                    print("\033[91mRemoving {name} from list\033[0m".format(name=i.name))
                    remove.append(i)
        for i in remove:
            if i in self.listings:
                self.listings.remove(i)
        print("Keeping {num} listings. ".format(num=len(self.listings)))

    def refresh_items(self):
        super().refresh_items()
