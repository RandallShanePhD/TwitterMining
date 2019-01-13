# Get Tweets

import pytz
import random

from datetime import date, datetime, timedelta
from twython import Twython, TwythonError
from misc import writeLog

results = []
# {'rt': bool, 'text': str, 'user': str, 'id': int, 'datetime': str}


def permission(mr):
    consumer_key = ""
    consumer_secret = ""
    access_token = ""
    access_token_secret = ""
    if mr == 0:
        # Locator Rig
        consumer_key = "gJileblrpfV8s1nqcjf4v8ZQw"
        consumer_secret = "3QuqGc8PxVBRoAUBZCPxGuyLFkNZZyEiNkMOkxEbXsU9KwdBd2"
        access_token = "1561881230-ti5xtGmY3gVqXkNXoPk6FH1VXi2URpJEx9rFUvL"
        access_token_secret = "fkK94WGBLJwuN4yEWkbzUaI0j1LNzrRpQ0Q2ktgDwmrXu"
    elif mr == 1:
        # Mining Rig 01
        consumer_key = "ouXMt740fBBvEiltPjw4A"
        consumer_secret = "fFrEHF6b6ibZBjuNfI1Waql4tDcLQKZO5ZknQMgjhf4"
        access_token = "1561881230-9ucwTOfH5LpwF5kc8CdfhkLwMuTI3VtsI8d2STU"
        access_token_secret = "zMgOnh1GqC0XSxWgbpQIrP3w24KdHycByxc0b31Fk"
    elif mr == 2:
        # Mining Rig 02
        consumer_key = "pWpV47yonc8eE5I8isjceQ"
        consumer_secret = "5lLRW81fXKqbkp43nkJMt9uRkxNEhycGNL4yVV8Q"
        access_token = "1561881230-N9qI9F61gzaeEv5V107m2R3Xfm5dH6HsitHiyfg"
        access_token_secret = "6U677xhMX5VXXk5ukKbHyp7pIEiVa8sK1AjfVFEWQ"
    elif mr == 3:
        # Mining Rig 03
        consumer_key = "2wsgS8jkz8r8VKraMdJP3Q"
        consumer_secret = "nJIK8WHxcbwDwprVRxgvEZPYtcnB54oH7EO3mARUY"
        access_token = "1561881230-ct501hj8yGiPLxlyBhAxPUcdEpr3qzg7DnWDsoW"
        access_token_secret = "I0O40B2x7v3gTaTG3qsaP3f8zQHrxH8mb7Zo5cuAJSLDb"
    elif mr == 4:
        # Mining Rig 04
        consumer_key = "oTUWHg9UxG3nUSCwDkNyqA"
        consumer_secret = "r3MeDb8e9jsRNrubbyQO2HbCX5xmzYGGflYRT9WcvAk"
        access_token = "1561881230-lRalilABfVJonqJBL44AWyuGIGlK459BM4XNOUK"
        access_token_secret = "io7MnSLALl0iovPkrXyIikVlcEc86n6lcaALDnEIqBmFk"

    perm = Twython(
        consumer_key, consumer_secret, access_token, access_token_secret)

    return perm


def retrieve(mr, keyword, sinceid, maxid):
    temp_results = []
    twitter = permission(mr)
    try:
        search_results = twitter.search(q=keyword,
                                        result_type='mixed',
                                        count=100,
                                        lang='en',
                                        since_id=sinceid,
                                        max_id=maxid)
        if 'statuses' in search_results:
            for status in search_results['statuses']:
                temp_results.append(status)

    except TwythonError as e:
        writeLog('ERROR', e)

    return temp_results


def timeline(mr, screen_name):
    temp_results = []
    twitter = permission(mr)
    try:
        temp_results = twitter.get_user_timeline(screen_name=screen_name,
                                                 count=200)
    except TwythonError as e:
        writeLog('ERROR', e)

    # if search_results:
    #     for result in search_results:
    #         temp_results.append(result)

    return temp_results


