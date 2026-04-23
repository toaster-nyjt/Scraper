import requests
import pymupdf
from bs4 import BeautifulSoup
from inc import Incident

URL_PREFIX = "https://www.police.ucsd.edu/docs/reports/callsandarrests/"  
OUTPUT_NAME = "scrapyard"   

# Runs the scraping operation of ALL logs, returns list of Incident objs
def scrap(metal=None):
    # Gets the HTML of the police log website
    url = URL_PREFIX + "Calls_and_Arrests.asp"
    r = requests.get(url)
    if r.status_code != 200:
        print(f"Failed to retrieve HTML of PD website.\nError Code: {r.status_code}")
    else: 
        output = OUTPUT_NAME
        allIncData = []
        if metal == None:
            for URL in getPdfUrlList(r.text):
                try: 
                    downloadToText(URL, output)
                    incList = scrapText(output)
                    allIncData.extend(inc.getData() for inc in incList)
                except Exception as e:
                    print(f"An unknown error occurred while attempting to parse this pdf: {URL}")
        else:
            try: 
                downloadToText(metal, output)
                incList = scrapText(output)
                allIncData.extend(inc.getData() for inc in incList)
            except Exception as e:
                print(f"An unknown error occurred while attempting to parse this pdf: {metal}")
                
        return allIncData
    
# Gets a list of the URLS of all published pdfs
def getPdfUrlList(html):
    pdfUrlList = []
    soup = BeautifulSoup(html, "html.parser") # Makes the HTML into tree of objs
    for optionTag in soup.find_all('option'): # Search doc for tag
        if optionTag.string != "Select Report to View":
            pdfUrl = URL_PREFIX + optionTag['value']
            pdfUrlList.append(pdfUrl)
    return pdfUrlList

# Converts the pdf URL to a text file
def downloadToText(URL, output):
    r = requests.get(URL)
    if r.status_code != 200:
        print(f"Failed to retrieve HTML of {URL}\nError Code: {r.status_code}")
    else:
        with open(output + ".pdf", 'wb') as f:
            f.write(r.content)
        writeFromPdfToTxt(output)

# Converts the local pdf output into a text file
def writeFromPdfToTxt(output):
    with pymupdf.open(output + ".pdf") as doc:
        text = "".join([page.get_text("text", sort=True) for page in doc])
    with open(output + ".txt", "w") as out:
        out.write(text)

# Scraper keywords
incAttrList = ["category", "loc", "date", "time", "summary", "dis"]
reportList = ["", "", "Date Occurred", "Time Occurred", "Summary", "Disposition"]
blacklist1 = ["UCSD POLICE DEPARTMENT", 
            "CRIME AND FIRE LOG/MEDIA BULLETIN", "202"]
blacklist2 = ["Date Reported", "Incident/Case#"]

# Converts the text file into a list of Incidents
def scrapText(output):
    incList = []
    attrIdx = -1
    addLast = True
    
    try:
        # Iterate through lines
        with open(output + ".txt", "r") as f:
            for line in f:
                # Checks for validity of current line and attribute index 
                if (attrIdx == 6):
                    catStr = ''
                    attrIdx = 0
                    incList.append(inc)
                    inc.display()
                    inc = Incident()
                if (line.strip() == blacklist2[0]):
                    addLast = False
                    break
                if (line[0].isspace() and any(word in line for word in blacklist1)):
                    continue
                if any(word in line for word in blacklist2):
                    continue
                if (line.strip() == ""):
                    continue
                if (attrIdx == -1):
                    catStr =''
                    attrIdx = 0
                    inc = Incident()
                if (attrIdx == 4 and not(line[0].isspace() or line.find(reportList[4]) == 0)):
                    setattr(inc, incAttrList[attrIdx], 
                            (lineStr.split(":")[1].strip() if ":" in lineStr else lineStr))
                    attrIdx += 1

                # Sets the attribute of the inc obj depending on current data proptery
                if (attrIdx == 0):
                    catStr += scrapTextHelper(line.strip())
                    if (not scrapTextHelper(line.strip()).endswith("/")):
                        setattr(inc, incAttrList[attrIdx], catStr)
                        attrIdx += 1
                elif (attrIdx == 1):
                    setattr(inc, incAttrList[attrIdx], scrapTextHelper(line.strip()))
                    attrIdx += 1
                elif (attrIdx == 2 or attrIdx == 3):
                    setattr(inc, incAttrList[attrIdx], line.split(reportList[attrIdx])[1].strip())
                    attrIdx += 1
                elif (attrIdx == 4 and line.find(reportList[attrIdx]) == 0):
                    lineStr = line.split(reportList[attrIdx])[1].strip()
                    lineStr = scrapTextHelper(lineStr)
                elif (attrIdx == 4 and line[0].isspace()):
                    lineStr += " " + line.split(blacklist1[0])[0].strip()
                    lineStr = scrapTextHelper(lineStr)
                elif (attrIdx == 5):
                    lineStr = line.split(reportList[attrIdx])[1].strip()
                    lineStr = scrapTextHelper(lineStr)
                    setattr(inc, incAttrList[attrIdx], 
                            lineStr.split(":")[1].strip() if ":" in lineStr else lineStr)
                    attrIdx += 1
                
            #Add last incident
            if addLast: incList.append(inc)

    except Exception as e:
        print("Exception occured in the middle of a document proccess")
    
    # Reset default time    
    Incident.isPM = False

    return incList

# Helper funtion to scrapText 
def scrapTextHelper(str):
    for word in blacklist1:
        if blacklist1[2] in str:
            str = ""
        str = str.split(word)[0]
    return str.strip()

