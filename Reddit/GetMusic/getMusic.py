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
		search_url = 'https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q={}&key={}'.format(search_query,apikey) 
		result_json = requests.get(search_url,headers={'content-type': 'application/json'}).json()
		id = result_json['items'][0]['id']	#TODO explain this line, may have to remove the hardcoding
		if id['kind'] != 'youtube#video':
			self.youtubeuid = None	#TODO fix this
			print("Currently we only support songs, not albums")
		else:
			self.youtubeuid = id['videoId']

	def set_spotify_uid(self):
		# TODO should this go in SpotifyInterface
		if self.title is None:
			return	#TODO fix this
		search_query = 'q={} {}&type=track'.format(self.title,self.artist).strip().replace(' ','+')	#TODO experiment with artist name etc	
		search_url = "https://api.spotify.com/v1/search?{}&limit=1".format(search_query)
		sp = SpotifyInterface()
		token = sp.get_token()
		headers = {"Authorization":"Bearer {}".format(token)}
		result_json = requests.get(search_url,headers=headers).json()
		try:
			self.spotifyuid = "track:{}".format(result_json['tracks']['items'][0]['id'])	#TODO error handling
		except:
			search_query = 'q={}&type=track'.format(self.title).strip().replace(' ','+')
			search_url = "https://api.spotify.com/v1/search?{}&limit=1".format(search_query)
			result_json = requests.get(search_url,headers=headers).json()
			try:
				self.spotifyuid = "track:{}".format(result_json['tracks']['items'][0]['id'])	#TODO error handling
			except:
				print("No results for {}".format(self.title))
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
			self.spotifyuid = spmatch.group('uid').replace("/",":")

		if self.youtubeuid is None:
			apikey = json.load(open(userconfigfile))['youtube_api_key']
			self.set_youtube_uid(apikey)

		if self.spotifyuid is None:
			self.set_spotify_uid()

		#TODO parse provided URL to set artist, title etc.
class SpotifyInterface():
	def __init__(self,userconfigfile=userconfigfile):
		userdict = json.load(open(userconfigfile,"r"))
		self.userconfigfile = userconfigfile
		self.apikey = userdict['spotify']['api_key']

	def get_token(self):	#apikey is base64
		userdict = json.load(open(self.userconfigfile,"r"))
		last_time = userdict['spotify']['access_token']['timestamp']
		if time.time() - last_time < 3600:	# Access tokens valid for 3600 s, TODO remove hard coding
			return userdict['spotify']['access_token']['token']
		token_url = "https://accounts.spotify.com/api/token"
		data = {"grant_type" : "refresh_token", "refresh_token":userdict['spotify']['access_token']['refresh_token']}
		headers = {"Authorization" : "Basic {}".format(self.apikey)}
		response = requests.post(token_url,data=data,headers=headers)
		token = response.json()['access_token']	#TODO error handling
		userdict['spotify']['access_token']['token'] = token
		userdict['spotify']['access_token']['timestamp'] = time.time()
		json.dump(userdict,open(self.userconfigfile,"w"))
		return token

	def deleteAllTracks(self,playlisturi):
		token = self.get_token()
		request_url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlisturi)
		headers = {"Authorization":"Bearer {}".format(token),"Accept": "application/json"}
		result_json = requests.get(request_url,headers=headers).json()
		tracks = [x['track']['id'] for x in result_json["items"]]
		if len(tracks):
			delete_url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlisturi)
			delete_data = {"tracks":[{"uri":"spotify:track:{}".format(id)} for id in tracks]}
			headers['Content-Type'] = "application/json"
			j = requests.delete(delete_url,json=delete_data,headers=headers)	
			return j.json()
		else:
			print("Playlist was empty")

	def addTracks(self,playlisturi,MusicSubmissionlist):
		token = self.get_token()
		request_url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlisturi)
		headers = {"Authorization":"Bearer {}".format(token),"Accept": "application/json"}
		upload_data = "%2C".join(["spotify:{}".format(track.spotifyuid).replace(":","%3A") for track in MusicSubmissionlist if track.spotifyuid is not None])
		headers['Content-Type'] = "application/json"
		headers['Content-Type'] = "application/json"
		j = requests.post("{}?uris={}".format(request_url,upload_data),headers=headers)	
		print("Added {} tracks".format(len(upload_data.split("%2C"))))
		return j.json()


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
	#Updating time checked
	s = json.load(open(subredditconfigfile,"r"))
	time_since = s[subreddit]['time_checked']
	s[subreddit]['time_checked'] = time.time()
	json.dump(s,open(subredditconfigfile,"w"))
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

def main(subreddit):
	userconfig = json.load(open(userconfigfile,"r"))
	subs = getSubmissions(subreddit)
	MSlist = []
	for sub in subs:
		MS = MusicSubmission(subreddit,sub)
		MSlist.append(MS)
	sp = SpotifyInterface()
	print(sp.deleteAllTracks(userconfig['spotify']['playlists'][subreddit]))
	print(sp.addTracks(userconfig['spotify']['playlists'][subreddit],MSlist))

if __name__ == "__main__":
	subredditlist = json.load(open(userconfigfile,"r"))['subredditlist']
	for s in subredditlist:
		main(s)