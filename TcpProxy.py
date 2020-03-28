#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Tcp Port Forwarding (Reverse Proxy)
# Author : WangYihang <wangyihanger@gmail.com>

import socket
import threading

class TcpProxy(object):

    def __init__(self, local_host, port, fake_dns, max_connection, callback):
        self.callback = callback
        self.local_host = local_host
        self.port = port
        self.fake_dns = fake_dns
        self.max_connection = max_connection
        self.server_socket = None
        self.local_socket = None
        self.remote_socket = None
        self.local_address = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.local_host, self.port))
        self.server_socket.listen(self.max_connection)
        print '[+] Server started [%s:%d]' % (self.local_host, self.port)
        while True:
            self.local_socket, self.local_address = self.server_socket.accept()
            print '[+] Connect to [%s:%d] to get the content of [%s:%d]' % (
                self.local_host, self.port, self.fake_dns.last_domain, self.port)
            print '[+] Detect connection from [%s:%s]' % (self.local_address[0], self.local_address[1])
            print "[+] Trying to connect the REMOTE server [%s:%d]" % (self.fake_dns.last_domain, self.port)
            self.remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.remote_socket.connect((self.fake_dns.last_domain, self.port))
            print "[+] Tunnel connected! Tranfering data..."
            # threads = []
            s = threading.Thread(target=self.transfer, args=(
                self.remote_socket, self.local_socket, False))
            r = threading.Thread(target=self.transfer, args=(
                self.local_socket, self.remote_socket, False))
            # threads.append(s)
            # threads.append(r)
            s.start()
            r.start()

    @staticmethod
    def debug_callback(data, src_address, src_port, dst_address, dst_port, direction):
        if direction:
            print "[+] %s:%d >>> %s:%d [%d]" % (src_address, src_port, dst_address, dst_port, len(data))
        else:
            print "[+] %s:%d <<< %s:%d [%d]" % (dst_address, dst_port, src_address, src_port, len(data))
        print ':'.join('%02x' % ord(c) for c in data)

    def transfer(self, src, dst, direction):
        src_name = src.getsockname()
        src_address = src_name[0]
        src_port = src_name[1]
        dst_name = dst.getsockname()
        dst_address = dst_name[0]
        dst_port = dst_name[1]
        while True:
            buffer = src.recv(0x400)
            if len(buffer) == 0:
                print "[-] No data received! Breaking..."
                print src.getdefaulttimeout()
                break
            self.callback(buffer, src_address, src_port, dst_address, dst_port, direction)
            dst.send(buffer)
        print "[+] Closing connections! [%s:%d]" % (src_address, src_port)
        src.shutdown(socket.SHUT_RDWR)
        src.close()

    def close(self):
        print "[+] Releasing resources..."
        if self.remote_socket is not None:
            self.remote_socket.close()
        if self.local_socket is not None:
            self.local_socket.close()
        print "[+] Closing server..."
        self.server_socket.close()
        print "[+] Server shuted down!"
