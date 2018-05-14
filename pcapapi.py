# !/usr/bin/env python
try:
    import scapy.all as scapy
except ImportError:
    import scapy

import os

try:
    # This import works from the project directory
    import scapy_http.http
except ImportError:
    # If you installed this package via pip, you just need to execute this
    from scapy.layers import http

import networkx as nx
import matplotlib.pyplot as plt

from networkx.algorithms.community import k_clique_communities

import datamanager as dm

import time

PCAP_PATH = '/home/user/Data/Satellite/251_email/original/input/'
OUTPUT_PATH = '/home/user/Data/Satellite/251_email/output/'

PCAP_FILE = '20180308_dump_file'

HOST_LIST = []
SRC_DST_DIC = {}
TUNNEL_LIST = {}

# size limit of pcap file, in bytes
MAX_PCAP_FILE_SIZE = 10010000
CURRENT_WORK_PATH = ''
TEMP_PATH = 'tmp'

DATA_MANAGER = dm.DataManagerTools()


def draw_netwrok_graph():
    graph = nx.Graph()

    for node in HOST_LIST:
        graph.add_node(node)

    # for item_key in SRC_DST_DIC.keys():
    #     for peer in SRC_DST_DIC[item_key]:
    #         graph.add_edge(item_key, peer)

    for item_key in TUNNEL_LIST.keys():
        for peer_turple in TUNNEL_LIST[item_key]:
            peer_name = peer_turple[0]
            peer_protocol = peer_turple[1]

            graph.add_edge(item_key, peer_name)

    klist = list(k_clique_communities(graph, 3))

    # nx.draw_networkx_nodes(graph, pos)
    # nx.draw_networkx_labels(graph, pos)
    # nx.draw_networkx_edges(graph, pos)
    # nx.draw_networkx_edge_labels(graph, pos)

    pos = nx.spring_layout(graph)
    plt.clf()
    nx.draw(graph, pos=pos, with_labels=False)

    if klist.__len__() > 1:
        nx.draw(graph, pos=pos, nodelist=klist[0], node_color='b')
        nx.draw(graph, pos=pos, nodelist=klist[1], node_color='y')

    elif klist.__len__() > 0:
        nx.draw(graph, pos=pos, nodelist=klist[0], node_color='b')

    plt.show()


def handle_files_in_directory(dir_name):
    path = dir_name

    for file_name in os.listdir(path):

        os.chdir(path)

        fullname = os.path.join(path, file_name)

        # is file
        if os.path.isfile(fullname):

            # split the big pcap file into smaller ones
            if os.path.getsize(fullname) > MAX_PCAP_FILE_SIZE:
                split_command = 'tcpdump -r %s -w %s/split -C %d' % (
                fullname, (CURRENT_WORK_PATH + '/' + TEMP_PATH), MAX_PCAP_FILE_SIZE / 1000000)
                os.system(split_command)

                os.chdir(CURRENT_WORK_PATH + '/' + TEMP_PATH + '/')

                tmp_path = os.getcwd()

                # handle the smaller pcap files recursively
                for tmp_file in os.listdir(tmp_path):

                    tmp_full_name = os.path.join(tmp_path, tmp_file)

                    if os.path.isfile(tmp_full_name) and os.path.getsize(tmp_full_name) <= MAX_PCAP_FILE_SIZE:
                        start_time = time.time()

                        handle_pcap_file(tmp_full_name)

                        end_time = time.time()
                        time_collaps = end_time - start_time

                        print('=' * 10 + '\tHandled file: {0} in {1} seconds.'.format(tmp_full_name,
                                                                                      time_collaps) + '=' * 10)

            else:
                start_time = time.time()

                handle_pcap_file(fullname)

                end_time = time.time()
                time_collaps = end_time - start_time

                print('=' * 10 + '\tHandled file: {0} in {1} seconds.'.format(fullname, time_collaps) + '=' * 10)

        remove_command = 'rm ' + fullname
        os.system(remove_command)


def save_dns_info(dns_query_list):
    if dns_query_list is not None:
        dns_data = dm.DnsData(dns_query_list)
        DATA_MANAGER.insert_dns_data(dns_data)


