## {{{ http://code.activestate.com/recipes/491264/ (r4)
import socket
import threading


class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''

        tipo = (ord(data[2]) >> 3) & 15  # Opcode bits
        if tipo == 0:  # Standard query
            ini = 12
            lon = ord(data[ini])
            while lon != 0:
                self.domain += data[ini + 1:ini + lon + 1] + '.'
                ini += lon + 1
                lon = ord(data[ini])

    def response(self, ip):
        packet = ''
        if self.domain:
            packet += self.data[:2] + "\x81\x80"
            packet += self.data[4:6] + self.data[4:6] + '\x00\x00\x00\x00'  # Questions and Answers Counts
            packet += self.data[12:]  # Original Domain Name Question
            packet += '\xc0\x0c'  # Pointer to domain name
            packet += '\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
            packet += str.join('', map(lambda x: chr(int(x)), ip.split('.')))  # 4bytes of IP
        return packet


class FakeDNS(object):

    def __init__(self, log, config):
        self.log = log
        self.ip = config['fakedns']['target_ip']
        self.log.info('[FakeDNS] Entry:: dom.query. 60 IN A %s' % self.ip)
        self.udps = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.last_domain = config['fakedns']['initial_domain']
        self.started = False

    def start(self):
        self.started = True
        self.udps.settimeout(1)
        self.udps.bind(('', 53))
        thread = threading.Thread(target=self.loop)
        thread.start()

    def close(self):
        self.log.info('[FakeDNS] Finalize')
        self.udps.close()
        self.started = False

    def loop(self):
        while self.started:
            try:
                data, addr = self.udps.recvfrom(1024)
                p = DNSQuery(data)
                self.udps.sendto(p.response(self.ip), addr)
                self.last_domain = p.domain
                self.log.info('[FakeDNS] Response: %s -> %s' % (p.domain, self.ip))
            except socket.timeout:
                pass


if __name__ == '__main__':

    fake_dns = FakeDNS()
    try:
        fake_dns.start()
        while 1:
            pass
    except KeyboardInterrupt:
        fake_dns.close()
