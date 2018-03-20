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

PCAP_PATH = '/home/mi1w0rm/Data/251_email/original/'
PCAP_FILE = '20180308_dump_file'

HOST_LIST = []
SRC_DST_DIC = {}
TUNNEL_LIST = {}

# size limit of pcap file, in bytes
MAX_PCAP_FILE_SIZE = 10010000
CURRENT_WORK_PATH = ''
TEMP_PATH = 'tmp'


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

        fullname = os.path.join(path, file_name)

        print '=' * 78
        print 'Handling File: [%s] .' % fullname

        # is file
        if os.path.isfile(fullname):

            # split the big pcap file into smaller ones
            if os.path.getsize(fullname) > MAX_PCAP_FILE_SIZE:
                command = 'tcpdump -r %s -w tmp/split -C %d' % (fullname, MAX_PCAP_FILE_SIZE / 1000000)

                os.system(command)

                os.chdir('tmp')

                tmp_path = os.getcwd()

                # handle the smaller pcap files recursively
                for tmp_file in os.listdir(tmp_path):

                    tmp_full_name = os.path.join(tmp_path, tmp_file)

                    if os.path.isfile(tmp_full_name) and os.path.getsize(tmp_full_name) <= MAX_PCAP_FILE_SIZE:
                        print '\t\tHandling Splited File: [%s] .' % tmp_full_name

                        handle_pcap_file(tmp_full_name)


def handle_pcap_file(file_name):
    """
    Handle the single pcap file and extract each packet info in it .
    Each packet info of each protocol should be write into a data file.

        IP:             From [Src_IP] to [Dst_IP]
        GRE tunnel:     tunnel From [Src_IP] to [Dst_IP]
        TCP:            From port:[Src_Port] to port:[Dst_Port]
        HTTP Response:  HTTP Status-Line content

    Args:
        file_name: The full path of the pcap file

    Returns:

    Raises:

    """

    packets = scapy.rdpcap(file_name)

    for p in packets:

        # print '=' * 78
        # print 'Packet No. [%d] ,\tPacket Protocol [%s]' % (p.fields['id'], p.name)

        src_ip = p.fields['src']
        dst_ip = p.fields['dst']

        if dst_ip not in HOST_LIST:
            HOST_LIST.append(dst_ip)

        if src_ip not in HOST_LIST:
            HOST_LIST.append(src_ip)

        if src_ip not in SRC_DST_DIC.keys():
            SRC_DST_DIC[src_ip] = []

        if dst_ip not in SRC_DST_DIC[src_ip]:
            SRC_DST_DIC[src_ip].append(dst_ip)

        counter = 1

        while p.name != 'NoPayload':
            content = '\t' * counter + ' - ' + 'Layer ' + str(counter) + ': ' + p.name

            if p.name == 'IP':
                content = content + (' From [%s] to [%s]' % (p.fields['src'], p.fields['dst']))

                # a gre tunnel
                if p.payload.name == 'GRE' and p.payload.payload.name == 'IP':

                    gre_src_ip = p.payload.payload.fields['src']
                    gre_dst_ip = p.payload.payload.fields['dst']

                    if gre_dst_ip not in HOST_LIST:
                        HOST_LIST.append(gre_dst_ip)

                    if gre_src_ip not in HOST_LIST:
                        HOST_LIST.append(gre_src_ip)

                    if gre_src_ip not in TUNNEL_LIST.keys():
                        TUNNEL_LIST[gre_src_ip] = []

                    temp_p = p.payload
                    protocol_name = p.payload.name

                    while temp_p.payload.name != 'NoPayload':
                        protocol_name = protocol_name + '-' + temp_p.payload.name
                        temp_p = temp_p.payload

                    if (gre_dst_ip, protocol_name) not in TUNNEL_LIST[gre_src_ip]:
                        TUNNEL_LIST[gre_src_ip].append((gre_dst_ip, protocol_name))

                    content = content + (' , with tunnel from [%s] to [%s]' % (gre_src_ip, gre_dst_ip))

            elif p.name == 'TCP':
                content = content + (' From port:[%s] to port:[%s]' % (p.fields['sport'], p.fields['dport']))

            elif p.name == 'HTTP' and p.payload.name == 'HTTP Response':
                content = content + ' ' + p.payload.fields['Status-Line']

            # elif p.name == 'HTTP' and p.payload.name == 'Raw':
            #     content = content + ' ' + p.payload.original

            # print content

            p = p.payload

            counter = counter + 1


if __name__ == '__main__':
    filename = PCAP_PATH + PCAP_FILE

    # handle_pcap_file('/home/user/Documents/satellite/dump/20180308_dump_file10')
    #
    # draw_netwrok_graph()

    CURRENT_WORK_PATH = os.getcwd()

    command = 'mkdir %s' % TEMP_PATH

    os.system(command)

    try:
        handle_files_in_directory(PCAP_PATH)

    except:
        print 'exception...'

    finally:
        command = 'rm -r %s' % (CURRENT_WORK_PATH + '/tmp')
        os.system(command)

        print 'Host List: '
        print HOST_LIST

        print 'IP Src_Dst_dic:'
        print SRC_DST_DIC

        print 'Tunnel List:'
        print TUNNEL_LIST