def process(s):
    tweet = {}

    # tweet id
    if 'id' in s:
        tweet['id'] = s['id']
    else:
        tweet['id'] = 0

    # Date processing for timezone
    if 'created_at' in s:
        dateConv0 = s["created_at"]
        dateConv1 = '%s %s' % (dateConv0[0:19], dateConv0[25:30])
        dateConv2 = datetime.strptime(
            dateConv1, '%a %b %d %H:%M:%S %Y')
        gmt = pytz.timezone('GMT')
        dateConv3 = gmt.localize(dateConv2)
        dateConv4 = dateConv3.astimezone(
            pytz.timezone('US/Eastern'))
        tweet['datetime'] = datetime.strftime(
            dateConv4, '%a %b %d %H:%M:%S %Y')
    else:
        tweet['datetime'] = 'Thu Jan 01 00:00:00 1970'

    # User check
    if 'user' in s:
        if 'screen_name' in s['user']:
            tweet['user'] = s['user']['screen_name'].encode('utf-8', 'ignore')
    else:
        tweet['user'] = 'tweeter'

    # Geo Coordinates
    tweet['geo'] = '[no geo]'
    if 'geo' in s:
        raw = s['geo']
        if raw is not None and 'coordinates' in raw:
            tweet['geo'] = raw[u'coordinates']

    # Tweets
    if 'text' in s:
        tweet['text'] = s['text'].replace('\n', '').encode('utf-8', 'ignore')
    else:
        tweet['text'] = ''

    # Retweet
    tweet['rt'] = False
    if tweet['text'][:2] == 'RT':
        tweet['rt'] = True

    # print 'TWEET: ', tweet  # DEV ONLY
    return tweet


def gettweets(keyword, category, retweets=True, days=2, count=20):
    tweets = []
    tweet_set = []
    # Step 0: Set oauth permission
    twitter = permission(0)
    if category == 'popular':
        try:
            search_results = twitter.search(q=keyword,
                                            result_type='popular',
                                            lang='en')
            for result in search_results['statuses']:
                tweets.append(process(result))
        except TwythonError as e:
            writeLog('ERROR', e)

    elif category == 'mixed':
        if keyword[0] == '@':  # User search
            mr = random.randint(1, 4)
            permission(mr)
            tweet_set = timeline(mr, keyword)
            for entry in tweet_set:
                tweets.append(process(entry))

        else:  # Keyword search
            # Step 1: tweet range back n days
            from_dt = str(date.today() - timedelta(days=days))
            since_id = 0
            max_id = 0
            try:
                from_tweet = twitter.search(q=keyword,
                                            result_type='recent',
                                            count=1,
                                            until=from_dt)
                if from_tweet['statuses'] != []:
                    since_id = int(from_tweet['statuses'][0]['id'])
                else:
                    return None
                to_tweet = twitter.search(q=keyword,
                                          result_type='recent',
                                          count=1)
                max_id = int(to_tweet['statuses'][0]['id']) + 1
            except TwythonError as e:
                # RATE LIMIT ERROR CATCHES HERE
                writeLog('ERROR', e)

            # Step 2: Retrieve tweets - cut into chunks
            increment = (max_id - since_id) / count
            since_id -= increment

            for i in range(count):
                mr = random.randint(1, 4)
                permission(mr)
                since_id = since_id + increment
                max_id = since_id + increment

                tweet_set = retrieve(mr, keyword, since_id, max_id)

                for entry in tweet_set:
                    tweets.append(process(entry))

                since_id = max_id
                mr += 1

        if len(tweets) == 0:
            tweets.append(['There', 'are', 'no', 'results!'])
        elif retweets is False:
            noRT = []
            for tweet in tweets:
                if tweet['rt'] is False:
                    noRT.append(tweet)
            return noRT
        else:
            return tweets


'''if __name__ == '__main__':
    import time
    start = time.time()
    # tweets = gettweets('dog', 'mixed')  # with retweets
    # tweets = gettweets('dog', 'mixed', retweets=False)  # no retweets
    tweets = gettweets('@madisonarf', 'mixed')  # user search
    # tweets = gettweets('dog', 'mixed', days=4, count=100)  # subscription
    print 'NUM: ', len(tweets)
    print 'TIME: ', time.time() - start
    print tweets'''
