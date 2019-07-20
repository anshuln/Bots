import json
import praw
import re
import requests

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

		#TODO may not be able to scrape Spotify, need some other method...


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
	a = getSubmissions('listentothis',number=5)
	for j in a:
		m = MusicSubmission('listentothis',j)
		print(str(m))
		print(m.youtubeuid)