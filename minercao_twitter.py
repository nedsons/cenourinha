import tweepy
import jsonpickle

api = tweepy.API(auth, wait_on_rate_limit=True,
                 wait_on_rate_limit_notify=True)
				 
searchQuery = 'queijo 0 lactose'

def coleta_tweets(searchQuery, grupo, num):
	maxTweets = 10000000
	tweetsPerQry = 100
	fName = 'file_name.txt'
	sinceId = None
	max_id = -1
	tweetCount = 0
		print("Downloading max {0} tweets".format(maxTweets))
		with open(fName, 'w') as f:
			while tweetCount < maxTweets:
				try:
					if max_id <= 0:
						if not sinceId:
							new_tweets = api.search(searchQuery, count=tweetsPerQry, lang='pt')
						else:
							new_tweets = api.search(searchQuery, count=tweetsPerQry,
													since_id=sinceId, lang='pt')
					else:
						if not sinceId:
							new_tweets = api.search(searchQuery, count=tweetsPerQry,
													max_id=str(max_id - 1), lang='pt')
						else:
							new_tweets = api.search(searchQuery, count=tweetsPerQry,
													max_id=str(max_id - 1),
													since_id=sinceId, lang='pt')
					if not new_tweets:
						print("No more tweets found")
						break
					for tweet in new_tweets:
						try:
							# print(tweet._json['text'])
							f.write(jsonpickle.encode(tweet._json, unpicklable=False) +
									'\n')
						except(RuntimeError, TypeError, NameError, Exception) as e:
							print('error: ', e)
							logging.error(e)
							pass
					tweetCount += len(new_tweets)
					print("Downloaded {0} tweets".format(tweetCount))
					max_id = new_tweets[-1].id
				except tweepy.TweepError as e:
					# Just exit if any error
					print("some error : " + str(e))
					break

		print("Downloaded {0} tweets, Saved to {1}".format(tweetCount, fName))
