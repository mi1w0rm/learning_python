#!/usr/bin/env python

import re
from datetime import datetime

import nltk
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import NewPost, EditPost


def init_wordpress_client():
    wp = Client('http://localhost:8082/xmlrpc.php', 'mi1w0rm', 'satsumacar895')

    return wp


# parse the original_time like 'Fri Feb 16 07:42:40 +0000 2018' to '2018-02-16 07:42:40' datetime
def parse_post_formated_time(original_time='Fri Feb 16 07:42:40 +0000 2018'):
    post_date = datetime.strptime(original_time, '%a %b %d %H:%M:%S +0000 %Y')

    return post_date


# use nltk to generate the tags of the raw info
def generate_tags(raw_info):
    tags = []
    tags_result = []
    week_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']

    tokens = nltk.word_tokenize(raw_info)

    print tokens

    tags.append(nltk.pos_tag(tokens))

    for tag in tags[0]:

        # only find the 'JJ' and 'NNP'
        if 'JJ' in tag or 'NNP' in tag:

            str_temp = tag[:1][0]

            # only find the word starts with capitalized character or digits
            if re.match('^[A-Z0-9]', str_temp) is not None:

                # exclude the weekday and month
                if not (str_temp in week_days or str_temp in months):
                    tags_result.append(str_temp)

    return (tags_result)


def reformat_url_with_htmltag(raw_content):
    re_object = re.compile('(http|https)://.*\s<br>')

    url = re_object.search(raw_content).group()[:-5]

    # new url with tag like <a href="https://t.co/g67c4RKGBu">https://t.co/g67c4RKGBu</a>
    url_with_tag = '<a href="%s">%s</a>' % (url, url)

    new_content = raw_content.replace(url, url_with_tag)

    return new_content


def create_new_post(wp_instance, title='', content='', author='', tags=[], category=['USAF']):
    post = WordPressPost()

    post.title = title

    content = reformat_url_with_htmltag(content)

    post.content = content

    tags.append(author)

    tags = tags + generate_tags(content)

    category.append(author)

    # By far, only classify the 'Kadena' and 'Andersen' AFB
    if 'Kadena' in tags:
        category.append('Kadena')

    if 'Andersen' in tags:
        category.append('Andersen')

    post.terms_names = {
        'post_tag': tags,
        'category': category
    }

    post.post_status = 'publish'

    # insert the new post
    post_id = wp_instance.call(NewPost(post))

    # update the published date to the tweet datetime
    re_object = re.compile('(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s.*\s\d{4}')

    original_time = re_object.search(content).group()

    post.date = parse_post_formated_time(original_time)

    post.date_modified = post.date

    # update the post author to the tweet screen name
    post.post_author = 2

    wp_instance.call(EditPost(post_id, post))

    return post_id
