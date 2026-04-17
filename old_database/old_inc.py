from datetime import datetime

class Incident():
    isPM = False

    def __init__(self):
        self.loc = None
        self._time = None
        self._date = None
        self.category = None
        self._summary = None
        self.dis = None

    @staticmethod
    def getIsPM(sTime):
        if (sTime[-2:] == "AM"):
            Incident.isPM = False
        elif (sTime[-2:] == "PM"):
            Incident.isPM = True
        return Incident.isPM
    
    @property
    def summary(self):
        return self._summary
    
    @summary.setter
    def summary(self, value):
        if (value == ""): 
            self._summary = None
        else:
            self._summary = value

    @property
    def date(self):
        return self._date
    
    @date.setter
    def date(self, value):
        try:
            dateStr = value.split("-")[0].strip()

            if (len(dateStr[dateStr.rindex("/") + 1:]) == 2):
                dateStr = "".join([dateStr[:dateStr.rindex("/") + 1], "20", 
                                   dateStr[dateStr.rindex("/") + 1:]])
                
            self._date = datetime.strptime(dateStr, "%m/%d/%Y").date()
        except ValueError:
            self._date = None
 
    @property
    def time(self):
        return self._time

    @time.setter
    def time(self, value):
        try: 
            strippedTime = value.split("-")[0].strip()
            isPM = Incident.getIsPM(strippedTime)

            if (strippedTime[-2:] not in ("AM", "PM")):
                strippedTime += ("PM" if isPM else "AM")
            if (strippedTime[-3:][0] != " "):
                strippedTime = "".join([strippedTime[:-2], " ", strippedTime[-2:]])

            self._time = datetime.strptime(strippedTime, "%I:%M %p").time()
        except ValueError:
            self._time = None

    def getData(self):
        formatDate = self.date.strftime("%B %d, %Y") if self.date else None
        formatTime = self.time.strftime("%I:%M %p") if self.time else None
        return self.category, self.loc, formatDate, formatTime, self.summary, self.dis
    
    def display(self):
        print(f"Time: {self.time}\nDate: {self.date}\nCategory: {self.category}")
        print(f"Location: {self.loc}\nSummary: {self.summary}\nDisposition: {self.dis}\n")




    

