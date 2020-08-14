# import dependencies 
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from splinter import Browser


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "/usr/local/bin/chromedriver"}
    return Browser("chrome", **executable_path, headless=False)


def scrape():
    browser = init_browser()

    # creating mars_data dict that will be insterted into mongodb
    mars_data = {}

    # getting headline and body from nasa site
    # save url and use browser to visit site
    url = "https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    browser.visit(url)

    html = browser.html
    soup = bs(html, 'html.parser')

    # git container for each article 
    results = soup.find_all('li', class_="slide")

    # get first headline and body 
    for r in results:
        headline = r.find('div', class_="content_title").text
        body_teaser = r.find('div', class_="article_teaser_body").text

    # add headline and body to mars_data
    mars_data['nasa_headline'] = headline
    mars_data['body_teaser'] = body_teaser

    # getting featured image from space images 
    image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(image_url)

    # create route to get to image page
    # click full image
    click_fi = browser.links.find_by_partial_text('FULL IMAGE')
    click_fi.click()

    # click on more info
    click_mi = browser.links.find_by_partial_text('more info')
    click_mi.click()

    # set up htlm string and beautiful soup object 
    image_html = browser.html
    soup_img = bs(image_html, 'html.parser')

    # get image part of url
    image_url = soup_img.find('figure', class_='lede').find('img')['src']

    # combine img url to get full address
    image_url = f'https://www.jpl.nasa.gov{image_url}'

    # add image_url to mars_data
    mars_data['image_url'] = image_url

    # gettig Mars Weather from twitter 
    ###############################
    ###############################

    # getting Mars Facts
    # set url 
    facts_url = 'https://space-facts.com/mars/'

    # turn data into tables and get wanted table 
    tables = pd.read_html(facts_url)
    df = tables[0]

    # changing column headers, setting information to index
    df.columns = ['Information','Value']
    df.set_index('Information', inplace=True)
    html_table = df.to_html()

    # add df to mars_data
    mars_data['MarsTable'] = html_table

    # getting Mars Hemisphere pictures and titles
    # set url and visit site
    hems_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(hems_url)
    
    # set html string and soup object
    hems_html = browser.html
    soup_hems = bs(hems_html, 'html.parser')

    # set results to iterate through 
    results = soup_hems.find_all('div', class_='item')

    # create dictionary
    hemis_dict = {}

    # iterate through results to get hemisphere name and image 
    for r in results:
        info = r.find('a')['href']
        links = ('https://astrogeology.usgs.gov'+info)
        

        browser.visit(links)
        link_html = browser.html
        soup_link = bs(link_html, 'html.parser')
        img_url = soup_link.find('li').find('a', target='_blank')['href']
        hemi_title = soup_link.find('h2', class_='title').text
        hemis_dict[hemi_title] = img_url
        browser.back()
    
    # add hemis_dict to mars_data
    mars_data['HemisphereImg'] = hemis_dict


    # quit browser
    browser.quit()
    #return results
    return mars_data
    