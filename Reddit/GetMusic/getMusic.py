import json
import praw
import re

configfile = "subredditconfig.json"
# TODO - filter out playlist posts, save for later
# TODO - can use only certain genres
class MusicSubmission:
	def __init__(self,subreddit,submission):
		config = json.load(open(configfile,"r"))[subreddit]
		self.parse_title(submission['title'],config)
	def __str__(self):
		str = ("Title : {}\nArtist : {}\n".format(self.title,self.artist))
		if self.genre is not None:
			str+=("Genre : {}\n".format(self.genre))
		return str
	def parse_title(self,title,config):
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

	# def parse_url(self,)
	# 	self.url = url
	# 	self.spotifyuri = service
	# 	self.youtubeuri = uid

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

if __name__ == '__main__':
	submissions = getSubmissions('listentothis',number=10)
	for sub in submissions:
		m = MusicSubmission('listentothis',sub)
		print(str(m))