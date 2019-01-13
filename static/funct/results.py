# twResults class

import datetime
import re
from flask import redirect
from gettweets import gettweets
from misc import writeLog
from words import connectors, cuswords


def redirect_flask():
    return redirect('wait')


class twResults:

    def __init__(self, search_term, result_type, retweets=True):
        self.tweet_data = {}
        self.num_tweets = 0
        self.keyword = search_term.replace(' ', '%20').lower().strip()
        self.result_type = result_type
        self.retweets = retweets
        self.words = {}
        self.hashtags = {}
        self.users = {}
        self.dates = {}
        self.out_words = ''
        self.out_hashtags = ''
        self.out_users = ''
        self.out_tweets = ''
        self.out_dates = ''
        self.email_text = ''
        self.twittermine()
        if self.tweet_data is not None:
            self.distill()
            self.create_text()
        if self.result_type == 'subscribe':
            self.create_file()
        # self.display()

    def twittermine(self):
        if self.result_type in ('mixed', 'popular'):
            self.tweet_data = gettweets(self.keyword,
                                        self.result_type,
                                        retweets=self.retweets)
        elif self.result_type == 'subscribe':
            self.tweet_data = gettweets(self.keyword,
                                        'mixed',
                                        retweets=self.retweets,
                                        days=4,
                                        count=100)
        if self.tweet_data is not None:
            self.num_tweets = len(self.tweet_data)
        else:
            self.num_tweets = 0

    def display(self):  # DEV ONLY
        print 'TWEETS:'
        for ix, tweet in enumerate(self.tweet_data):
            print '%i: %s' % (ix, tweet)
        print '\nHASHTAGS: ', self.out_hashtags
        print '\nUSERS: ', self.out_users
        print '\nDATES: ', self.dates
        print '\nWORDS: ', self.out_words
        print self.email_text

    def distill(self):
        limit = 5
        if self.result_type == 'popular' or self.num_tweets < 100:
            limit = 1
        [self.parse_texts(x['text']) for x in self.tweet_data]
        [self.parse_users(x['user']) for x in self.tweet_data]
        [self.parse_times(x['datetime']) for x in self.tweet_data]
        self.out_words = self.trim_sort(self.words, limit)
        self.out_hashtags = self.trim_sort(self.hashtags, limit)
        self.out_users = self.trim_sort(self.users, limit)
        self.out_dates = self.trim_sort(self.dates, limit)
        self.out_tweets = [str((x['datetime'],
                               x['user'],
                               unicode(x['text'], errors='ignore')))
                           for x in self.tweet_data if x['rt'] is False][:50]

    def parse_texts(self, text):
        for temp00 in text.split(' '):
            temp01 = re.sub('[^0-9a-zA-Z#@]+', '', temp00)
            word = temp01.lower().encode('utf-8', 'ignore')
            if len(word) < 3:
                pass
            elif word in self.keyword:
                pass
            elif word in connectors:
                pass
            elif word in cuswords:
                pass
            elif word[:4] == 'http':
                pass
            elif word[0] == '@':
                pass
            elif word[0] == '#':
                if word in self.hashtags:
                    self.hashtags[word] += 1
                else:
                    self.hashtags[word] = 1
            else:
                if word in self.words:
                    self.words[word] += 1
                else:
                    self.words[word] = 1

    def parse_users(self, user):
        # Tweets per User
        if user in self.users:
            self.users[user] += 1
        else:
            self.users[user] = 1

    def parse_times(self, dt):
        dtClip = dt[4:13].replace(' ', '-')
        if dtClip in self.dates:
            self.dates[dtClip] += 1
        else:
            self.dates[dtClip] = 1

    def trim_sort(self, data, limit, sort_key=1, num=25):
        # Trim
        a = [(x, data[x]) for x in data if data[x] > limit]
        # Sort
        a.sort(key=lambda x: x[sort_key])
        if sort_key == 1:
            a.reverse()
        # Create top n limit if sort_key is 1
        if sort_key == 1:
            b = a[:num]
        else:
            b = a
        # Create string representation
        c = str(['%s: %i' % (x[0], x[1]) for x in b])
        d = c.replace("'", "")
        return d

    def create_text(self):
        limit = 2
        email = ''
        email += '...your results from www.TwitterMining.com\n\n'
        email += 'Keyword: %s\n' % self.keyword.replace('%20', ' ')
        email += 'Date & Time of Mining Operation: %s EST\n' %\
            str(datetime.datetime.now())
        email += 'Number of tweets: %i\n\n' %\
            self.num_tweets
        email += 'Trending Words(Frequency):\t%s\n\n' %\
            self.trim_sort(self.words, limit)
        email += 'Trending Hashtags(Frequency):\t%s\n\n' %\
            self.trim_sort(self.hashtags, limit)
        email += 'Users(tweets >= 3): %s\n' %\
            self.trim_sort(self.users, limit)
        email += 'Tweets by hour: %s\n\n' %\
            self.trim_sort(self.dates, limit)
        email += 'Tweet List:\n'
        email += '#: datetime, user, geo, text\n'
        for index, tweet in enumerate(self.tweet_data):
            email += '%i: %s, %s, %s, %s\n' %\
                (index + 1, tweet['datetime'],
                 tweet['user'], tweet['geo'],
                 tweet['text'].decode('utf-8').strip())
        email += '\n\nThank you for using twittermining.com!\n'
        email += 'www.twitterMining.com\n'
        email += 'info@twittermining.com'
        self.email_text = email.encode('utf-8', 'encode')

    def create_file(self):
        limit = 3
        txtfile = 'temp/%s.txt' % self.keyword.replace('%20', '_')
        f = open(txtfile, "w")
        try:
            f.write('################################################\n')
            f.write('##  w w w . t w i t t e r m i n i n g . c o m ##\n')
            f.write('################################################\n\n')
            f.write('Keyword: %s\n' % self.keyword.replace('%20', ' '))
            f.write('Date & Time of Mining Operation: %s EST\n' %
                    str(datetime.datetime.now()))
            f.write('Number of tweets: %i\n\n' % self.num_tweets)
            f.write('Words:\t%s\n' %
                    self.trim_sort(self.words, limit, num=50))
            f.write('\nHashtags:\t%s\n' %
                    self.trim_sort(self.hashtags, limit, num=50))
            f.write('\nUsers: %s\n' %
                    self.trim_sort(self.users, limit, num=50))
            f.write('\nTweets by hour: %s\n' %
                    self.trim_sort(self.dates, limit, num=50))
            f.write('\nTweet List:\n')
            for index, tweet in enumerate(self.tweet_data):
                f.write('%i: %s, %s, %s, %s\n' %
                        (index + 1,
                            tweet['datetime'],
                            tweet['user'],
                            tweet['geo'],
                            tweet['text']))
            f.write('\nThank you for using twittermining.com!')
            f.write('\nwww.twitterMining.com')
            f.write('\ninfo@twittermining.com\n\n')
        except IOError:
            action = 'Problem rendering attachment - %s' % IOError
            writeLog('ERROR', action)
            pass
        finally:
            f.close()


"""if __name__ == '__main__':
    import time
    start = time.time()
    terms = ['the other woman',
             'anchorman 2',
             'catching fire']
    for term in terms:
        print 'TERM: ', term
        a = twResults(term, 'subscribe')
        print 'NUM: ', a.num_tweets
        print 'TIME: ', time.time() - start"""
