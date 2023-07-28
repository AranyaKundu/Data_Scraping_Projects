import requests, json, datetime, pandas as pd

t1 = datetime.datetime.now() # get current time

# Thanks to "https://stackoverflow.com/questions/61950709/trying-to-extract-football-data"
def extract_data():
    # store stats to extract
    stat_types = ['goals', 'outfielder_block', 'touches', 'goal_assist', 'appearances', 'clean_sheet', 
                 'mins_played', 'yellow_card', 'red_card', 'total_pass', 'big_chance_missed', 'total_offside', 
                 'total_tackle', 'fouls', 'dispossessed', 'total_clearance']
    
    # create dataframes for final data
    final_2021 = pd.DataFrame(columns = ['Name', 'date_of_birth'])
    final_2020 = pd.DataFrame(columns = ['Name', 'date_of_birth'])
    
    dfs_final = [final_2020, final_2021] # create list to dynamically change dataframes while looping
    filename = ["stats_2020.csv", "stats_2021.csv"] # Create csv file names
    
    # Create empty dataframes for storing data before merging
    temp_df_2020 = pd.DataFrame()
    temp_df_2021 = pd.DataFrame()
    dfs_temp = [temp_df_2020, temp_df_2021] # create list to dynamically change dataframes while looping
    
    seasons = [363, 418] # save season numbers to update the links
    
    # enumerate through season to dynamically change dataframes
    for season_idx, season in enumerate(seasons):
        # loop through all stat types
        for stat in stat_types:
            dfs_temp[season_idx] = pd.DataFrame(columns = ['Name', 'date_of_birth', stat])
            url = f"https://footballapi.pulselive.com/football/stats/ranked/players/{stat}?page=0&pageSize=20&compSeasons={season}&comps=1&compCodeForActivePlayer=EN_PR&altIds=true"
            response = requests.get(url, headers = {"origin": "https://www.premierleague.com"})
            data = response.json()
            # loop through all pages for any particular stat_type
            for i in range(data['stats']['pageInfo']['numPages']):
                url = f"https://footballapi.pulselive.com/football/stats/ranked/players/{stat}?page={i}&pageSize=20&compSeasons={season}&comps=1&compCodeForActivePlayer=EN_PR&altIds=true"
                response = requests.get(url, headers = {'origin': 'https://www.premierleague.com'})
                data = response.json()
                # loop through each element in any page 
                for j in range(len(data['stats']['content'])):
                    dob = datetime.datetime.fromtimestamp(data['stats']['content'][j]['owner']['birth']['date']['millis']/ 1000)
                    format_dob = dob.strftime("%Y-%m-%d")
                    dfs_temp[season_idx].loc[len(dfs_temp[season_idx])] = [data['stats']['content'][j]['owner']['name']['display'], 
                                                                           format_dob, data['stats']['content'][j]['value']]
            # merge data with outer join to ensure no player misses out because of "NA" 
            dfs_final[season_idx] = pd.merge(dfs_final[season_idx], dfs_temp[season_idx], 
                                             on = ['Name', 'date_of_birth'], how = 'outer')
            # replace "NAs" with 0s
            dfs_final[season_idx].fillna(0, inplace = True)
        # save data to a ".csv" file. Change filename dynamically for season
        dfs_final[season_idx].to_csv(filename[season_idx], index = False, encoding = "utf-8")

extract_data() # run the function

# To extract team wise stats
# select teams that played in the season
teams_2020 = [1, 2, 131, 43, 4, 6, 7, 34, 9, 26, 10, 11, 12, 23, 18, 20, 21, 36, 25, 38]
teams_2021 = [1, 2, 131, 43, 4, 6, 7, 26, 9, 10, 11, 12, 23, 20, 21, 25, 38, 130, 33, 14]

temp_df = pd.DataFrame(columns = ['Team', 'stat_name', 'Value'])

def extract_teams_data(teams_list, filename):
    temp_df = pd.DataFrame(columns = ['Team', 'stat_name', 'Value'])
    for team in teams_list:
        url = f"https://footballapi.pulselive.com/football/stats/team/{team}?comps=1&compSeasons=418"
        response = requests.get(url, headers = {"origin": "https://www.premierleague.com"})
        data = response.json()
        for i in range(len(data['stats'])):
            temp_df.loc[len(temp_df)] = [data['entity']['name'], data['stats'][i]['name'], data['stats'][i]['value']]
    final = temp_df.set_index(['Team', 'stat_name']).unstack()
    final.to_csv(f"{filename}.csv", encoding = "utf-8")

# call the functions for both the years
extract_teams_data(teams_2020,  "team_stats_2020")
extract_teams_data(teams_2021,  "team_stats_2021")

timelapsed = datetime.datetime.now() - t1 # get current time
print("Time Elapsed = ", timelapsed) # compute run time 