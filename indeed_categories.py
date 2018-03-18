import traceback
from selenium.common.exceptions import NoSuchElementException
import sqlite3
import sys

from selenium.webdriver.common.keys import Keys

from pyscraper.selenium_utils import get_headed_driver, wait_for_xpath, get_headless_driver
conn = sqlite3.connect('indeed.db')
cur = conn.cursor()
# cur.execute('CREATE TABLE RESUME (category text, keyword text, title text, name text, location text, summary text, resume text, link text)')
try:
    if sys.argv[1] == 'create':
        cur.execute('CREATE TABLE RESUME (category text, keyword text, title text, name text, location text, summary text, resume text, link text)')
except: pass
query = 'INSERT INTO RESUME values(?, ?, ?, ?, ?, ?, ?, ?)'
driver = get_headed_driver()
results = []
# driver.get('https://secure.indeed.com/account/login?')
# email = driver.find_element_by_xpath('//*[@id="signin_email"]')
# password = driver.find_element_by_xpath('//*[@id="signin_password"]')
# email.send_keys('julian.gabus.downloads@gmail.com')
# password.send_keys('safarijuli')
# password.send_keys(Keys.ENTER)
with open('indeed_categories.txt', 'r') as input_file:
    print 'Scanning'
    matches = []
    for line in input_file:
        counter = 0
        keyword_index = 0
        found = False
        keyword_counter = 0
        print
        while True:
            try:
                if keyword_counter == 100:
                    try:
                        print keywords[keyword_index] + ' to ' + keywords[keyword_index + 1]
                    except:
                        print keywords[keyword_index] + ' Done. Changing category...'
                    keyword_index += 1
                    keyword_counter = 0
                    found = False
                    counter = 0
                category = line.split(':')[1]
                keywords = line.split(':')[0].split(',')
                try:
                    kw = keywords[keyword_index].strip()
                except:
                    print
                    print len(matches), keyword_index
                    break
                driver.get('https://www.indeed.com/resumes?q={0}&co=US&start={1}'.format(kw, str(counter)))
                # driver.get('https://www.indeed.com/jobs?q={0}&filter=0&start={1}'.format(kw, str(counter)))
                counter += 50
                listings = driver.find_elements_by_xpath('//*[@id="results"]/li')
                for listing in listings:
                    name = listing.find_element_by_xpath('./div/div[2]/div/a')
                    link = name.get_attribute('href')
                    name = name.text
                    experience = [l.text.split('-')[0] for l in listing.find_elements_by_class_name('experience')]
                    education = [l.text.split('-')[0] for l in listing.find_elements_by_class_name('education')]
                    for exp in experience:
                        if kw in exp:
                            if keyword_counter == 100:
                                break
                            found = True
                            matches.append((link, category, kw, exp))
                            keyword_counter += 1
                            break

                # if len(matches) == len(keywords) * 100:
                #     break

                page_links = driver.find_element_by_id('pagination').find_elements_by_tag_name('a')
                next_button = page_links[-1]
                if 'next' not in next_button.text.lower():
                    try:
                        print keywords[keyword_index] + ' to ' + keywords[keyword_index + 1]
                    except:
                        print keywords[keyword_index] + ' Done. Changing category...'
                    keyword_counter = 0
                    keyword_index += 1
                    counter = 0
                    continue

                print len(matches),
            except:
                traceback.print_exc()
                continue
        break


    for link, category, keyword, experience in matches:
        try:
            driver.get(link)
            resume = driver.find_element_by_xpath('//*[@id="resume_body"]')

            title = experience
            try: name = resume.find_element_by_id('resume-contact').text
            except: name = ''
            try: location = resume.find_element_by_id('headline_location').text
            except: location = ''
            try: summary = resume.find_element_by_id('res_summary').text
            except: summary = ''
            resume_text = resume.text
            cur.execute(query, (category, keyword, title, name, location, summary, resume_text, link))
            conn.commit()
        except:
            traceback.print_exc()
            continue
