This is the scraper tool that can connect to a PostgreSQL database (or hosted
locally through SQLite3 if running from old_database), populate it with all 
police reports from the UCSD police department log website (typically the past 
60 days worth of logs), and contains an update function to scan the website 
for new logs.