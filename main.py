#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from bs4 import BeautifulSoup
import sys, time, os, MySQLdb, threading, argparse

services = []

def get_cli_arguements():
  parser = argparse.ArgumentParser(description='Facebook Business Scraper - https://github.com/Garindan/facebook-business-scraper/')
  parser.add_argument('-l', '--location', required=False, type=str, help="Provide a target location (i.e. Flordia or Miami, Flordia")
  parser.add_argument('-m', '--mode', required=True, type=str, help="Gather business pages for associated services (gather) or try to get contact information for pages in table (get)")
  parser.add_argument('-s', '--scroll', required=False, type=int, help="Page result scroll limit (i.e. 1000 - the higher the limit the more results you could obtain) which aids in memory management")
  parser.add_argument('-t', '--threads', required=False, type=int, help="Provide the number of threads you'd like to use for getting contact information on pages (i.e. 20)")
  parser.add_argument('--services', required=False, type=str, help="Define a custom service list file (i.e. services.txt)")
  parser.add_argument('-ip', '--dbip', required=True, type=str, help="IP address of database (i.e. 127.0.0.1)")
  parser.add_argument('-db', '--database', required=True, type=str, help="Provide database name")
  parser.add_argument('--dbuser', required=True, type=str, help="Provide user login name for the database")
  parser.add_argument('--dbpasswd', required=True, type=str, help="Provide user login password for the database")
  parser.add_argument('--fbuser', required=False, type=str, help="Provide your facebook Username")
  parser.add_argument('--fbpasswd', required=False, type=str, help="Provide your facebook Username")
  return parser.parse_args()

location = get_cli_arguements().location
mode = get_cli_arguements().mode
scroll = get_cli_arguements().scroll
servicefile = get_cli_arguements().services
dbip = get_cli_arguements().dbip
database = get_cli_arguements().database
dbuser = get_cli_arguements().dbuser
dbpasswd = get_cli_arguements().dbpasswd
fbuser = get_cli_arguements().fbuser
fbpasswd = get_cli_arguements().fbpasswd
threads = get_cli_arguements().threads

if servicefile:
  with open(servicefile, 'r') as file:
    for line in file:
      services.append(line)

if mode == "get":
  if not threads:
    print "[! - Error] You must supply the number of threads you'd like to use (i.e. '--threads 20')"
    raise Exception('Number of threads not provided')
elif mode == "gather":
  if not fbuser:
    print "[! - Error] You must provide the facebook email you're going to use (i.e. '--fbuser example@hotmail.com')"
    raise Exception('Facebook username not provided')
  if not fbpass:
    print "[! - Error] You must provide the facebook password you're going to use (i.e. '--fbpasswd examplepass')"
    raise Exception('Facebook password not provided')
  if not scroll:
    print "[! - Error] You must provide the number of scrolls to perform (i.e. '--scroll 10')"
    raise Exception('Scroll count not provided')
	
