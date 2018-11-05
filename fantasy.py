import requests
import pandas as pd
from datetime import date

"""
TODO:
0.  Compare rosters of other teams from a week ago, just show difference between categories, with and without bench
1.  Load rosters from yahoo API
2.  Clean up, add parameters
"""

class Player():
	@staticmethod
	def create_player(person_id, display_name_comma, display_name, roster_status, from_year, to_year, player_code, team_id, team_city, team_name, team_abr, team_code, games_played):
		return Player(display_name_comma, team_id, team_city, player_code, person_id, games_played)


	def __init__(self, name, team_id, team_city, player_code, person_id, games_played):
		self.name = name
		self.team_id = team_id
		self.team_city = team_city
		self.player_code = player_code
		self.person_id = person_id
		self.games_played = games_played


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36', "Upgrade-Insecure-Requests": "1","DNT": "1","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language": "en-US,en;q=0.5","Accept-Encoding": "gzip, deflate"}
base = 'https://stats.nba.com/stats/commonallplayers'
params = {
	'LeagueID':'00',
	'Season':'2018-19',
	'IsOnlyCurrentSeason':1
}

r = requests.get(base, headers=headers, params=params)
player_data = r.json()['resultSets'][0]['rowSet']

players = {}
for data in player_data:
	p = Player.create_player(*data)
	players[p.player_code] = p

fantasy_team = [
	'ben_simmons',
	'damyean_dotson',
	'russell_westbrook',
	'joe_harris',
	'ersan_ilyasova',
	'zach_collins',
	'clint_capela',
	'rudy_gobert',
	'tj_warren',
	'draymond_green'
	]

week_start = pd.Timestamp(2018, 10, 29)
week_end = pd.Timestamp(2018, 11, 4)

# categories interested in
categories = [
	'points',
	'rebounds',
	'assists',
	'field_goal_percentage',
	'free_throw_percentage',
	'steals',
	'blocks',
	'turnovers',
	'three_pointers'
]

player_games = {}
all_games = []

for p in fantasy_team:
	params = {
		'playerid':players[p].person_id,
		'season':'2018-19',
		'seasontype':'Regular Season'
	}

	r = requests.get(
		'https://stats.nba.com/stats/playergamelog',
		headers=headers,
		params=params
	)

	# TODO: Validate response code
	response = r.json()['resultSets']
	game_log = response[0]['rowSet']

	df = pd.DataFrame(game_log)
	df.columns = response[0]['headers']

	# drop unneeded columns
	drop_cols = ['SEASON_ID', 'Player_ID', 'Game_ID', 'MATCHUP', 'WL', 'MIN', 'FG_PCT', 'FG3A', 'FG3_PCT', 'FT_PCT', 'OREB', 'DREB', 'PF', 'PLUS_MINUS', 'VIDEO_AVAILABLE']
	df = df.drop(columns=drop_cols)

	# filter data frame by date
	df['GAME_DATE'] = pd.to_datetime(df['GAME_DATE'], format='%b %d, %Y')
	df = df[(df['GAME_DATE'] >= week_start) & (df['GAME_DATE'] <= week_end)]
	df = df.drop(columns='GAME_DATE')
	all_games.append(df)
	player_games[p] = df

df = pd.concat(all_games)

# prints out sum for the week
tot = df.sum()
tot['FGP'] = tot['FGM']/tot['FGA']*1000
tot['FTP'] = tot['FTM']/tot['FTA']*1000
print(tot)