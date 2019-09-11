# imports
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import pandas as pd
import re
import os

URL = 'https://www.abodo.com'
result_limit = 1 # pages (10 = 200)
postal_codes = ["60603", "60607"]


# main method that calls each individual method
def find_properties(bedrooms=None, bathrooms=None):
    property_list = []
    for code in postal_codes:
        driver = initialize_driver()
        search_for_properties(code, driver)
        filter_and_expand_results(bedrooms, bathrooms, driver)
        url_list= get_links(driver)
        driver.quit()
        property_list.extend(get_property_attributes(url_list))
    return {'properties': property_list}


# goes through a list of URLs and obtains each attribute
def get_property_attributes(url_list):
    property_list = []
    for url in url_list:
        print("Processing property with URL: " + url)

        page = requests.get(url).content
        page_soup = BeautifulSoup(page, 'html.parser')

        # name
        name = page_soup.find('h1', attrs={'itemprop': 'name'})

        if name is not None:
            name = name.getText().strip()
        else:
            name = page_soup.find('h1', attrs={'itemprop': 'streetAddress'})
            if name is not None:
                name = name.getText().strip()
            else:
                # odd edge case that needs further investigation
                name = ""

        # latitude, longitude
        geo = page_soup.find_all('span', attrs={'itemprop': 'geo'})[0]
        latitude = geo.findChildren('meta', attrs={'itemprop': 'latitude'})[0].attrs['content']
        longitude = geo.findChildren('meta', attrs={'itemprop': 'longitude'})[0].attrs['content']

        # location
        location = page_soup.find('span', attrs={'itemprop': 'addressLocality'}).getText().strip()

        # bedrooms
        bedroom_parent = page_soup.find_all('div', attrs={'class': re.compile('^listing-summary-bedrooms.*')})[0]
        bedrooms = bedroom_parent.findChildren('div', {'class': 'listing-summary-detail'})[0].getText() + " " + bedroom_parent.findChildren('div', {'class': 'subtext-label'})[0].getText()

        # bathrooms
        bathroom_parent = page_soup.find_all('div', attrs={'class': re.compile('^listing-summary-bathrooms.*')})[0]
        bathrooms = bathroom_parent.findChildren('div', {'class': 'listing-summary-detail'})[0].getText() + " " + bathroom_parent.findChildren('div', {'class': 'subtext-label'})[0].getText()

        # bedrooms
        size_parent = page_soup.find_all('div', attrs={'class': re.compile('^listing-summary-unit-size.*')})[0]
        size = size_parent.findChildren('div', {'class': 'listing-summary-detail'})[0].getText() + " " + size_parent.findChildren('div', {'class': 'subtext-label'})[0].getText()

        # property details
        details_parent = page_soup.find_all('div', attrs={'id': 'description_tab'})[0]
        details = details_parent.findChildren('div', {'class': 'shortentext'})[0].getText().strip()

        # amenities
        amenities_parent = page_soup.find_all('div', attrs={'class': re.compile('^amenity-group.*')})
        amenities = []
        if len(amenities_parent) > 0:
            amenities_children = amenities_parent[0].findChildren('span', attrs={'class': re.compile('^amenity-element.*')})
            for child in amenities_children:
                title = child.getText().strip()
                amenities.append(title)

        property = {'Property Name': name,
                    'Location': location,
                    'Latitude': latitude,
                    'Longitude': longitude,
                    'Bedrooms': bedrooms,
                    'Bathrooms': bathrooms,
                    'Property Details': details,
                    'Amenities': amenities}

        property_list.append(property)

    return property_list


# Obtains individual links to each property for future processing
def get_links(driver):
    print("Obtaining links")

    page_soup = BeautifulSoup(driver.page_source, 'html.parser')
    page_soup_code = page_soup.find_all('a', href=True, attrs={'class': re.compile('^grid-image-anchor.*')})
    link_list = []
    for a in page_soup_code:
        link_list.append(URL + a['href'])

    return link_list


# Filters and expands the search results
def filter_and_expand_results(bedrooms, bathrooms, driver):
    print("Filtering and expanding results for properties")

    WebDriverWait(driver, 10).until( lambda x: x.find_element_by_xpath('//*[@id="list_holder"]/div[2]/div[2]/a'))

    # open up all filters
    if bedrooms is not None or bathrooms is not None:
        driver.find_element_by_class_name("filter-btn-container").click()
        # wait for screen holder to disappear
        WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="search-loading-screen-holder"]/div[contains(@class, "hidden")]'))

        driver.find_element_by_xpath('//*[@id="main-filters"]/div[2]/div[2]/div/button[10]').click()
        # filter based on bedrooms and bathrooms
        if bedrooms is not None:
            if bedrooms > 8:
                bedrooms = 8
            bedrooms = bedrooms + 1
            bedroom_xpath = '//*[@id="main-filters"]/div[2]/div[2]/div/button[' + str(bedrooms) + ']'
            driver.find_element_by_xpath(bedroom_xpath).click()

        if bathrooms is not None:
            if bathrooms > 4:
                bathrooms = 4
            bathroom_xpath = '//*[@id="baths-btn-group"]/button[' + str(bathrooms) + ']'
            driver.find_element_by_xpath(bathroom_xpath).click()

        driver.find_element_by_xpath('//input[@value="Apply Filters"]').click()

    WebDriverWait(driver, 10).until(lambda x: x.find_element_by_xpath('//*[@id="list_holder"]/div[2]/div[2]/a'))
    load_more_btn = driver.find_element_by_xpath('//*[@id="list_holder"]/div[2]/div[2]/a')

    # expand more results
    for i in range(result_limit):
        load_more_btn.click()


# Search for property using a postal code
def search_for_properties(code, driver):
    print("Searching for property with postal code " + code)

    search_bar = driver.find_element_by_id("google-places-input")
    search_bar.send_keys(code)
    driver.find_element_by_css_selector("div[class^='home-page-search-button']").click()


def initialize_driver():
    driver = webdriver.Chrome()
    driver.get(URL)
    driver.implicitly_wait(10)

    return driver