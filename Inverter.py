import TcpProxy
import pprint
import InverterMsg
import FakeDNS

def callback(data, src_address, src_port, dst_address, dst_port, direction):
    TcpProxy.TcpProxy.debug_callback(data, src_address, src_port, dst_address, dst_port, direction)
    if not direction and len(data) > 140:
        msg = InverterMsg.InverterMsg(data)
        pp = pprint.PrettyPrinter()
        pp.pprint(msg.dict())


def main():
    LOCAL_HOST = '0.0.0.0'
    PORT = 10000
    MAX_CONNECTION = 1
    fake_dns = FakeDNS.FakeDNS()
    tcp_proxy = TcpProxy.TcpProxy(LOCAL_HOST, PORT, fake_dns, MAX_CONNECTION, callback)
    try:
        fake_dns.start()
        tcp_proxy.start()
    except KeyboardInterrupt:
        tcp_proxy.close()
        fake_dns.close()


if __name__ == "__main__":
    main()
