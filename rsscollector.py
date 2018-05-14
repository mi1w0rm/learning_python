# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example docstrings.

This module is an auto rss collector of multi news websites. It can reach the newest news rss contents,
collect them and transport them into a local WordPress website

Class RssCoverImage:
    The meta data class of a rss channel cover image

Class RssChannel:
    The meta data and functions class to get a rss channel and store its contents

Class NewsSite:
    The meta data class of a news website

"""

from datetime import datetime

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

import datamanager as dm

import urllib2

DATA_MANAGER = dm.DataManagerTools()


class RssCoverImage(object):
    # image url
    image_url = ''

    # image title
    image_title = ''

    # image link
    image_link = ''

    def __init__(self, initdata={}):

        if 'image_url' in initdata.keys():
            self.image_url = initdata['image_url']
        if 'image_title' in initdata.keys():
            self.image_title = initdata['image_title']
        if 'image_link' in initdata.keys():
            self.image_link = initdata['image_link']


class RssChannel(object):
    # rss contents list
    channel_contents_list = []

    # rss channel title
    channel_title = ''

    # rss channel url
    channel_link = ''

    # channel description
    channel_description = ''

    # channel copyright
    channel_copyright = ''

    # channel ttl(time to live)
    channel_ttl = 60

    # channel last build date, xml date format like: Sat, 28 Apr 2018 14:30:34 +0800
    channel_last_build_date = datetime.now()

    # channel generator, not important
    channel_generator = ''

    # channel cover image
    channel_image = RssCoverImage()

    # channel atom data
    channel_atom = {'href': '', 'rel': 'self', 'type': 'application/rss+xml'}

    def __init__(self, initdata={}):
        if 'channel_title' in initdata.keys():
            self.channel_title = initdata['channel_title']
        if 'channel_link' in initdata.keys():
            self.channel_link = initdata['channel_link']
        if 'channel_description' in initdata.keys():
            self.channel_description = initdata['channel_description']
        if 'channel_image' in initdata.keys():
            self.channel_image.image_link = initdata['channel_image'].image_link
            self.channel_image.image_url = initdata['channel_image'].image_url
            self.channel_image.image_title = initdata['channel_image'].image_title
        if 'channel_generator' in initdata.keys():
            self.channel_generator = initdata['channel_generator']
        if 'channel_atom_href' in initdata.keys():
            self.channel_atom['href'] = initdata['channel_atom_href']

    def get_rss_content(self, time_interval=0):
        return ''


class NewsSite(object):
    # site original name
    site_name = ''

    # site's dictionary of rss channel name, url, and rss template in xml format
    site_rss_channel = []

    def __init__(self, initdata={}):

        if 'site_name' in initdata.keys():
            self.site_original_name = initdata['site_name']

    def append_channel(self, channel=RssChannel):
        if isinstance(channel, RssChannel) and channel is not None:
            self.site_rss_channel.append(channel)

    '''
    voachinese site's rss channel meta-data
    
        <div class="content">
        <a href="/z/2404" onclick="">
        <h4 class="media-block__title">
        <span class="title">双语新闻</span>
        </h4>
        <p>美国之音中文网每周一到五提供两条中英对照的新闻，供读者参考使用。</p>
        </a>
        <a class="link-service" href="/api/z-$trevtuo">
        <span class="ico ico-rss"></span>
        订阅
        </a>
        </div>
    '''

    def init_site_channels(self, atom_url='https://www.voachinese.com/rssfeeds'):

        if self.site_original_name == 'voachinese':

            response = urllib2.urlopen(urllib2.Request(atom_url))
            html = response.read()
            parsed_html = BeautifulSoup(html)

            # parsed_html = BeautifulSoup(open('voa.html'))
            # print parsed_html.prettify()

            channel_list = []

            for div_content in parsed_html.find_all('div', class_="media-block horizontal size-2"):
                # print(div_content.contents)

                if (div_content.h4.attrs['class'][0] == 'media-block__title'):
                    channel_data = dm.RssChannelData()

                    channel_data.str_channel_title = div_content.span.text.encode("UTF-8")
                    channel_data.str_last_build_date = ''
                    channel_data.str_channel_page_link = div_content.a['href']
                    channel_data.str_channel_language = 'cn'
                    channel_data.str_channel_atom_link = div_content.contents[1].contents[3].attrs['href']
                    channel_data.str_channel_description = div_content.contents[1].contents[1].contents[3].text.encode(
                        "UTF-8")

                    channel_list.append(channel_data)

                else:
                    continue
        elif self.site_original_name == '':

        if channel_list.__len__() > 0:
            for channel in channel_list:
                DATA_MANAGER.insert_Rss_Channel_Data(channel)


if __name__ == '__main__':
    voa_site = NewsSite({'site_name': 'voachinese'})
    voa_site.init_site_channels()
