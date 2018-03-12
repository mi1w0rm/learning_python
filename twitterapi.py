#!/usr/bin/env python

from __future__ import print_function

import cStringIO
import codecs
import datetime
import os
import time
import types
import urllib2

import MySQLdb as mdb
import requests.exceptions
import twitter
import twitter.error
from PIL import Image

from wpapi import create_new_post
from wpapi import init_wordpress_client

CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'satsumacar*(%',
    'db': 'global_mil_infomation',
    'charset': 'utf8'
}

conn = mdb.connect(**CONFIG)


def update_sleeping_status(sleep_time=60):
    t = time.time()
    i = 0
    while (i < sleep_time):
        print(datetime.datetime.now())
        i = i + 5
        time.sleep(5)


ACCESS_TOKEN = '76266912-KFBRoW8utydwHl4UqEPP2xZr7CD35xKRL165Vxy9H'
ACCESS_TOKEN_SECRET = 'Biosve1cLqETSEoi7UZFBrlHcAzmtl8UaVtq27ETM1OZ6'
CONSUMER_KEY = 'SKXWYrbC8OeYxl1PCmjRf9IEr'
CONSUMER_SECRET = 'sVpkOOY1mK5a8Z6Sv2yLD3qOvVXZZakK8DtHsURFTmH7lBA5FY'

# Create an Api instance.
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN,
                  access_token_secret=ACCESS_TOKEN_SECRET)

people_dic = {}
tweet_dic = {}


# Get Twitter_user_id and Twitter_screen_name from default input
# user_id = raw_input('Enter the target people"s twitter_user_id:')
# screen_name = raw_input('Enter the target people"s twitter_screen_name:')

# def GetFriends(self, user_id=None, screen_name=None, cursor=None, count=None, total_count=None, skip_status=False, include_user_entities=True):

# if (user_id != '' and screen_name != ''):
#    users = api.GetFriendsPaged(user_id,screen_name)

# else:
def get_following_followed_by_userid(uid=3823186093, sname='@iRebiyaKadeer', iflag='following'):
    user_id = uid
    screen_name = sname
    flag = iflag
    fellow_counter = 0

    if (screen_name != ''):
        if not (os.path.isdir(screen_name)):
            os.mkdir(screen_name)
        os.chdir(screen_name)

    next_cursor = -1

    try:
        if (flag == 'following'):
            users = api.GetFriendsPaged(user_id, screen_name, next_cursor)
        else:
            users = api.GetFollowersPaged(user_id, screen_name, next_cursor)

    except twitter.error.TwitterError as te1:
        print('\t----Reach the query limit, wait for 15 minites until next query......\n')
        flog = open(screen_name + 'log.txt', 'a+')
        # flog.write(time.localtime(time.time()) + '\t:\t' + te1.message)
        flog.write(
            datetime.datetime.now().__str__() + '\t----Reach the query limit, wait for 15 minites until next query......\n')
        flog.close()

        # time.sleep(900)
        update_sleeping_status(900)

        print('\tStarting new query after 15 minutes sleep......\n')

        if (flag == 'following'):
            users = api.GetFriendsPaged(user_id, screen_name, next_cursor)
        else:
            users = api.GetFollowersPaged(user_id, screen_name, next_cursor)

    except requests.exceptions.ConnectionError as cerr:
        print('\t----Network is unreachable, wait 60 seconds and retry......\n')
        flog = open(screen_name + 'log.txt', 'a+')
        # flog.write(time.localtime(time.time()) + '\t:\t' + cerr.message)
        flog.write(
            datetime.datetime.now().__str__() + '\t----Network is unreachable, wait 60 seconds and retry......\n')
        flog.close()
        cerr
        # time.sleep(900)
        update_sleeping_status(60)

        print('\tStarting new query after 1 minutes sleep......\n')

        if (flag == 'following'):
            users = api.GetFriendsPaged(user_id, screen_name, next_cursor)
        else:
            users = api.GetFollowersPaged(user_id, screen_name, next_cursor)

    while (users[2].__len__() > 0):

        fellow_counter = fellow_counter + users[2].__len__()

        next_cursor = users[0]

        for u in users[2]:
            file_name = '[%s]-[%d].txt' % (u.name, u.id)

            # people_dic[u.id] = u.name
            people_dic[u.id] = {'screen_name': u.screen_name, 'user_name': u.name}

            print('Writing file:\t' + file_name + '......')

            try:
                fp = open(file_name, 'a+')
                fp.write(u.__str__())
            except Exception as e:
                fp = open('[%d].txt' % (u.id), 'a+')
            finally:
                fp.close()

        print('Waiting for 60 seconds until next query......\n')
        update_sleeping_status()

        print(datetime.datetime.now().__str__() + ':\t' + 'Starting next query......\n')

        try:
            if (flag == 'following'):
                users = api.GetFriendsPaged(user_id, screen_name, next_cursor)
            else:
                users = api.GetFollowersPaged(user_id, screen_name, next_cursor)


        except twitter.error.TwitterError as te1:

            print('\t----Reach the query limit, wait for 15 minites until next query......\n')

            flog = open(screen_name + 'log.txt', 'a+')

            flog.write(time.localtime(
                time.time()) + '\t----Reach the query limit, wait for 15 minites until next query......\n')

            flog.close()

            # time.sleep(900)

            update_sleeping_status(900)

            print('\tStarting new query after 15 minutes sleep......\n')

            if (flag == 'following'):

                users = api.GetFriendsPaged(user_id, screen_name, next_cursor)

            else:

                users = api.GetFollowersPaged(user_id, screen_name, next_cursor)


        except requests.exceptions.ConnectionError as cerr:

            print('\t----Network is unreachable, wait 60 seconds and retry......\n')

            flog = open(screen_name + 'log.txt', 'a+')

            flog.write(
                datetime.datetime.now().__str__() + '\t----Network is unreachable, wait 60 seconds and retry......\n')

            flog.close()

            # time.sleep(900)

            update_sleeping_status(60)

            print('\tStarting new query after 1 minutes sleep......\n')

            if (flag == 'following'):

                users = api.GetFriendsPaged(user_id, screen_name, next_cursor)

            else:

                users = api.GetFollowersPaged(user_id, screen_name, next_cursor)

        finally:
            print('\n' + u'Find %s(%s) followings %d ' % (screen_name, user_id, fellow_counter))

    # Create the twitter dictory
    if not (os.path.isdir('../twitter_dic/')):
        os.mkdir('../twitter_dic/')

    if (flag == 'following'):
        file_name = '../twitter_dic/' + screen_name + '_following_dic.txt'
    else:
        file_name = '../twitter_dic/' + screen_name + '_followed_dic.txt'

    try:
        fdic = codecs.open(file_name, 'a+', 'utf-8')

        for id in sorted(people_dic.keys()):
            fdic.write(
                str(id) + '\t\t\t@' + people_dic[id]['screen_name'] + '\t\t\t' + people_dic[id]['user_name'] + '\n')

    finally:
        fdic.close()


