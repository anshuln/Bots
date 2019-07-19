import praw

class MusicSubmission:
	def __init__(self,title,artist,url,genre=None,service=None,uid=None):
		self.title = title
		self.artist = artist
		self.url = url
		self.genre = genre
		self.service = service
		self.uid = uid

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

