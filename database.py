from datetime import datetime
from dotenv import load_dotenv
import os
import psycopg2
import requests
import scraper

# Loads the env into os env variable for security
load_dotenv("database_key.env")
key = os.environ["DIRECT_URL"]

# Sets everything up
def setup():
    data = scraper.scrap()
    urls = getURLs()

    with psycopg2.connect(key) as con:
        with con.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS Incidents (
                    id          SERIAL PRIMARY KEY,
                    Category    TEXT,   
                    Location    TEXT,
                    Date        DATE,
                    Time        TIME,
                    Summary     TEXT,
                    Disposition TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS PDFs (
                    id      SERIAL PRIMARY KEY,
                    Url     TEXT,
                    Date    DATE
                )
            """)

            # populate PDF table
            for url in urls:
                cur.execute("INSERT INTO PDFs (Url, Date) VALUES(%s, %s)", (url, getDate(url)))

            # populate Incidents table
            cur.executemany("INSERT INTO Incidents (Category, Location, Date, Time, Summary, Disposition) " \
            "VALUES(%s, %s, %s, %s, %s, %s)", data)

# Scans the website and updates databases accordingly
def updateDatabase():
    URLs = getURLs()

    with psycopg2.connect(key) as con:
        with con.cursor() as cur:
            cur.execute("SELECT Url FROM PDFs")
            res = cur.fetchall()
            change = 0

            for url in URLs:
                if (url,) not in res:
                    addUrl(url)
                    print("Added: " + url)
                    change += 1

            print(f"{change} new PDFs have been added")

# Adds the incidents to the incident table and the pdf url to the pdf table
def addUrl(url):
    data = scraper.scrap(url)
    date = getDate(url)

    with psycopg2.connect(key) as con:
        with con.cursor() as cur:

            if "UPDATE" in url:
                print("Update!") 
                cur.execute("""UPDATE PDFs
                            SET Url = %s
                            WHERE Date = %s
                            """, (url, date))
                cur.execute("""DELETE FROM Incidents
                            WHERE Date = %s
                            """, (date,))
                data = (row for row in data if row[2] == date)
            else:
                cur.execute("INSERT INTO PDFs (Url, Date) VALUES(%s, %s)", (url, date))

            cur.executemany("INSERT INTO Incidents (Category, Location, Date, Time, Summary, Disposition) " \
            "VALUES(%s, %s, %s, %s, %s, %s)", data)

# Parses the date of a URL
def getDate(url):
    url = url[url.rindex("/") + 1:url.rindex(".pdf")].strip()
    if "UPDATED" in url:
        url = url[:url.index("UPDATED")].strip()
    url = url.replace("%20"," ").strip()
    parsed = datetime.strptime(url, "%B %d, %Y")  
    result = parsed.strftime("%Y-%m-%d")
    return result

# Gets the list of URLS from the website
def getURLs():
    return scraper.getPdfUrlList(requests.get(scraper.URL_PREFIX + "Calls_and_Arrests.asp").text)