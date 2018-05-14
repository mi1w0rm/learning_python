# !/usr/bin/env python

import MySQLdb as mdb

CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'passwd': 'satsumacar*(%',
    # 'db': 'Afghanistan_Intelligence',
    'charset': 'utf8'
}

SITE_ID_VOACHINESE = 1


class PcapData(object):
    # pcap item unique id
    pcap_item_number = ''

    # ip address
    ip_src_addr = ''
    ip_dst_addr = ''

    # gre protocol ip address, optional
    gre_lv1_src_addr = ''
    gre_lv1_dst_addr = ''
    gre_lv2_src_addr = ''
    gre_lv2_dst_addr = ''

    # transportation protocol name : tcp / udp
    trans_protocol_name = ''

    # transportation protocol ports
    trans_src_port = 0
    trans_dst_port = 0

    # network level protocol name
    ip_protocol_name = ''

    # application level protocol name
    app_protocol_name = ''

    def __init__(self, initdata={}):

        if 'pcap_item_number' in initdata.keys():
            self.pcap_item_number = initdata['pcap_item_number']
        if 'ip_src_addr' in initdata.keys():
            self.ip_src_addr = initdata['ip_src_addr']
        if 'ip_dst_addr' in initdata.keys():
            self.ip_dst_addr = initdata['ip_dst_addr']
        if 'gre_lv1_src_addr' in initdata.keys():
            self.gre_lv1_src_addr = initdata['gre_lv1_src_addr']
        if 'gre_lv1_dst_addr' in initdata.keys():
            self.gre_lv1_dst_addr = initdata['gre_lv1_dst_addr']
        if 'gre_lv2_src_addr' in initdata.keys():
            self.gre_lv2_src_addr = initdata['gre_lv2_src_addr']
        if 'gre_lv2_dst_addr' in initdata.keys():
            self.gre_lv2_dst_addr = initdata['gre_lv2_dst_addr']
        if 'trans_protocol_name' in initdata.keys():
            self.trans_protocol_name = initdata['trans_protocol_name']
        if 'trans_src_port' in initdata.keys():
            self.trans_src_port = initdata['trans_src_port']
        if 'trans_dst_port' in initdata.keys():
            self.trans_dst_port = initdata['trans_dst_port']
        if 'ip_protocol_name' in initdata.keys():
            self.ip_protocol_name = initdata['ip_protocol_name']
        if 'app_protocol_name' in initdata.keys():
            self.app_protocol_name = initdata['app_protocol_name']


class DnsData(object):
    # site original name
    site_original_name = ''

    # site alias name, optional
    site_alias_name = ''

    # site name-address pair list
    site_ip_addr_pair = []

    def __init__(self, initdata={}):

        if 'site_name' in initdata.keys():
            self.site_original_name = initdata['site_name']
        if 'site_alias' in initdata.keys():
            self.site_alias_name = initdata['site_alias']
        if 'site_answer' in initdata.keys():
            self.site_ip_addr_pair = initdata['site_answer']


class RssChannelData(object):
    # rss site id
    i_site_id = ''

    # rss channel name
    str_channel_title = ''

    # rss channel page link
    str_channel_page_link = ''

    # rss channel atom link, which contains the news feed
    str_channel_atom_link = ''

    # rss channel description
    str_channel_description = ''

    # rss channel language, like en, cn, etc
    str_channel_language = ''

    # rss channel last modified time, like Wed, 02 May 2018 10:35:10 +0800
    str_last_build_date = ''

    def __init__(self, initdata={}):

        if 'str_site_name' in initdata.keys():
            if initdata['str_site_name'] == 'voachinese':
                self.i_site_id = SITE_ID_VOACHINESE
        if 'str_channel_title' in initdata.keys():
            self.str_channel_title = initdata['str_channel_title']
        if 'str_channel_page_link' in initdata.keys():
            self.str_channel_page_link = initdata['str_channel_page_link']
        if 'str_channel_atom_link' in initdata.keys():
            self.str_channel_atom_link = initdata['str_channel_atom_link']
        if 'str_channel_description' in initdata.keys():
            self.str_channel_description = initdata['str_channel_description']
        if 'str_channel_language' in initdata.keys():
            self.str_channel_language = initdata['str_channel_language']
        if 'str_last_build_date' in initdata.keys():
            self.str_last_build_date = initdata['str_last_build_date']


