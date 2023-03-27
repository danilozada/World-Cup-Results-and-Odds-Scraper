# World-Cup-Results-and-Odds-Scraper
Uses Selenium and BeautifulSoup to scrape thesoccerworldcups.com and oddsportal.com for individual World Cup game results and betting odds. The excel file that gets created using the Scraper_Function.py file is labeled as 'WorldCupOdds.xlsx' and the excel file that gets created after the MoreInfo.py file is labeled 'NewWorldCupOdds.xlsx'.

# Scraper_Function.py
This script has a function that will scrape all individual World Cup game results and betting odds based on the year of the tournament. Thesoccerworldcups.com has results for all World Cup games and oddsportal.com has World Cup betting odds dating back to the 2006 World Cup. The following tournament years could be scraped: 2006, 2010, 2014, 2018 and 2022.

The function will return an excel file with the following information: game date (object), match type (object), home team (object), home team regulation goals (integer), away team (object), away team regulation goals (integer), home betting odds (float), tie betting odds (float), and away team betting odds (float). Oddsportal.com did not have some betting odds and these columns are NaN.

# MoreInfo.py
This script reads in the excel file created from the Scraper_Function.py script. It then calculates the implied odds of the home team winning, a tie, and the away team winning based on the betting odds and creates new columns. Additionally, the FIFA confederation that each team belongs to was also added to the data frame. The following columns were added: home team implied winning odds (float), away team implied winning odds (float), implied tie odds (float), sum of the implied odds (integer), the home confederation (object) and the away confederation (object).









