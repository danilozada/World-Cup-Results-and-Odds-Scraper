# Import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import requests
from bs4 import BeautifulSoup
import datetime
import time

def wc_scraper(year):
    # Original website - designate World Cup year
    base_website = 'https://www.thesoccerworldcups.com/world_cups/{}_results.php'.format(year)

    # Get page data with BeautifulSoup
    page = requests.get(base_website)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Get individual match day data
    match_day = soup.find(attrs={'class': 'fondo'}).find(attrs={'class': 'main-content'}).find_all(attrs=
                                {'class': 'max-1 margen-b8 bb-2'})

    # Create a data frame to append all of the data to
    df = pd.DataFrame(columns=['Date', 'MatchType', 'HomeTeam', 'HomeTeamRegScore', 'AwayTeam', 'AwayTeamRegScore'])

    # Get individual match data
    for match in match_day:
        # Date of match day games
        date = match.find(attrs={'class': 't-enc-2 a-left pad-l20 margen-t0 margen-b0 no-negri'}).text
        date_str = date.split(':')[1].lstrip().rstrip()
        date_format = '%b %d, %Y'
        date_final = datetime.datetime.strptime(date_str, date_format).date()

        # Get individual matches from date
        games = match.find_all(attrs={'class': 'margen-y3 clearfix'})
        for g in games:
            stage = g.find(attrs={'class': 'left a-left wpx-170'}).text
            if 'Group' in stage:
                stage = 'Group Stage'
            if stage == '1/4 Finals':
                stage = 'Quarterfinals'
            if stage == 'Final Game':
                stage = 'Final'

            # Game information
            game_stats = g.find(attrs={'class': 'right-sm a-right'})

            # Home Team
            home_team = game_stats.find(attrs={'class': 'left margen-b2 clearfix'}).text.strip('\n')

            # Away Team
            away_team = game_stats.find(attrs={'class': 'left a-left margen-b2 clearfix'}).text.strip('\n').lstrip().rstrip()

            # Score
            scores = game_stats.find(attrs={'class': 'left a-center margen-b3 clearfix'}).find(attrs={
                'class': 'left wpx-60'}).text.strip('\n')

            # Initial home team score
            home_team_score = int(scores.split('-')[0].lstrip().rstrip())

            # Initial away team score
            away_team_score = int(scores.split('-')[1].lstrip().rstrip())

            # Justify the scores from extra time or penalty kicks
            if stage != 'Group Stage':
                if game_stats.find(attrs=
                                   {'class': 'margen-b3 a-left clearfix d-flex flex-wrap flex-row justify-center'}):
                    et_score = game_stats.find(attrs=
                                               {
                                                   'class': 'margen-b3 a-left clearfix d-flex flex-wrap flex-row justify-center'}).find(
                        attrs={'class': 'left clearfix wpx-80 a-center'}).text.split(' ')
                    home_team_et_score = int(et_score[1])
                    away_team_et_score = int(et_score[3])

                    home_team_score = home_team_score - home_team_et_score
                    away_team_score = away_team_score - away_team_et_score

            # Change names to make scraping odds data easier
            if home_team == 'Holland':
                home_team = 'Netherlands'
            if away_team == 'Holland':
                away_team = 'Netherlands'

            # Combine data
            game_data = [date_final, stage, home_team, home_team_score, away_team, away_team_score]

            # Create dataframe and add to main data frame
            game_df = pd.DataFrame([game_data], columns=df.columns)
            df = pd.concat([df, game_df], ignore_index=True)

    # Add columns for betting odds
    df['HomeOdds'] = np.NaN
    df['TieOdds'] = np.NaN
    df['AwayOdds'] = np.NaN

    # Scrape odds data - first URL
    base_url = 'https://www.oddsportal.com/soccer/world/world-cup-{}/results/'.format(year)

    # 2022 data has different URL
    if year == 2022:
        base_url = 'https://www.oddsportal.com/soccer/world/world-championship-2022/results/'

    # Use Selenium to get data from website
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(base_url)
    WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.CSS_SELECTOR, 'div'))
    time.sleep(10)

    # Make sure that the page scrolls all the way down
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while (match == False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == lenOfPage:
            match = True

    # Get game data
    all_data = driver.find_element(By.XPATH,
                                   '//div[@class = "flex flex-col px-3 text-sm max-mm:px-0"]').find_elements(
        By.XPATH, '//div[@class = "flex flex-col w-full text-xs eventRow"]')

    all_data_text = []

    # Append game data text to variable
    for d in all_data:
        all_data_text.append(d.text)

    driver.quit()

    # Get rid of spacings
    for x in range(len(all_data_text)):
        s = all_data_text[x].split('\n')
        new = ' '.join(s)
        all_data_text[x] = new

    # Get indexes with dates of games
    date_index = [i for i, val in enumerate(all_data_text) if "B's" in all_data_text[i]]
    date_index.append(len(all_data_text))

    # Append groups of games based on date index
    con = []
    for x in np.arange(1, len(date_index)):
        temp = []
        new = np.arange(date_index[x - 1], date_index[x])
        for y in new:
            temp.append(all_data_text[y])
        con.append(temp)

    # Get date, teams and odds from website
    for x in range(len(con)):
        for y in range(len(con[x])):
            date_format = '%d %b %Y'
            if x == 0:
                comp = con[x][y].split(' ')[7:]
                comp = ' '.join(comp)

                # Get date from website header
                date = comp.split('-')[0].lstrip().rstrip()
                date_str = datetime.datetime.strptime(date, date_format).date()

            # Get date from rest of game day entries
            if x != 0 and y == 0:
                comp = con[x][y].split('1 X 2')[0].rstrip().split('-')[0].rstrip()
                date_str = datetime.datetime.strptime(comp, date_format).date()

            # Get game information
            if len(con[x][y].split(':00')) > 1:
                game_info = con[x][y].split(':00')[1][:-2].lstrip().rstrip()
            if len(con[x][y].split(':30')) > 1:
                game_info = con[x][y].split(':30')[1][:-2].lstrip().rstrip()

            # Home team
            home_team = game_info.split('–')[0].rstrip().lstrip()

            # Away team
            away_team_comp = game_info.split('–')[1].rstrip().lstrip()

            # Find index of away team score from total game information
            for s in away_team_comp:
                if s.isnumeric():
                    num_loc = away_team_comp.find(s)
                    break

            # Get away team name using away team score index
            away_team = away_team_comp[:num_loc].lstrip().rstrip().replace('&', 'and')
            home_team = home_team.replace('&', 'and')

            # Get odds
            home_odds = game_info.split(' ')[-3]
            tie_odds = game_info.split(' ')[-2]
            away_odds = game_info.split(' ')[-1]

            if home_odds == '-':
                home_odds = np.NaN
            if away_odds == '-':
                away_odds = np.NaN
            if tie_odds == '-':
                tie_odds = np.NaN


            # If game data matches, add odds information
            for y in range(len(df)):
                if df.loc[y, 'Date'] == date_str and df.loc[y, 'HomeTeam'] == home_team and df.loc[y, 'AwayTeam']:
                    df.loc[y, 'HomeOdds'] = home_odds
                    df.loc[y, 'TieOdds'] = tie_odds
                    df.loc[y, 'AwayOdds'] = away_odds

    # Scrape second page of odds data
    sec_url = 'https://www.oddsportal.com/soccer/world/world-cup-{}/results/#/page/2/'.format(year)

    # 2022 data has different URL
    if year == 2022:
        sec_url = 'https://www.oddsportal.com/soccer/world/world-championship-2022/results/#/page/2/'

    # Use Selenium to get data from website
    service = ChromeService(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get(sec_url)
    WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.CSS_SELECTOR, 'body'))

    # Make sure that the page scrolls all the way down
    lenOfPage = driver.execute_script(
        "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match = False
    while (match == False):
        lastCount = lenOfPage
        time.sleep(3)
        lenOfPage = driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount == lenOfPage:
            match = True

    # Get game data
    all_data = driver.find_element(By.XPATH,
                                   '//div[@class = "flex flex-col px-3 text-sm max-mm:px-0"]').find_elements(
        By.XPATH, '//div[@class = "flex flex-col w-full text-xs eventRow"]')

    all_data_text = []

    # Append game data text to variable
    for xyz in all_data:
        all_data_text.append(xyz.text)

    driver.quit()

    # Get rid of spacings
    for x in range(len(all_data_text)):
        s = all_data_text[x].split('\n')
        new = ' '.join(s)
        all_data_text[x] = new

    # Get indexes with dates of games
    date_index = [i for i, val in enumerate(all_data_text) if "B's" in all_data_text[i]]
    date_index.append(len(all_data_text))

    # Append groups of games based on date index
    con = []
    for x in np.arange(1, len(date_index)):
        temp = []
        new = np.arange(date_index[x - 1], date_index[x])
        for y in new:
            temp.append(all_data_text[y])
        con.append(temp)

    # Get index positions of World Cup matches
    new_it = [0]
    for x in range(len(con)):
        for y in range(len(con[x])):
            date_format = '%d %b %Y'
            if x != 0 and y == 0:
                if 'Qualification' not in con[x][y]:
                    new_it.append(x)

    # Get date, teams and odds from website
    for x in new_it:
        for y in range(len(con[x])):
            date_format = '%d %b %Y'
            if x == 0 and y == 0:
                comp = con[x][y].split(' ')[7:]
                comp = ' '.join(comp)

                # Get date from website header
                date = comp.split("1 X 2 B's")[0].lstrip().rstrip()
                date_str = datetime.datetime.strptime(date, date_format).date()

            # Get date from rest of game day entries
            if x != 0 and y == 0:
                comp = con[x][y].split('1 X 2')[0].rstrip().split('-')[0].rstrip()
                date_str = datetime.datetime.strptime(comp, date_format).date()

            # Get game information
            if len(con[x][y].split(':00')) > 1:
                game_info = con[x][y].split(':00')[1][:-2].lstrip().rstrip()
            if len(con[x][y].split(':30')) > 1:
                game_info = con[x][y].split(':30')[1][:-2].lstrip().rstrip()

            # Home team
            home_team = game_info.split('–')[0].rstrip().lstrip()

            # Away team
            away_team_comp = game_info.split('–')[1].rstrip().lstrip()

            # Find index of away team score from total game information
            for s in away_team_comp:
                if s.isnumeric():
                    num_loc = away_team_comp.find(s)
                    break

            # Get away team name using away team score index
            away_team = away_team_comp[:num_loc].lstrip().rstrip().replace('&', 'and')

            # Get odds
            home_odds = game_info.split(' ')[-3]
            tie_odds = game_info.split(' ')[-2]
            away_odds = game_info.split(' ')[-1]

            # If game data matches, add odds information
            for y in range(len(df)):
                if df.loc[y, 'Date'] == date_str and df.loc[y, 'HomeTeam'] == home_team and df.loc[y, 'AwayTeam']:
                    df.loc[y, 'HomeOdds'] = home_odds
                    df.loc[y, 'TieOdds'] = tie_odds
                    df.loc[y, 'AwayOdds'] = away_odds

    # Change all data frame columns to integers
    df['HomeTeamRegScore'] = df['HomeTeamRegScore'].astype('int')
    df['AwayTeamRegScore'] = df['AwayTeamRegScore'].astype('int')
    df['HomeOdds'] = df['HomeOdds'].astype('float')
    df['AwayOdds'] = df['AwayOdds'].astype('float')
    df['TieOdds'] = df['TieOdds'].astype('float')




    return df

# Germany 2006 World Cup Matches, Results and Odds
germany_wc = wc_scraper(2006)

# South Africa 2010 World Cup Matches, Results and Odds
south_africa_wc = wc_scraper(2010)

# Brazil 2014 World Cup Matches, Results and Odds
brazil_wc = wc_scraper(2014)

# Russia 2018 World Cup Matches, Results and Odds
russia_wc = wc_scraper(2018)

# Qatar 2022 World Cup Matches, Results and Odds
qatar_wc = wc_scraper(2022)

# Write an excel file with each tournament on a different sheet
with pd.ExcelWriter('WorldCupOdds.xlsx') as writer:
    germany_wc.to_excel(writer, sheet_name = 'Germany 2006 WC', index = False)
    south_africa_wc.to_excel(writer, sheet_name = 'South Africa 2010 WC', index=False)
    brazil_wc.to_excel(writer, sheet_name = 'Brazil 2014 WC', index=False)
    russia_wc.to_excel(writer, sheet_name = 'Russia 2018 WC', index = False)
    qatar_wc.to_excel(writer, sheet_name = 'Qatar 2022 WC', index =False)









