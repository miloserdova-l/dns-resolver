import dns.message
import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype
from dnslib import RR, QTYPE, A
from dnslib.server import BaseResolver


class DNSResolver(BaseResolver):
    # https://root-servers.org/
    ROOT_SERVERS = (
        "198.41.0.4",
        "199.9.14.201",
        "192.33.4.12",
        "199.7.91.13",
        "192.203.230.10",
        "192.5.5.241",
        "192.112.36.4",
        "198.97.190.53",
        "192.36.148.17",
        "192.58.128.30",
        "193.0.14.129",
        "199.7.83.42",
        "202.12.27.33"
    )

    def __init__(self):
        super()
        self.domain_cache = {}

    def resolve(self, request, handler):
        reply = request.reply()
        name = request.q.qname
        response = self.__find(str(name))
        if response:
            for answers in response.answer:
                for answer in answers:
                    if answer.rdtype == dns.rdatatype.A:
                        reply.add_answer(RR(name, QTYPE.A, rdata=A(str(answer)), ttl=60))
        return reply

    def __find(self, name: str) -> dns.message.Message:
        target_name: dns.name = dns.name.from_text(name)
        split = str(target_name).split(".")
        domain = split[len(split) - 2]
        if domain not in self.domain_cache:
            self.domain_cache[domain] = {}

        for root_server in self.ROOT_SERVERS:
            if root_server in self.domain_cache[domain]:
                response = self.domain_cache[domain][root_server]
            else:
                response = self.__make_request(target_name, root_server)
                self.domain_cache[domain][root_server] = response
            if not response:
                continue

            if response.answer:
                return response
            elif response.additional:
                for additional in response.additional:
                    if additional.rdtype != dns.rdatatype.A:
                        continue
                    for add in additional:
                        new_response = self.__find_recursive(target_name, str(add))
                        if new_response:
                            return new_response
        return None

    def __find_recursive(
            self,
            target_name: dns.name.Name,
            ip_address: str
    ) -> dns.message.Message:
        response = self.__make_request(target_name, ip_address)
        if not response:
            return None
        if response.answer:
            return response
        elif response.additional:
            for additional in response.additional:
                if additional.rdtype != dns.rdatatype.A:
                    continue
                for add in additional:
                    ip = str(add)
                    new_response = self.__find_recursive(target_name, ip)
                    if new_response:
                        return new_response
        return response

    @staticmethod
    def __make_request(
            target_name: dns.name.Name,
            ip_address: str
    ) -> dns.message.Message:
        outbound_query = dns.message.make_query(target_name, dns.rdatatype.A)
        try:
            response = dns.query.udp(outbound_query, ip_address)
        except Exception:
            response = None
        return response