class DataManagerTools(object):
    """docstring for MySQLTools"""
    conn = None

    def __init__(self, config=CONFIG):
        self.conn = mdb.connect(**config)
        self.conn.autocommit(True)

    def get_connection(self):
        if self.conn is not None:
            return self.conn

        else:
            self.conn = mdb.connect(**CONFIG)
            self.conn.autocommit(True)

            return self.conn

    def insert_item(self, sql, *param):
        cursor = self.conn.cursor()
        cursor.execute(sql, param)

    """     
        INSERT INTO `Afghanistan_Intelligence`.`tb_pcap_summary`
        (`i_pcap_item_number`,
        `str_ip_src_addr`,
        `str_ip_dst_addr`,
        `str_gre_lv1_src_addr`,
        `str_gre_lv1_dst_addr`,
        `str_gre_lv2_src_addr`,
        `str_gre_lv2_dst_addr`,
        `str_trans_protocol`,
        `i_trans_src_port`,
        `i_trans_dst_port`,
        `str_network_protocol`,
        `str_application_protocol`)
        VALUES
        (<{i_pcap_item_number: }>,
        <{str_ip_src_addr: }>,
        <{str_ip_dst_addr: }>,
        <{str_gre_lv1_src_addr: }>,
        <{str_gre_lv1_dst_addr: }>,
        <{str_gre_lv2_src_addr: }>,
        <{str_gre_lv2_dst_addr: }>,
        <{str_trans_protocol: }>,
        <{i_trans_src_port: }>,
        <{i_trans_dst_port: }>,
        <{str_network_protocol: }>,
        <{str_application_protocol: }>);
    
    """

    def insert_pcap_data(self, data=PcapData):

        myconn = self.get_connection()

        sql = "INSERT INTO Afghanistan_Intelligence.tb_pcap_summary " \
              "(`i_pcap_item_number`, `str_ip_src_addr`, `str_ip_dst_addr`, " \
              "`str_gre_lv1_src_addr`, `str_gre_lv1_dst_addr`, `str_gre_lv2_src_addr`, " \
              "`str_gre_lv2_dst_addr`,  `str_trans_protocol`, `i_trans_src_port`, " \
              "`i_trans_dst_port`, `str_network_protocol`, `str_application_protocol`) " \
              "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, %d, '%s', '%s')" \
              % (data.pcap_item_number, data.ip_src_addr, data.ip_dst_addr, data.gre_lv1_src_addr,
                 data.gre_lv1_dst_addr, data.gre_lv2_src_addr, data.gre_lv2_dst_addr, data.trans_protocol_name,
                 data.trans_src_port, data.trans_dst_port, data.ip_protocol_name, data.app_protocol_name)

        sql = sql.encode('utf-8')

        try:
            myconn.cursor().execute(sql)

        except mdb.IntegrityError as dbie:
            print('----[%s] mdb.IntegrityError......' % (data.pcap_item_number))

        except mdb.OperationalError as dboe:
            print('--------Insert [%s] mdb.OperationalError......' % (data.pcap_item_number))

        except mdb.ProgrammingError as pe:
            print('--------[%s] mdb.ProgrammingError, and message is %s......' % (data.pcap_item_number, pe))

    '''
        Need to further unit test
    '''

    def insert_batch_pcap_data(self, data_list):

        myconn = self.get_connection()

        insert_list = []

        sql = "INSERT INTO Afghanistan_Intelligence.tb_pcap_summary " \
              "(`i_pcap_item_number`, `str_ip_src_addr`, `str_ip_dst_addr`, " \
              "`str_gre_lv1_src_addr`, `str_gre_lv1_dst_addr`, `str_gre_lv2_src_addr`, " \
              "`str_gre_lv2_dst_addr`,  `str_trans_protocol`, `i_trans_src_port`, " \
              "`i_trans_dst_port`, `str_network_protocol`, `str_application_protocol`) " \
              "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, %d, '%s', '%s')"

        if isinstance(data_list, list):
            for data in data_list:
                if isinstance(data, PcapData):
                    insert_item = (data.pcap_item_number, data.ip_src_addr, data.ip_dst_addr, data.gre_lv1_src_addr,
                                   data.gre_lv1_dst_addr, data.gre_lv2_src_addr, data.gre_lv2_dst_addr,
                                   data.trans_protocol_name, data.trans_src_port, data.trans_dst_port,
                                   data.ip_protocol_name, data.app_protocol_name)
                    insert_list.append(insert_item)
                else:
                    continue

        try:
            myconn.cursor().executemany(sql, insert_list)

        except mdb.IntegrityError as dbie:
            print('----[%s] mdb.IntegrityError......' % (data.site_original_name))

        except mdb.OperationalError as dboe:
            print('--------Insert [%s] mdb.OperationalError......' % (data.site_original_name))

        except mdb.ProgrammingError as pe:
            print('--------[%s] mdb.ProgrammingError, and message is %s......' % (data.site_original_name, pe))

    """
        INSERT INTO `Afghanistan_Intelligence`.`tb_dns_query_result`
        (`id_dns_item_index`,
        `str_site_original_name`,
        `str_site_alias_name`,
        `str_site_ip_addr`)
        VALUES
        (<{id_dns_item_index: }>,
        <{str_site_original_name: }>,
        <{str_site_alias_name: }>,
        <{str_site_ip_addr: }>);

    """

    def insert_dns_data(self, data=DnsData):

        myconn = self.get_connection()

        sql = "INSERT INTO Afghanistan_Intelligence.tb_dns_query_result " \
              "(`str_site_original_name`, `str_site_alias_name`, `str_site_ip_addr`) " \
              "VALUES (%s, %s, %s)"

        insert_list = []

        if data.site_ip_addr_pair.__len__():
            for pair in data.site_ip_addr_pair:
                insert_item = (data.site_original_name, data.site_alias_name, pair[1])
                insert_list.append(insert_item)
        else:
            insert_item = (data.site_original_name, data.site_alias_name, '')
            insert_list.append(insert_item)

        try:
            myconn.cursor().executemany(sql, insert_list)

        except mdb.IntegrityError as dbie:
            print('----[%s] mdb.IntegrityError......' % (data.site_original_name))

        except mdb.OperationalError as dboe:
            print('--------Insert [%s] mdb.OperationalError......' % (data.site_original_name))

        except mdb.ProgrammingError as pe:
            print('--------[%s] mdb.ProgrammingError, and message is %s......' % (data.site_original_name, pe))

    '''
        INSERT INTO `rss_news_feed`.`tb_site_channel`
        (`idx_channel`,
        `id_site`,
        `str_channel_title`,
        `str_channel_page_link`,
        `str_channel_atom_link`,
        `str_channel_description`,
        `str_channel_language`,
        `str_last_build_date`)
        VALUES
        (<{idx_channel: }>,
        <{id_site: }>,
        <{str_channel_title: }>,
        <{str_channel_page_link: }>,
        <{str_channel_atom_link: }>,
        <{str_channel_description: }>,
        <{str_channel_language: }>,
        <{str_last_build_date: }>);
        
    '''

    def insert_Rss_Channel_Data(self, data=RssChannelData):

        myconn = self.get_connection()

        sql = "INSERT INTO `rss_news_feed`.`tb_site_channel` (`id_site`, `str_channel_title`, `str_channel_page_link`, " \
              "`str_channel_atom_link`, `str_channel_description`, `str_channel_language`) " \
              " VALUES (1, '%s', '%s', '%s', '%s', '%s');" % (data.str_channel_title, data.str_channel_page_link,
                                                              data.str_channel_atom_link, data.str_channel_description,
                                                              data.str_channel_language)

        # insert_list = []

        # for data in data_list:
        # insert_item = (1, data.str_channel_title, data.str_channel_page_link, data.str_channel_atom_link,
        #                data.str_channel_description, data.str_channel_language)

        # insert_list.append(insert_item)

        try:
            # myconn.cursor().executemany(sql, insert_list)

            myconn.cursor().execute(sql)

        except mdb.IntegrityError as dbie:
            print('---- mdb.IntegrityError, and message is %s ......' % (dbie))

        except mdb.OperationalError as dboe:
            print('-------- mdb.OperationalError, and message is %s ......' % (dboe))

        except mdb.ProgrammingError as pe:
            print('-------- mdb.ProgrammingError, and message is %s......' % (pe))