class Browser():
  def __init__(self, UserAgent):
    options = []
    options.append('--ignore-ssl-errors=true')
    options.append('--ssl-protocol=any')
    capabilities = dict(DesiredCapabilities.PHANTOMJS)
    capabilities["phantomjs.page.settings.userAgent"] = UserAgent
    self.driver = webdriver.PhantomJS(desired_capabilities=capabilities, service_args=options)
    self.driver.set_page_load_timeout(30)
    self.driver.implicitly_wait(20)

  def get_page(self, url):
    self.driver.get(url)

    if url == "https://www.facebook.com":
      print "[! - Informative] Visiting Facebook's Home Page: " + url
      return
    elif url == "https://www.facebook.com/services":
      print "[! - Informative] Gathering Facebook's Service Categories: " + url
    elif "https://www.facebook.com/search/pages/?q=" in url:
      lastHeight = self.driver.execute_script("return document.body.scrollHeight")
      i = 0
      while True:
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1.5)
        # Memory Usage Limit (Number of results to display)
        if i >= scroll:
          print "[! - Informative] Breaking loop as max scroll count has been reached"
          break
        newHeight = self.driver.execute_script("return document.body.scrollHeight")
        if newHeight == lastHeight:
          break
        lastHeight = newHeight
        i += 1
        print "[! - Informative] Page scroll number - " + str(i)
    elif "/about" in url:
      name_elem = self.driver.find_element_by_class_name("_2wma")
      html = self.driver.page_source
      try:
        return name_elem.text, html
      except:
        return "Blank Name-", "Blank Page"
        pass

    html = self.driver.page_source
    return html

  def login(self, email, password):
    self.get_page("https://www.facebook.com")
    username = self.driver.find_element_by_name('email')
    username.send_keys(email)
    passwd = self.driver.find_element_by_name('pass')
    passwd.send_keys(password)
    passwd.send_keys(Keys.RETURN)
    time.sleep(5)
    if self.driver.title == "Facebook":
      print '[! - Success] Successfully logged into Facebook'

  def __flush__(self):
    self.driver.delete_all_cookies()
    os.system("rm -rf /tmp/.com*")
    os.system("rm -rf /tmp/.org*")

  def __del__(self):
    self.__flush__()
    self.driver.quit()

class Database:
  host = dbip
  user = dbuser
  password = dbpasswd
  db = database

  def __init__(self):
    self.connection = MySQLdb.connect(self.host, self.user, self.password, self.db)
    self.cursor = self.connection.cursor()

  def insert(self, query):
    try:
      self.cursor.execute(query)
      self.connection.commit()
    except:
      self.connection.rollback()

  def query(self, query):
    cursor = self.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(query)

    return cursor.fetchall()

  def __del__(self):
    self.connection.close()


def run_in_thread(func, func_args=[]):
  if threading.activeCount() > threads: time.sleep(5)
  lock = threading.Lock()
  class MyThread(threading.Thread):
    def run(self):
      with lock:
        func(*func_args)
  MyThread().start()

def get_business_page(service, browser):
  db = Database()
  link_list = []

  print '[! - Informative] Gathering Facebook business information for ' + service
  html = browser.get_page("https://www.facebook.com/search/pages/?q=" + service + " in " + location)
  soup = BeautifulSoup(html, 'html.parser')
  raw_links = soup.find('div',attrs={'id':'contentArea'}).findAll('a', href=True)

  for link in raw_links:
    if link.has_attr('href'):
      link = link['href']
      if "/?ref=br_rs" in link:
        link_list.append(link)

  link_list = set(link_list)

  for link in link_list:
    query = "INSERT INTO `business_pages` (`service`, `page`, `search_location`) VALUES ('" + service + "', '" + link + "', '" + location + "');"
    db.insert(query)