def handle_pcap_file(file_name):
    print '=' * 78
    print 'Starting process ' + file_name

    # try:
    #     file = os.path.split(file_name)[1]
    #
    #     if not os.path.isdir(OUTPUT_PATH):
    #         os.mkdir(OUTPUT_PATH)
    #
    #     back_file = open(OUTPUT_PATH + file + ".output", "w+")
    #
    # except IOError, err:
    #     print ('IOError: ' + err)

    packets = scapy.rdpcap(file_name)

    temp_index = 0

    for p in packets:

        temp_index += 1
        init_data = {}

        # print '=' * 78
        # print 'Packet No. [%d] ,\tPacket Protocol [%s]' % (p.fields['id'], p.name)
        # back_file.write('=' * 78 + '\n')
        # back_file.write('Packet No. [%d] ,\tPacket Protocol [%s]' % (p.fields['id'], p.name) + '\n')

        try:

            src_ip = p.fields['src']
            dst_ip = p.fields['dst']

            # if dst_ip not in HOST_LIST:
            #     HOST_LIST.append(dst_ip)
            #
            # if src_ip not in HOST_LIST:
            #     HOST_LIST.append(src_ip)
            #
            # if src_ip not in SRC_DST_DIC.keys():
            #     SRC_DST_DIC[src_ip] = []
            #
            # if dst_ip not in SRC_DST_DIC[src_ip]:
            #     SRC_DST_DIC[src_ip].append(dst_ip)

            init_data['pcap_item_number'] = str(p.fields['id'])
            init_data['ip_src_addr'] = p.fields['src']
            init_data['ip_dst_addr'] = p.fields['dst']

            counter = 1

            while p.name != 'NoPayload':
                content = '\t' * counter + ' - ' + 'Layer ' + str(counter) + ': ' + p.name

                if p.name == 'IP':
                    content = content + (' From [%s] to [%s]' % (p.fields['src'], p.fields['dst']))

                    # a gre tunnel
                    if p.payload.name == 'GRE' and p.payload.payload.name == 'IP':

                        gre_src_ip = p.payload.payload.fields['src']
                        gre_dst_ip = p.payload.payload.fields['dst']

                        if 'gre_lv1_src_addr' not in init_data.keys():
                            init_data['gre_lv1_src_addr'] = gre_src_ip
                            init_data['gre_lv1_dst_addr'] = gre_dst_ip
                        else:
                            if 'gre_lv2_src_addr' not in init_data.keys():
                                init_data['gre_lv2_src_addr'] = gre_src_ip
                                init_data['gre_lv2_dst_addr'] = gre_dst_ip

                        # if gre_dst_ip not in HOST_LIST:
                        #     HOST_LIST.append(gre_dst_ip)
                        #
                        # if gre_src_ip not in HOST_LIST:
                        #     HOST_LIST.append(gre_src_ip)
                        #
                        # if gre_src_ip not in TUNNEL_LIST.keys():
                        #     TUNNEL_LIST[gre_src_ip] = []

                        temp_p = p.payload
                        protocol_name = p.payload.name

                        while temp_p.payload.name != 'NoPayload':
                            protocol_name = protocol_name + '-' + temp_p.payload.name
                            temp_p = temp_p.payload

                        # if (gre_dst_ip, protocol_name) not in TUNNEL_LIST[gre_src_ip]:
                        #     TUNNEL_LIST[gre_src_ip].append((gre_dst_ip, protocol_name))

                        content = content + (' , with tunnel from [%s] to [%s]' % (gre_src_ip, gre_dst_ip))

                elif p.name == 'TCP' or p.name == 'UDP':
                    content = content + (' From port:[%s] to port:[%s]' % (p.fields['sport'], p.fields['dport']))

                    init_data['trans_protocol_name'] = p.name
                    init_data['trans_src_port'] = p.fields['sport']
                    init_data['trans_dst_port'] = p.fields['dport']

                    if p.payload.name != 'NoPayload':
                        init_data['app_protocol_name'] = p.payload.name

                elif p.name == 'HTTP' and p.payload.name == 'HTTP Response':
                    content = content + ' ' + p.payload.fields['Status-Line']

                # elif p.name == 'HTTP' and p.payload.name == 'Raw':
                #     content = content + ' ' + p.payload.original
                # print content
                # back_file.write(content + '\n')

                elif p.name == 'DNS':

                    dns_result = {}

                    query_site = p.fields['an']

                    if query_site is not None:

                        query_site_name = query_site.fields['rrname']
                        query_site_alias = query_site.fields['rdata']

                        dns_result['site_name'] = query_site_name
                        dns_result['site_alias'] = query_site_alias

                        query_answer = []
                        temp_payload = query_site.payload

                        while temp_payload.name != 'NoPayload':
                            query_answer.append((temp_payload.fields['rrname'], temp_payload.fields['rdata']))
                            temp_payload = temp_payload.payload

                        dns_result['site_answer'] = query_answer

                        save_dns_info(dns_result)

                        break

                p = p.payload
                counter = counter + 1

        except Exception, e:
            print ('=' * 15 + '\tError occured during parsing some pcap data. Error message is: {0}.'.format(e.message))

        pcap_data = dm.PcapData(init_data)
        DATA_MANAGER.insert_pcap_data(pcap_data)

        if temp_index % 1000 == 0:
            print ('=' * 10 + '\t[{0}] Pcap Packet is inserted.'.format(temp_index))

        #
        # if temp_index == 2655:
        #     print ('=' * 10 + '\t[{0}] Pcap Packet is inserted.'.format(temp_index))

    # back_file.close()


if __name__ == '__main__':
    # filename = PCAP_PATH + PCAP_FILE

    # handle_pcap_file('/home/user/Documents/satellite/dump/20180308_dump_file10')

    # draw_netwrok_graph()

    CURRENT_WORK_PATH = os.getcwd()

    command = 'mkdir %s' % TEMP_PATH

    os.system(command)

    try:
        handle_files_in_directory(PCAP_PATH)

        command = 'rm -r {0}'.format(PCAP_PATH)
        os.system(command)

    except Exception, e:
        print 'Exception occured, message is {0}'.format(e.message)

    finally:
        command = 'rm -r %s' % (CURRENT_WORK_PATH + '/tmp')
        os.system(command)
    #
    #     print 'Host List: '
    #     print HOST_LIST
    #
    #     print 'IP Src_Dst_dic:'
    #     print SRC_DST_DIC
    #
    #     print 'Tunnel List:'
    #     print TUNNEL_LIST
