#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Tcp Port Forwarding (Reverse Proxy)
# Author : WangYihang <wangyihanger@gmail.com>

import socket
import threading
import time

class TcpProxy(object):

    def __init__(self, config, log, fake_dns, callback):
        self.callback = callback
        self.log = log
        self.local_host = config.get('proxy', 'bind_ip')
        self.port = int(config.get('proxy', 'bind_port'))
        self.max_connection = int(config.get('proxy', 'max_connection'))
        self.fake_dns = fake_dns
        self.server_socket = None
        self.local_socket = None
        self.remote_socket = None
        self.local_address = None
        self.threads = []
        self.started = False

    def start(self):
        while self.fake_dns.last_domain is None:
            time.sleep(5)
            self.log.info('Waiting 5s for DNS resolution before starting proxy')
        self.started = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.local_host, self.port))
        self.server_socket.listen(self.max_connection)
        self.log.info('[TcpProxy] Server started [%s:%d]' % (self.local_host, self.port))
        while self.started:
            self.local_socket, self.local_address = self.server_socket.accept()
            self.log.info('[TcpProxy] Connect to [%s:%d] to get the content of [%s:%d]' % (
                self.local_host, self.port, self.fake_dns.last_domain, self.port))
            self.log.info('[TcpProxy] Detect connection from [%s:%s]' % (self.local_address[0], self.local_address[1]))
            self.log.info("[TcpProxy] Trying to connect the REMOTE server [%s:%d]" % (self.fake_dns.last_domain, self.port))
            self.remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.remote_socket.connect((self.fake_dns.last_domain, self.port))
            self.log.info("[TcpProxy] Tunnel connected! Tranfering data...")
            s = threading.Thread(target=self.transfer, args=(
                self.remote_socket, self.local_socket, False))
            r = threading.Thread(target=self.transfer, args=(
                self.local_socket, self.remote_socket, True))
            self.threads.append(s)
            self.threads.append(r)
            s.start()
            r.start()

    @staticmethod
    def debug_callback(log, data, src_address, src_port, dst_address, dst_port, direction):
        if direction:
            log.debug("[TcpProxy] %s:%d >>> %s:%d [%d]" % (src_address, src_port, dst_address, dst_port, len(data)))
        else:
            log.debug("[TcpProxy] %s:%d <<< %s:%d [%d]" % (dst_address, dst_port, src_address, src_port, len(data)))
        log.debug(':'.join('%02x' % ord(c) for c in data))

    def transfer(self, src, dst, direction):
        src_name = src.getsockname()
        src_address = src_name[0]
        src_port = src_name[1]
        dst_name = dst.getsockname()
        dst_address = dst_name[0]
        dst_port = dst_name[1]
        while self.started:
            buffer = src.recv(0x400)
            if len(buffer) == 0:
                self.log.info("[-] No data received! Breaking...")
                break
            self.callback(buffer, src_address, src_port, dst_address, dst_port, direction)
            dst.send(buffer)
        self.log.info("[TcpProxy] Closing connections! [%s:%d]" % (src_address, src_port))
        src.shutdown(socket.SHUT_RDWR)
        src.close()

    def close(self):
        self.started = False
        self.log.info("[TcpProxy] Releasing resources...")
        if self.remote_socket is not None:
            self.remote_socket.shutdown()
            self.remote_socket.close()
        if self.local_socket is not None:
            self.local_socket.shutdown()
            self.local_socket.close()
        self.log.info("[TcpProxy] Closing server...")
        self.server_socket.close()
        self.log.info("[TcpProxy] Server shuted down!")