def get_contact_info(row):
  browser = Browser("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36")
  db = Database()
  contact_list = []
  location_list = []
  home_uri = row['page'].strip("?ref=br_rs")
  about_uri = home_uri + "about"
  delete = "delete from business_pages where id = '" + str(row['id']) + "';"

  try:
    about_uri.decode("utf-8")
  except:
    print "[! - Error] Bad encoding found - " + about_uri
    print "[! - Informative] Deleting bad URL encoding from table - ID: " + str(row['id'])
    db.insert(delete)
    return

  try:
    name, html = browser.get_page(about_uri)
  except ValueError:
    print "[! - Error] Incorrect or corrupt page retrieved - " + about_uri
    print "[! - Informative] Deleting bad page - ID: " + str(row['id'])
    db.insert(delete)
    return

  if name == "Blank Name-":
    print "[! - Error] Bad page found - " + about_uri
    print "[! - Informative] Deleting bad page from table - ID: " + str(row['id'])
    db.insert(delete)
    return

  soup = BeautifulSoup(html, 'html.parser')

  for text in soup.findAll('div',attrs={'class':'_50f4'}):
    contact_list.append(''.join(text.findAll(text=True)))
  for text in soup.findAll('span',attrs={'class':'_50f4'}):
    location_list.append(''.join(text.findAll(text=True)))

  for info in contact_list:
    if "Call" in info:
      call = info.strip("Call ")
    elif "http:" in info:
      http = info
    elif "@" in info:
      email = info

  for loc in location_list:
    if row['search_location'] in loc:
      business_location = loc

  try:
    # Remove any potential insert error's
    name = name.replace("'", "")
    name = name.replace('"', '')
    if not business_location:
      print "[! - Error] Business location does not match - " + about_uri
      print "[! - Informative] Deleting bad page from table - ID: " + str(row['id'])
      db.insert(delete)
      return
    else:
      print "[! - Informative] Updating table row with name and business location - ID: " + str(row['id'])
      db.insert("UPDATE business_pages SET location='" + business_location + "', name='" + name + "' where id='" + str(row['id']) + "';")
  except:
    print "[! - Error] Business location was not found - " + about_uri
    print "[! - Informative] Deleting bad page from table - ID: " + str(row['id'])
    db.insert(delete)
    return
    pass

  try:
    if call:
      print "[! - Informative] Updating table row with telephone number - ID: " + str(row['id'])
      db.insert("UPDATE business_pages SET phone='" + call + "' where id='" + str(row['id']) + "';")
  except:
    pass

  try:
    if http:
      print "[! - Informative] Updating table row with website - ID: " + str(row['id'])
      db.insert("UPDATE business_pages SET website='" + http + "' where id='" + str(row['id']) + "';")
  except:
    pass

  try:
    if email:
      print "[! - Informative] Updating table row with email - ID: " + str(row['id'])
      db.insert("UPDATE business_pages SET email='" + email + "' where id='" + str(row['id']) + "';")
  except:
    pass

  # Remove all non-location information (Failed to parse physical address as tags are dynamic) - open to contribution ideas
#  bad_tags = ["Home", "About", "Photos", "Instagram", "Twitter", "Videos", "Reviews", "Weather", "Likes", "Mobile Apps", "Contents", "Posts", "Notes", "Livestream", "Events", "Subscribe to Email", "Jobs", "Donate", "YouTube", "Instagram feed", "Milestones", "Contests", "Obituaries", "Poll", "Pinterest"]

#  for bad_tag in bad_tags:
#    while bad_tag in location_list:
#      location_list.remove(bad_tag)

def main():
  browser = Browser("Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36")
  db = Database()

  if mode == "gather":
    browser.login(fbuser, fbpasswd)
    if len(services) == 0:
      html = browser.get_page("https://www.facebook.com/services")
      soup = BeautifulSoup(html, 'html.parser')
      for text in soup.find('div',attrs={'class':'_375g'}).findAll('a'):
        services.append(''.join(text.findAll(text=True)))
      print '[! - Success] Stored All Possible Services'
      print '[! - Informative] Gathering business contact information'
    else:
      print '[! - Informative] Gathering business contact information'
      print '[! - Success] Using externally defined service list'

##### Incase of an error or want to pickup where you left off - Remove already completed tags
#    bad_tags = ["Broadcasting & Media Production", "Entertainment Service", "Graphic Design", "Photographer", "Publisher", "Automotive Customizing", "Automotive Parts & Accessories", "Automotive Repair", "Car Dealership", "Car Parts & Accessories", "Car Wash & Detailing"]

#    for bad_tag in bad_tags:
#      while bad_tag in services:
#        services.remove(bad_tag)

    for service in services:
      get_business_page(service, browser)
	  
  elif mode == "get":
    rows = db.query("select id, service, page, search_location from business_pages where name is NULL;")
    for row in rows:
      run_in_thread(get_contact_info, func_args=[row])

if __name__ == "__main__":
  main()
