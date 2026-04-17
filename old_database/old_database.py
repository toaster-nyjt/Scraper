# IMPORTANT: DELETE PDWatch.db INSIDE old_database BEFORE RUNNING SETUP
# OR THE DATA WILL BE DUPLICATED

from datetime import datetime
import sqlite3
import requests
import scraper

DATABASE = "PDWatch.db"

# Sets everything up
def setup():
    data = scraper.scrap()
    urls = getURLs()

    # maximizes sqlite performance
    with sqlite3.connect(DATABASE, timeout=30) as con:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA cache_size=10000")
        con.execute("PRAGMA synchronous=NORMAL")  
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS Incidents (
                Category,
                Location,
                Date,
                Time,
                Summary,
                Disposition
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS PDFs (
                Url,
                Date
            )
        """)

        # populate PDF table
        for url in urls:
            cur.execute("INSERT INTO PDFs VALUES(?, ?)", (url, getDate(url)))

        # populate Incidents table
        cur.executemany("INSERT INTO Incidents VALUES(?, ?, ?, ?, ?, ?)", data)

# Scans the website and updates databases accordingly
def updateDatabase():
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    URLs = getURLs()
    res = cur.execute("SELECT Url FROM PDFs").fetchall()
    change = 0

    for url in URLs:
        if (url,) not in res:
            addUrl(url)
            print("Added: " + url)
            change += 1

    print(f"{change} new PDFs have been added")
    con.close()

# Adds the incidents to the incident table and the pdf url to the pdf table
def addUrl(url):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    data = scraper.scrap(url)
    date = getDate(url)

    if "UPDATE" in url:
        print("Update!") 
        cur.execute("""UPDATE PDFs
                    SET Url = ?
                    WHERE Date = ?
                    """, (url, date))
        cur.execute("""DELETE FROM Incidents
                    WHERE Date = ?
                    """, (date,))
    else:
        cur.execute("INSERT INTO PDFs VALUES(?, ?)", (url, date))

    filtered_data = (tuple for tuple in data if tuple[2] == date)
    cur.executemany("INSERT INTO Incidents VALUES(?, ?, ?, ?, ?, ?)", filtered_data)
    con.commit()
    con.close()

# Parses the date of a URL
def getDate(url):
    url = url[url.rindex("/") + 1:url.rindex(".pdf")].strip()
    if "UPDATED" in url:
        url = url[:url.index("UPDATED")].strip()
    url = url.replace("%20"," ").strip()
    parsed = datetime.strptime(url, "%B %d, %Y")  
    result = parsed.strftime("%B %d, %Y")
    return result

# Gets the list of URLS from the website
def getURLs():
    return scraper.getPdfUrlList(requests.get(scraper.URL_PREFIX + "Calls_and_Arrests.asp").text)