# import dependencies 
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
from splinter import Browser
import time


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
    browser.is_element_present_by_css("li.slide", wait_time=5)

    
    html = browser.html
    soup = bs(html, 'html.parser')

    # get container for each article 
    results = soup.find('li', class_="slide")

    # get first headline and body 
    headline = results.find('div', class_="content_title").text
    body_teaser = results.find('div', class_="article_teaser_body").text

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
    time.sleep(4)
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
    weather_url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(weather_url)
    browser.is_element_present_by_css("div.css-901oao r-jwli3a r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0", wait_time=5)
    try:
        tweet_html = browser.html
        soup_tweet = bs(tweet_html, 'lxml')

        results = soup_tweet.find('div', class_="css-901oao r-jwli3a r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0")
        time.sleep(3)
        tweet = results.text


        mars_data['tweet'] = tweet
    except:
        pass

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

    # create list to hold hemi 
    hemis_list = []

    # iterate through results to get hemisphere name and image 
    for r in results:
        
        # create dictionary to hold individual hemis
        hemis_dict = {}
        
        # get individual links, visit page and creat bs objects
        info = r.find('a')['href']
        links = ('https://astrogeology.usgs.gov'+info)
        browser.visit(links)
        link_html = browser.html
        soup_link = bs(link_html, 'html.parser')
        
        # get img and title
        img_url = soup_link.find('li').find('a', target='_blank')['href']
        hemi_title = soup_link.find('h2', class_='title').text
        
        # add to dictionary and append dict to list
        hemis_dict['title'] = hemi_title
        hemis_dict['img_url'] = img_url
        hemis_list.append(hemis_dict)
        
        # go back to start process over 
        browser.back()

    # add hemis_dict to mars_data
    mars_data['HemisphereImg'] = hemis_list


    # quit browser
    browser.quit()
    #return results
    return mars_data
    
