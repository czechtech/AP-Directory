from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import logging, sys, time

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

# Create headless web browser
logging.info("Creating Chrome browser")
chrome_options = Options()
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
driver.implicitly_wait(15)

# Login Page:
logging.info("Loading https://account.collegeboard.org/login/login...")
driver.get("https://account.collegeboard.org/login/login")
username = driver.find_element_by_name('person.userName')
password = driver.find_element_by_name('person.password')
print("Login to https://account.collegeboard.org/login/login")
username.send_keys(raw_input("Username: "))
password.send_keys(raw_input("Password: "))
driver.find_element_by_id('loginForm').submit()

# AP Community Members List
logging.info("Loading AP Community...")
driver.get("https://apcommunity.collegeboard.org/group/apcsp/")
time.sleep(6)
driver.find_element_by_link_text("Members").click()
logging.info("Loading AP Community Members Page...")
next_page_lst = [driver.find_element_by_link_text("All")]

member_urls = {}

# Open URL Output File
filename = "ap-member-urls.csv"
print("Writing to "+filename)
file = open(filename, 'a') # 'w' to start a new file each time
file.write("URL,Course/s\n")

# For each page, parse each row
while len(next_page_lst) > 0:
    next_page_lst[0].click()
    time.sleep(2)
    page = int(driver.find_element_by_class_name("ap-page-strong").text)
    print("Page: "+str(page))
    row_count = len(driver.find_elements_by_xpath("//tr[contains(@class, 'data-table-row')]"))
    for r in range(1,row_count):
        url        = driver.find_element_by_xpath("//tr[contains(@class, 'data-table-row')]["+str(r)+"]/td[1]//a").get_attribute("href")
        first_name = driver.find_element_by_xpath("//tr[contains(@class, 'data-table-row')]["+str(r)+"]/td[2]").text
        last_name  = driver.find_element_by_xpath("//tr[contains(@class, 'data-table-row')]["+str(r)+"]/td[3]").text
        school     = driver.find_element_by_xpath("//tr[contains(@class, 'data-table-row')]["+str(r)+"]/td[5]").text
        course     = driver.find_element_by_xpath("//tr[contains(@class, 'data-table-row')]["+str(r)+"]/td[6]").text
        member_urls[url] = course
        file.write('"'+url+'","'+course+'"\n')
        file.flush()
    next_page_lst = driver.find_elements_by_link_text("Next")

# Close URL file
file.close()


# Re-read urls & course/s back in to be able to resume processing
member_urls = {}
filename = "ap-member-urls.csv"
print("Reloading "+filename+"...")
with open(filename) as file:
    next(file)
    for line in file:
        url = line.split(',', 1)[0][1:-1]
        course = line.split(',', 1)[1][1:-2]
        if len(course) == 0:
            course = '""'
        member_urls[url] = course
file.close()


# Open Schools Output File
filename = "ap-schools.csv"
print("Writing to "+filename)
file = open(filename, 'w')
file.write("Location,Subject,School,URL,Name,Position\n")


def separate_school_location(school):
    if "(" in school:
        p = school.find("(")
        return school[:p-1], school[p+1:-1]
    return school, ""

def trim_subject(subject):
    if "Computer Science Principles" in subject and "Computer Science A" in subject:
        return "Computer Science Principles & Computer Science A"
    if "Computer Science A" in subject:
        return "Computer Science A"
    if "Computer Science Principles" in subject:
        return "Computer Science Principles"

driver.implicitly_wait(5)

# For each url
for url in member_urls.keys():
    subject = member_urls[url]
    if "Computer Science" in subject:
        #logging.info("Loading "+url+"...")
        print(url)
        driver.get(url)
        subject  = trim_subject(subject)
        try:
            name     = driver.find_element_by_class_name("ap-user-profile-heading").text[:-10]
            title    = driver.find_element_by_name("jobTitle").text
            school   = driver.find_element_by_name("school").text
            school, location = separate_school_location(school)
            file.write('"'+location+'",')
            file.write('"'+subject+'",')
            file.write('"'+school+'",')
            file.write('"'+url+'",')
            file.write('"'+name+'",')
            file.write('"'+title+'"\n')
            file.flush()
        except NoSuchElementException:
            logging.info("Problem with "+url)

file.close()

driver.quit()

# https://chrome.google.com/webstore/detail/geocode-by-awesome-table/cnhboknahecjdnlkjnlodacdjelippfg?utm_source=permalink
# https://www.google.com/earth/outreach/learn/visualize-your-data-on-a-custom-map-using-google-my-maps/
