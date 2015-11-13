import json
import urllib2
import csv


def get_hashtag_data(client_id, hashtags, outfile, days=1):
    """
    Create csv with headers hashtag, timestamp, and number of likes.
    Must provide registered Instagram client_id and list of hashtags.
    CSV saved to outfile name.
    Option to choose number of days to process. Default is 1 day.
    """

    if not isinstance(hashtags, list):
        print("Please provide hashtags as a list of words.")
        print("Received: {}".hashtags)
        return

    # Make sure extension is .csv
    outfile = '{}.csv'.format(outfile.partition('.')[0])
    csvfile = open(outfile, 'wb')
    outwriter = csv.writer(csvfile, delimiter=';')
    outwriter.writerow(['hashtag', 'timestamp', 'likes'])

    url = ('https://api.instagram.com/v1/tags/{hashtag}/media/recent'
           '?client_id={client_id}')

    for hashtag in hashtags:
        data = json.load(urllib2.urlopen(url.format(hashtag=hashtag,
                                                    client_id=client_id)))
        next_url = data['pagination']['next_url']
        time = int(data['data'][0]['created_time'])
        time_stop = time - (86400 * days)
        while time > time_stop:
            for media in data['data']:
                time = int(media['created_time'])
                outwriter.writerow([hashtag, time, media['likes']['count']])

            data = json.load(urllib2.urlopen(next_url))
            next_url = data['pagination']['next_url']

    csvfile.close()
