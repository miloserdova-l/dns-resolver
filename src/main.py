from resolver import DNSResolver
from dnslib.server import DNSServer, DNSLogger
from time import sleep


if __name__ == "__main__":
    resolver = DNSResolver()
    logger = DNSLogger(prefix=False, logf=lambda s: print(s.upper()))
    server = DNSServer(resolver, address="localhost", logger=logger)
    server.start_thread()

    try:
        while server.isAlive():
            sleep(1)
    except KeyboardInterrupt:
        pass
