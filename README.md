# Facebook Business Scraper for Marketing

A **Facebook scraper** for business intelligence by targeted location. This python scraper can assist in driving various campaigns if you engage in Business-to-Business (B2B) marketing with the following constraint:

![Sample of Marketing Business Data](https://github.com/Garindan/facebook-business-scraper/raw/master/Sample%20Data.png)

> You will need to follow Facebook's Terms of Service (ToS), and applicable laws in your region. I or we take no responsibility for the use of this tool.

### Resources
***
<div align="center" id="resources">
<img alt="Project Icon" src="https://github.com/Garindan/facebook-business-scraper/raw/master/Project%20Icon.png"><br>

Website - <a href="https://www.jussive.com" alt="Local SEO Service">https://www.jussive.com</a> | Blog - <a href="https://www.jussive.com/b" alt="SEO & SEM Blog">https://www.jussive.com/b</a>
</div><br>

<p align="left">This project is provided to you by Jussive. A local business SEO provider who offers SEO for Google, Managed Hosting, and Website Development options to revise or create content which improves search rates.</p>

### Installation
***
####Debian and Ubuntu

**System Packages**

Install all required system packages if not already installed

`apt-get update && apt-get upgrade -y; apt-get install python python-pip python-mysqldb ca-certificates git -y`

**Python Library's**

Install all required Python libraries if not already installed

`pip install argparse selenium bs4`

**Simple PhantomJS Installation**

Download the latest PhantomJS package and extract

`cd /tmp; wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2; tar xvfj phantomjs-2.1.1-linux-x86_64.tar.bz2`

Cleanup and create symbolic links

`rm -rf /tmp/phantomjs-*.tar.bz2; mv phantomjs-2.1.1-linux-x86_64 /opt/phantomjs; ln -sf /opt/phantomjs/bin/phantomjs /usr/local/bin`

**MySQL Installation and Configuration**

Install and Configure MySQL

`apt-get install mysql-server mysql-client`

Connect to the database server

`mysql -u root -p`

Create a database to utilize

`CREATE DATABASE Facebook;`

Create the table utilized to store data

`CREATE TABLE Facebook.business_pages (
id INT NOT NULL AUTO_INCREMENT,
service VARCHAR(250),
page VARCHAR(250),
name VARCHAR(250),
search_location VARCHAR(250),
location VARCHAR(250),
website VARCHAR(250),
phone VARCHAR(250),
email VARCHAR(250),
PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;`

Exit the MySQL prompt

`exit;`

**Web scraper**

Install the Facebook web scraper

`cd /opt; git clone https://github.com/Garindan/facebook-business-scraper/`

### Usage
***

####Modes of Operation

The Facebook business scraper comes with two modes of operation (gather or get) which is specified via the command line argument '-m' or '--mode'. 

##### Gather

The '**gather**' mode scrapes information for a specific location and service ('-l Miami, Florida' or -'--location Florida'), and stores the Facebook business page in the database for processing. 

Notes: _Facebook may rate limit you for using this method, and providing another account should fix any issues if you start getting minimal results. Should the script error out or stop producing redefine your service lists to include only results you have not processed to avoid database duplicates. Do not forget that you need to comply with Facebook's ToS._

**Mode: 'gather' Usage Notes**

A custom service list can be defined by using '--services services.txt' or the script will try to gather all business information for every associated service available. The services file should contain one service per line (the default services.txt file contains all possible services) if utilized.

The scroll page command line argument is meant to set memory limitations or to deliver fast results. You'll get  a connection refused if all the available RAM / Memory is used. Typically, you will not need to scroll over 2,000 times for one service if it is for a state.

Facebook authentication is required for scraping data in this mode

**Mode: 'gather' Usage Example**

`python /opt/facebook-business-scraper/main.py --location Florida --mode gather --scroll 10 --services "/opt/facebook-business-scraper/services.txt" --dbip 127.0.0.1 --database Facebook --dbuser root --dbpasswd examplepass --fbuser example@hotmail.com --fbpasswd examplepass`

##### Get

The second mode of operation is '**get**', and it will go through all information in the database that has not yet been processed to retrieve business contact information. Database entries that do match your previous search location or cannot be parsed by name will be deleted.

Note: _Again, if you get a connection refused you're likely running to many threads for the amount of resources you can utilize (CPU, Memory, and Bandwidth).There will be some pages that may not be able to be processed, and you can delete these bad pages in the table by running the following MySQL statement:_

`DELETE FROM Facebook.business_pages WHERE name IS NONE;`

**Mode: 'get' Usage Notes**

This mode of operation is multi-threaded, and you should be conscious of your resource limitations (CPU and Network Bandwidth). I recommend running only 10 threads until you know your limitations (i.e. '--threads 10'), and would run this two to three times to ensure you've processed all the information you can before deleting bad pages as described above.

**Mode: 'get' Usage Example**

`python /opt/facebook-business-scraper/main.py --mode get --threads 10 --dbip 127.0.0.1 --database Facebook --dbuser root --dbpasswd examplepass`

####General Usage Information

`# python /opt/facebook-business-scraper/main.py -h`

<div id="usage">
usage: usage: main.py [-h] [-l LOCATION] -m MODE [-s SCROLL] [-t THREADS]<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[--services SERVICES] -ip DBIP -db DATABASE --dbuser DBUSER<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; --dbpasswd DBPASSWD [--fbuser FBUSER] [--fbpasswd FBPASSWD]<br><br>

Facebook Business Scraper - https://github.com/Garindan/facebook-business-scraper

_optional arguments_:<br>
&nbsp;&nbsp; -h, --help<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; show this help message and exit<br>
&nbsp;&nbsp; -l LOCATION, --location LOCATION<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Provide a target location (i.e. Flordia or Miami, Flordia)<br>
&nbsp;&nbsp; -m MODE, --mode MODE<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Gather business pages for associated services (gather) or try to get contact information for pages in table (get)<br>
&nbsp;&nbsp; -s SCROLL, --scroll SCROLL<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Page result scroll limit (i.e. 1000 - the higher the limit the more results you could obtain) which aids in memory management<br>
&nbsp;&nbsp; -t THREADS, --threads THREADS<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Provide the number of threads you'd like to use for getting contact information on pages (i.e. 20)<br>
&nbsp;&nbsp; --services SERVICES  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Define a custom service list file (i.e. services.txt)<br>
&nbsp;&nbsp; -ip DATABASE_IP, --dbip DATABASE_IP<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; IP address of database (i.e. 127.0.0.1)<br>
&nbsp;&nbsp; -db DATABASE, --database DATABASE<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Provide database name<br>
&nbsp;&nbsp; --dbuser DATABASE_USER<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Provide user login name for the database<br>
&nbsp;&nbsp; --dbpasswd DATABASE_PASSWD<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Provide user login password for the database<br>
&nbsp;&nbsp; --fbuser FACEBOOK_USER<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Provide your facebook Username<br>
&nbsp;&nbsp; --fbpasswd FACEBOOK_PASSWD<br>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Provide your facebook Username<br>
<div>
