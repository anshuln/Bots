import json
import praw
import re
import requests
import time

subredditconfigfile = "subredditconfig.json"
platformconfigfile = "platformconfig.json"
userconfigfile = "userconfig.json"	#Contains secret identities
# TODO - filter out playlist posts, save for later
# TODO - can use only certain genres
# TODO refactor for only 1 config file
class MusicSubmission:
	def __init__(self,subreddit,submission):
		subconfig = json.load(open(subredditconfigfile,"r"))[subreddit]
		platformconfig = json.load(open(platformconfigfile,"r"))
		self.parse_title(submission['title'],subconfig)
		self.parse_url(submission['url'],platformconfig)
	def __str__(self):
		str = ("Title : {}\nArtist : {}\n".format(self.title,self.artist))
		if self.genre is not None:
			str+=("Genre : {}\n".format(self.genre))
		return str
	def parse_title(self,title,config):		#TODO refactor to get this information from url
		regexexp = re.compile(config['regex']['expression'])
		groups = config['regex']['groups']
		try:
			match = re.match(regexexp,title)
			title = match.group('title')
			artist = match.group('artist')
			if 'genre' in groups:
				genre = match.group('genre')
			else:
				genre = None	# TODO search for genre somehow
			self.title = title
			self.artist = artist
			self.genre = genre
		except AttributeError:
			print("No match for :",title)
			self.title = None
			self.artist = None
			self.genre = None
	def set_youtube_uid(self,apikey):
		search_query = '{}+by+{}'.format(self.title,self.artist).strip().replace(' ','+')
		print(search_query)
		search_url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={}&key={}'.format(search_query,apikey) 
		result_json = requests.get(search_url,headers={'content-type': 'application/json'}).json()
		id = result_json['items'][0]['id']	#TODO explain this line, may have to remove the hardcoding
		if id['kind'] != 'youtube#video':
			self.youtubeuid = None	#TODO fix this
			print("Currently we only support songs, not albums")
		else:
			self.youtubeuid = id['videoId']

	def set_spotify_uid(self,apikey):
		search_query = 'q={} by {}&type=track'.format(self.title,self.artist).strip().replace(' ','+')	#TODO experiment with artist name etc	
		search_url = "https://api.spotify.com/v1/search?{}&limit=1".format(search_query)
		token = get_spotify_token(apikey)
		headers = {"Authorization":"Bearer {}".format(token)}
		result_json = requests.get(search_url,headers=headers).json()
		try:
			self.spotifyuid = result_json['tracks']['items'][0]['id']	#TODO error handling
		except:
			search_query = 'q={}&type=track'.format(self.title).strip().replace(' ','+')
			search_url = "https://api.spotify.com/v1/search?{}&limit=1".format(search_query)
			result_json = requests.get(search_url,headers=headers).json()
			try:
				self.spotifyuid = result_json['tracks']['items'][0]['id']	#TODO error handling
			except:
				print("No results for {}".format(self.title))
				print(search_url)
				print(result_json)


	def parse_url(self,url,config):
		self.url = url
		self.spotifyuid = None
		self.youtubeuid = None

		youtube_regex = re.compile(config['youtube']['regexexp'])
		spotify_regex = re.compile(config['spotify']['regexexp'])

		ytmatch = re.match(youtube_regex,url)
		spmatch = re.match(spotify_regex,url)

		if ytmatch is not None:
			self.youtubeuid = ytmatch.group('uid')
		elif spmatch is not None:
			self.spotifyuid = spmatch.groups('uid')

		if self.youtubeuid is None:
			apikey = json.load(open(userconfigfile))['youtube_api_key']
			self.set_youtube_uid(apikey)

		if self.spotifyuid is None:
			apikey = json.load(open(userconfigfile))['youtube_api_key']
			self.set_spotify_uid(apikey)

		#TODO parse provided URL to set artist, title etc.

def get_spotify_token(apikey):	#apikey is base64
	userdict = json.load(open(userconfigfile,"r"))
	last_time = userdict['spotify']['access_token']['timestamp']
	if time.time() - last_time < 3600:	# Access tokens valid for 3600 s, TODO remove hard coding
		return userdict['spotify']['access_token']['token']
	token_url = "https://accounts.spotify.com/api/token"
	data = {"grant_type" : "refresh_token", "refresh_token":userdict['spotify']['access_token']['refresh_token']}
	headers = {"Authorization" : "Basic {}".format(apikey)}
	response = requests.post(token_url,data=data,headers=headers)
	print(response.json())
	token = response.json()['access_token']	#TODO error handling
	userdict['spotify']['access_token']['token'] = token
	userdict['spotify']['access_token']['timestamp'] = time.time()
	json.dump(userdict,open(userconfigfile,"w"))
	return token

def deleteAllTracksSpotify(apikey,playlisturi):
	token = get_spotify_token(apikey)
	request_url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlisturi)
	headers = {"Authorization":"Bearer {}".format(token),"Accept": "application/json"}
	result_json = requests.get(request_url,headers=headers).json()
	tracks = [x['track']['id'] for x in result_json["items"]]
	if len(tracks):
		delete_url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlisturi)
		delete_data = {"tracks":[{"uri":"spotify:track:{}".format(id)} for id in tracks]}
		headers['Content-Type'] = "application/json"
		j = requests.delete(delete_url,json=delete_data,headers=headers)	
		print(j.json())
	else:
		print("Playlist was empty")




def getSubmissions(subreddit,mode="new",number=None,time_since=None):
	"""
	Gets post title and url from `subreddit
	Args - subreddit - string, subreddit to consider
		   mode - string, should be one of "hot","new" or "top"
		   number - int, number of posts to recover 
		   time_since - float, UTC stamp of oldest post to consider
	"""
	# TODO allow non-UTC time 
	redditgettor = praw.Reddit('GetMusicBot')
	if time_since is not None:
		mode = "new"
	if mode == "new":
		submissions = redditgettor.subreddit(subreddit).new()	# Get as many submissions as possible
	elif mode == "top":
		submissions = redditgettor.subreddit(subreddit).top()	# Get as many submissions as possible
	elif mode == "hot":
		submissions = redditgettor.subreddit(subreddit).hot()	# Get as many submissions as possible

	it = 0 
	ret = []
	for sub in submissions:
		if number is not None:
			if it >= number:
				break
		elif time_since is not None:
			if sub.created_utc < time_since:
				break

		summary = {}
		summary['title'] = sub.title
		summary['timestamp'] = sub.created_utc
		summary['url'] = sub.url
		ret.append(summary)
		it+=1

	return ret

if __name__ == "__main__":
	userconfig = json.load(open(userconfigfile,"r"))
	deleteAllTracksSpotify(userconfig['spotify']['api_key'],userconfig['spotify']['playlists']['listentothis'])