def get_latest_tweets_by_user(screenname, cursor, maxid=0, sinceid=0):
    # api = twitter.Api(consumer_key=CONSUMER_KEY,
    #                  consumer_secret=CONSUMER_SECRET,
    #                  access_token_key=ACCESS_TOKEN,
    #                  access_token_secret=ACCESS_TOKEN_SECRET)

    tweet_dic = api.GetUserTimeline(screen_name=screenname, max_id=maxid, since_id=sinceid, count=100)

    # print('-Created Time- \t Tweet ID \t ----Tweet Text----\t Tweet User')

    start_time = time.time()

    i_counter = 0

    for tweet in tweet_dic:
        insert_status_info_into_db(tweet, cursor)

        i_counter = i_counter + 1

    end_time = time.time()

    time_collaps = end_time - start_time

    print('--------{0} Status records have been inserted into dababase, total time is {1} seconds----'.format(i_counter,
                                                                                                              time_collaps))


def insert_status_info_into_db(tweet, cursor):
    tweet_created_time = tweet.created_at
    tweet_text = tweet.text
    tweet_id = tweet.id_str
    tweet_user = tweet.user.screen_name

    tweet_text = tweet_text.replace('\'', '\\\'')

    tweet_text = tweet_text.strip()
    tweet_created_time = tweet_created_time.strip()

    # detail_result = get_earth_quake_detail_info(u_id, cursor)

    sql = "INSERT INTO `global_mil_infomation`.`tb_aviation_raw_info` " \
          "(`s_status_id`,`s_created_time`,`s_text`,`s_twitter_user_name`)" \
          "VALUES " \
          "(%s,'%s','%s','%s');" % (tweet_id, tweet_created_time, tweet_text, tweet_user)

    sql = sql.encode('utf-8')

    try:
        cursor.execute(sql)
        # conn.commit()

    except mdb.IntegrityError as dbie:

        print('----[%s] mdb.IntegrityError......' % (tweet_id))
        # conn.rollback()

    except mdb.OperationalError as dboe:

        print('--------Insert [%s] mdb.OperationalError......' % (tweet_id))
        # conn.rollback()

    except mdb.ProgrammingError as pe:

        print('--------[%s] mdb.ProgrammingError, and message is %s......' % (tweet_id, pe))
        # conn.rollback()

    insert_status_media_info_db(tweet, cursor)


