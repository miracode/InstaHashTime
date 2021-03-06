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
    outwriter.writerow(['hashtags',
                        'timestamp',
                        'type',
                        'users_in_photo',
                        'user_id',
                        'likes',
                        ])

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
                outwriter.writerow([media['tags'],
                                    time,
                                    media['type'],
                                    len(media['users_in_photo'])
                                    if media['users_in_photo'] else 0,
                                    media['user']['id'],
                                    media['likes']['count']
                                    ])

            data = json.load(urllib2.urlopen(next_url))
            next_url = data['pagination']['next_url']

    csvfile.close()


def get_users_set(file):
    users = set()
    with open(file, 'rb') as read_file:
        reader = csv.reader(read_file, delimiter=';')
        header = next(reader, None)
        index = header.index('user_id')
        for row in reader:
            users.add(row[index])
    return users


def get_user_followers(client_id, user_ids, outfile):

    outfile = '{}.csv'.format(outfile.partition('.')[0])
    csvfile = open(outfile, 'wb')
    outwriter = csv.writer(csvfile, delimiter=';')
    outwriter.writerow(['user_id', 'followers'])

    url = ('https://api.instagram.com/v1/users/{user_id}'
           '?client_id={client_id}')

    for user_id in user_ids:
        try:
            data = json.load(urllib2.urlopen(url.format(user_id=user_id,
                                                        client_id=client_id)))
            followers = data['data']['counts']['followed_by']
            outwriter.writerow([user_id, followers])
        except Exception as e:
            # 429 is too many requests.
            if 'HTTP Error 429' in e:
                break
            # Also getting some 400's for presumably users that no longer exist
            print("Error: {}\nUser ID: {}".format(e, user_id))

    csvfile.close()
