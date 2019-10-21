from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains as AC
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options 

class Advertisement:
    def __init__(self, browser, link='', make='', model=''):
        self.hyperlink = link
        self.browser = browser
        self.browser.get(self.hyperlink)

        wait = WebDriverWait(self.browser,10)
        wait.until(EC.visibility_of_element_located((By.XPATH, '//ul[@class="key-specifications"]')))
        
        #get the list of necessary data
        self.key_specifications = self.browser.find_element_by_xpath('//ul[@class="key-specifications"]').text.split('\n')
        self.basic_check = self.get_basic_check()
        self.eco = self.get_eco()
        
        #Check if the eco variable list contain much information (the co2emission is at index 19)
        if len(self.eco) < 19:
            self.eco += [0 for x in range(20-len(self.eco))]
        
        self.description = self.browser.find_element_by_xpath('//h1[@class="advert-heading__title atc-type-insignia atc-type-insignia--medium"]').text
        self.seller_type = self.get_seller_type()
        self.price = int(self.browser.find_element_by_xpath('//span[@class="advert-price__cash-price"]').text[1:].replace(',', ''))
        self.make = make
        self.model = model
        self.year = int(self.key_specifications[0][:4])
        self.mileage = int(self.key_specifications[2].strip(' miles').replace(',', ''))
        self.body_style = self.key_specifications[1]
        self.co2emission = self.get_co2emission()
        self.doors = int(self.key_specifications[6].strip('doors '))
        self.transmission_type = self.key_specifications[4]
        self.get_basic_data()
        
        
    def get_basic_data(self):
        if len(self.basic_check) > 3:
            self.was_stolen = False if self.basic_check[self.basic_check.index('Stolen')+1] == 'Clear' else True
            self.was_write_off = False if self.basic_check[7] == 'Clear' else True
            self.was_scrapped = False if self.basic_check[self.basic_check.index('Scrapped')+1] == 'Clear' else True
        else:
            self.was_stolen = 'N/A'
            self.was_write_off = 'N/A'
            self.was_scrapped = 'N/A'            
        self.engine_size = self.key_specifications[3].strip('L')
        self.fuel_type = self.key_specifications[5]

        
    def get_seller_type(self):
        self.seller = self.browser.find_element_by_xpath('//p[@class="seller-name atc-type-toledo atc-type-toledo--medium"]').get_attribute('innerText')
        return 'Private' if 'Private' in self.seller else 'Dealer'

        
    def get_co2emission(self):
        if self.eco[19] == 0:
            return 'N/A'
        co_emision_id = self.eco.index('CO₂ emissions')
        return self.eco[co_emision_id+1].strip('g/km')

        
    def get_basic_check(self):
        try:
            return self.browser.find_element_by_xpath('//div[@class="basic-check-m"]').text.split('\n')
        except:
            return [] 
            
            
    def get_eco(self):
        try:
            return browser.find_element_by_xpath('//ul[@class="info-list tech-specs__info-list"]').get_attribute('innerText').split('\n')
        except:
            return [0 for x in range(20)]
    
    
    def to_string(self):
        return "Hyperlink: {0}, Description: {1}" \
        "Seller Type: {2}, Price: {3}" \
        "Make: {4}, Model: {5}," \
        "Year: {6}, Mileage: {7}," \
        "Body Style: {8}, Co2 Emissions: {9}," \
        "Doors: {10}, Transmission: {11}," \
        "Was Stolen: {12}, Was Write Off: {13}, " \
        "Was Scrapped: {14}," \
        "Engine Size: {15}, Fuel Type: {16}".format(
            self.hyperlink, self.description,
            self.seller_type, self.price,
            self.make, self.model,
            self.year, self.mileage,
            self.body_style, self.co2emission,
            self.doors, self.transmission_type,
            self.was_stolen, self.was_write_off,
            self.was_scrapped,
            self.engine_size, self.fuel_type)

            
BASE_URL = "https://www.autotrader.co.uk"
POSTCODE = 'PO16+7GZ'
browser = webdriver.Chrome(executable_path='chromedriver.exe')
CSV_FILE = 'atuk_makes_and_models.csv'


def get_address(MAKE, MODEL):
    return f"{BASE_URL}/car-search?advertising-location=at_cars&" \
           f"price-search-type=total-price&search-target=usedcars&" \
           f"postcode={POSTCODE}&make={MAKE}&model={MODEL}&"
           

def get_ads_links(link, listing, search_total):
    links = [listing[ids].find_element_by_tag_name('a').get_attribute('href') for ids in range(len(listing))] 
    n = 1
    while len(links) < search_total:
        n += 1
        browser.get(link+f'page={n}')
        listing = browser.find_elements_by_xpath('//li[@class="search-page__result"]')
        links += [listing[ids].find_element_by_tag_name('a').get_attribute('href') for ids in range(len(listing))] 
    return links


def write_to_file(ads_data):
    file = open('data.csv', 'a')      
    file.write(f"{ads_data.hyperlink},{ads_data.description.replace(',','|')}," \
           f'{ads_data.seller_type},{ads_data.price},' \
           f'{ads_data.make},{ads_data.model},' \
           f'{ads_data.year},{ads_data.mileage},' \
           f'{ads_data.body_style},{ads_data.co2emission},' \
           f'{ads_data.doors},{ads_data.transmission_type},' \
           f'{ads_data.was_stolen},{ads_data.was_write_off},' \
           f'{ads_data.was_scrapped},' \
           f'{ads_data.engine_size},{ads_data.fuel_type}\n')    
           
           
def main(car_data, write=False):
    for data in open(CSV_FILE):
        data = data.split(',')
        MAKE = data[0]
        MODEL = data[1]
        print(f'searching {MAKE} {MODEL}')
        SEARCH_BY_MAKE_AND_MODEL_URL = get_address(MAKE, MODEL)     
        browser.get(SEARCH_BY_MAKE_AND_MODEL_URL)
        browser.set_window_size(1900, 800)
        
        search_total = int(browser.find_element_by_xpath('//h1[@class="search-form__count js-results-count"]').get_attribute('innerText').strip('cars found'))
        listing = browser.find_elements_by_xpath('//li[@class="search-page__result"]')
        links = get_ads_links(SEARCH_BY_MAKE_AND_MODEL_URL, listing, search_total)
      
        car_data[MAKE] = car_data.get(MAKE, {})
        car_data[MAKE][MODEL] = {}

        for ids, ads in enumerate(links):
            ads_data = Advertisement(browser, link=ads, make=MAKE, model=MODEL)
            
            #This is example what to do with the data i choose to make dict variable and write to csv file
            car_data[MAKE][MODEL][ids] = ads_data
            if write:
                write_to_file(ads_data)
            

if __name__ == '__main__':
    car_data = {}
    main(car_data, True)