# Get following friends with specified user_id
# get_following_followed_by_userid(76266912, '@AircraftSpots', 'following')
# get_following_followed_by_userid(876321004120936448, '@cskun1989', 'followed')

def insert_status_media_info_db(tweet, cursor):
    status_id = tweet.id
    media = tweet.media

    if type(media) is not None:

        try:
            for each_media in media:

                display_url = each_media.display_url
                expanded_url = each_media.expanded_url
                media_id = each_media.id
                media_url = each_media.media_url
                media_url_https = each_media.media_url_https
                media_type = each_media.type
                short_url = each_media.url

                if type(each_media.video_info) is not None:
                    video_info = each_media.video_info

                sql = 'INSERT INTO `global_mil_infomation`.`tb_status_media` ' \
                      '(`s_status_id`, `i_media_id`, `s_media_type`, `s_display_url`, ' \
                      '`s_extended_url`, `s_media_url`, `s_media_url_https`, `s_url`) ' \
                      'VALUES ( %d, \'%s\', \'%s\', \'%s\', \'%s\', \'%s\',  \'%s\', \'%s\')' \
                      % (
                          status_id, media_id, media_type, display_url, expanded_url, media_url, media_url_https,
                          short_url)

                sql = sql.encode('utf-8')

                try:
                    cursor.execute(sql)

                except mdb.IntegrityError as dbie:

                    print('----[%s] mdb.IntegrityError......' % (status_id))

                except mdb.OperationalError as dboe:

                    print('--------Insert [%s] mdb.OperationalError, and message is %s......' % (status_id, dboe))

                except mdb.ProgrammingError as pe:

                    print('--------[%s] mdb.ProgrammingError, and message is %s......' % (status_id, pe))

        except TypeError as te:

            # print('--------[%s] TypeError, and message is %s......' % (status_id, te))

            return

            # get the remote photo and insert into db
            # get_photo_by_url(media_url, media_id)


def get_photo_by_url(photo_url, i_media_id):
    if type(photo_url) is not None:
        photo_file = urllib2.urlopen(photo_url)
        tmp_image = cStringIO.StringIO(photo_file.read())

        im = Image.open(tmp_image)

        sql = 'UPDATE `global_mil_infomation`.`tb_status_media` ' \
              'SET ' \
              '`b_media_content` = %b WHERE `i_media_id` = %s'


def get_oldest_status_id_by_user(screen_name, cursor):
    oldest_status_id = ''

    sql = "SELECT min(s_status_id) " \
          "FROM global_mil_infomation.tb_aviation_raw_info " \
          "where s_twitter_user_name = '%s'" % screen_name
    try:

        cursor.execute(sql)

        for row in cursor:
            print(row)
            oldest_status_id = row[0]

    except mdb.OperationalError as mdbe:

        print('--------[%s] mdb.OperationalError, and message is %s......' % (screen_name, mdbe))

    return oldest_status_id


def post_aviation_intelligence(cursor, wpinstance, screen_name='', count=100):
    sql = "SELECT * FROM global_mil_infomation.status_media_view " \
          "WHERE s_twitter_user_name = '%s' " \
          "ORDER BY s_status_id DESC LIMIT %d" % (screen_name, count)

    try:

        cursor.execute(sql)

        i_counter = 0

        for row in cursor:
            content = '%s ' \
                      '<br>Posted at %s .' \
                      '<img src="%s" alt="" />' % (row[5], row[4], row[6])

            twitter_author = row[2]

            post_id = create_new_post(wpinstance, 'Status ID:' + row[0], content, twitter_author)

            print('%d post has been uploaded to wordpress.' % i_counter)

            i_counter = i_counter + 1


    except mdb.OperationalError as mdbe:

        print('--------[%s] mdb.OperationalError, and message is %s......' % (screen_name, mdbe))


def main():
    screen_name = 'AircraftSpots'
    current_status_id = ''

    # initial the mysql db
    if (conn != None):
        conn.autocommit(True)  # conn.autocommit(True)
        cursor = conn.cursor()

    wp = init_wordpress_client()

    post_aviation_intelligence(cursor, wp, screen_name, 100)

    # get_latest_tweets_by_user(screen_name, cursor, maxid=0, sinceid=966116467753197571)

    # while 1:
    #
    #     oldest_status_id = get_oldest_status_id_by_user(screen_name, cursor)
    #
    #     if type(oldest_status_id) is not types.NoneType:
    #
    #         get_latest_tweets_by_user(screen_name, cursor, maxid=oldest_status_id)
    #
    #         if current_status_id == oldest_status_id:
    #             break
    #
    #         else:
    #             current_status_id = oldest_status_id
    #
    #             print('----Has fetched the [%s]\'s status before [%s]----' % (screen_name, current_status_id))
    #
    #     else:
    #
    #         break


main()
