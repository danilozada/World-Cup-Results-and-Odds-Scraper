# Import packages
import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np
import datetime
import pycountry_convert as pc

## Read in Excel file

# Get sheet names
sheets = pd.ExcelFile('WorldCupOdds.xlsx').sheet_names

# Open existing odds, add implied probabilities and save new excel file
writer = pd.ExcelWriter('NewWorldCupOdds.xlsx')
for s in sheets:
    df = pd.read_excel('WorldCupOdds.xlsx', s)
    df['HomeImpliedOdds'] = np.NaN
    df['AwayImpliedOdds'] = np.NaN
    df['TieImpliedOdds'] = np.NaN
    df['SumOdds'] = np.NaN
    df['HomeConfederation'] = np.NaN
    df['AwayConfederation'] = np.NaN
    for x in range(len(df)):
        t = df['Date'][x].strftime('%Y-%m-%d')
        new_t = datetime.datetime.strptime(t,'%Y-%m-%d').date()
        df['Date'][x] = new_t
        if df['HomeOdds'][x] > 0:
            home_implied_prob = 1 / ((df['HomeOdds'][x] / 100) + 1)
        if df['HomeOdds'][x] < 0:
            home_implied_prob = 1 / (1 + 100 / (abs(df['HomeOdds'][x])))
        if df['AwayOdds'][x] > 0:
            away_implied_prob = 1 / ((df['AwayOdds'][x] / 100) + 1)
        if df['AwayOdds'][x] < 0:
            away_implied_prob = 1 / (1 + 100 / (abs(df['AwayOdds'][x])))
        if df['TieOdds'][x] > 0:
            tie_implied_prob = 1 / ((df['TieOdds'][x] / 100) + 1)
        if df['TieOdds'][x] < 0:
            tie_implied_prob = 1 / (1 + 100 / (abs(df['TieOdds'][x])))
        implied_sum = home_implied_prob + away_implied_prob + tie_implied_prob
        home_prob = home_implied_prob / implied_sum
        away_prob = away_implied_prob / implied_sum
        tie_prob = tie_implied_prob / implied_sum
        sum_prob = round(home_prob + away_prob + tie_prob, 2)

        df['HomeImpliedOdds'][x] = home_prob * 100
        df['AwayImpliedOdds'][x] = away_prob * 100
        df['TieImpliedOdds'][x] = tie_prob * 100
        df['SumOdds'][x] = sum_prob * 100

        if np.isnan(df['HomeOdds'][x]):
            df['HomeImpliedOdds'][x] = np.NaN
            df['AwayImpliedOdds'][x] = np.NaN
            df['TieImpliedOdds'][x] = np.NaN
            df['SumOdds'][x] = np.NaN
        a_team = df['AwayTeam'][x]
        h_team = df['HomeTeam'][x]
        teams = [h_team, a_team]
        for team in teams:
            try:
                a = pc.map_countries()[team]
                if a:
                    country_alpha2 = pc.country_name_to_country_alpha2(team)
                    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
                    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
            except:
                if team == 'USA':
                    country_continent_name = 'North America'
                if team == 'England':
                    country_continent_name = 'Europe'
                if team == 'Serbia and Montenegro':
                    country_continent_name = 'Europe'
            if team == h_team:
                if country_continent_name == 'Europe':
                    df['HomeConfederation'][x] = 'UEFA'
                if country_continent_name == 'North America':
                    df['HomeConfederation'][x] = 'CONCACAF'
                if country_continent_name == 'South America':
                    df['HomeConfederation'][x] = 'CONMOBEL'
                if country_continent_name == 'Africa':
                    df['HomeConfederation'][x] = 'CAF'
                if country_continent_name == 'Asia':
                    df['HomeConfederation'][x] = 'AFC'
                if country_continent_name == 'Oceania':
                    df['HomeConfederation'][x] = 'OFC'
            if team == a_team:
                if country_continent_name == 'Europe':
                    df['AwayConfederation'][x] = 'UEFA'
                if country_continent_name == 'North America':
                    df['AwayConfederation'][x] = 'CONCACAF'
                if country_continent_name == 'South America':
                    df['AwayConfederation'][x] = 'CONMOBEL'
                if country_continent_name == 'Africa':
                    df['AwayConfederation'][x] = 'CAF'
                if country_continent_name == 'Asia':
                    df['AwayConfederation'][x] = 'AFC'
                if country_continent_name == 'Oceania':
                    df['AwayConfederation'][x] = 'OFC'

        if a_team == 'Australia':
            df['AwayConfederation'][x] = 'AFC'
        if h_team == 'Australia':
            df['HomeConfederation'][x] = 'AFC'
    df.to_excel(writer, sheet_name=s, index = False)
writer.save()



































