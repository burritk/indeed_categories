import traceback
from selenium.common.exceptions import NoSuchElementException
import sqlite3
import sys
from pyscraper.selenium_utils import get_headed_driver, wait_for_xpath, get_headless_driver
conn = sqlite3.connect('indeed.db')
cur = conn.cursor()
try:
    if sys.argv[1] == 'create':
        cur.execute('CREATE TABLE PRODUCT (title text, description text, category text, link text, keyword text)')
except: pass
query = 'INSERT INTO PRODUCT values(?, ?, ?, ?, ?)'
driver = get_headless_driver(no_sandbox=True)
results = []
with open('indeed_categories.txt', 'r') as input_file:
    for line in input_file:
        matches = []
        counter = 10
        keyword_index = 0
        found = False
        while True:
            if len(matches) % 100 == 0 and len(matches) != 0 and found:
                keyword_index += 1
                found = False
                counter = 0
            category = line.split(':')[1]
            keywords = line.split(':')[0].split(',')
            keywords_formatted = [word.replace(' ', '+') for word in keywords]
            # for keyword in keywords:
            try:
                kw = keywords[keyword_index].strip()
            except:
                print len(matches)
                break
            driver.get('https://www.indeed.com/jobs?q={0}&start={1}'.format(kw, str(counter)))
            counter += 10
            listings = []
            listings.extend(driver.find_elements_by_xpath('//div[@class="row result clickcard"]'))
            listings.append(driver.find_element_by_xpath('//div[@class="lastRow row result clickcard"]'))
            for listing in listings:
                name = listing.find_element_by_xpath('./h2/a')
                link = name.get_attribute('href')
                if kw in name.text:
                    if len(matches) % 100 == 0 and len(matches) != 0 and found:
                        break
                    found = True
                    matches.append((link, category, kw))

            if len(matches) == len(keywords) * 100:
                break
        break


    for link, category, keyword in matches:
        driver.get(link)
        title = driver.find_element_by_xpath('//b[@class="jobtitle"]').text
        description = driver.find_element_by_xpath('//*[@id="job_summary"]').text
        cur.execute(query, (title, description, category, link, keyword))
        conn.commit()

