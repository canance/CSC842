#!/usr/bin/env python3

# Cory Nance
# dns_proxy.py: Proxy and log DNS requests.
# 8 October 2016

from datetime import datetime
from dnslib import DNSRecord
import argparse
import socket
import csv


class DNS_Proxy:
	"""
	Proxy DNS requests that are received to a specified DNS server
	"""

	_qtypes = {
		1:'A', 2:'NS', 5:'CNAME', 6:'SOA', 12:'PTR', 15:'MX',
        16:'TXT', 17:'RP', 18:'AFSDB', 24:'SIG', 25:'KEY', 28:'AAAA',
        29:'LOC', 33:'SRV', 35:'NAPTR', 36:'KX', 37:'CERT', 38:'A6',
        39:'DNAME', 41:'OPT', 42:'APL', 43:'DS', 44:'SSHFP',
        45:'IPSECKEY', 46:'RRSIG', 47:'NSEC', 48:'DNSKEY', 49:'DHCID',
        50:'NSEC3', 51:'NSEC3PARAM', 52:'TLSA', 55:'HIP', 99:'SPF',
        249:'TKEY', 250:'TSIG', 251:'IXFR', 252:'AXFR', 255:'ANY',
        257:'TYPE257', 32768:'TA', 32769:'DLV',
    }

	def __init__(self, bind_address='127.0.0.1', bind_port=5053, dns_server='8.8.8.8', dns_port=53, output_path='output.csv'):
		"""
		Specify the remote dns_server IP and port as well as the local instance's bind address and port
		"""
		self.dns_server = dns_server
		self.dns_port = dns_port
		self.bind_address = bind_address
		self.bind_port = bind_port
		self.outfile = open(output_path, 'w', newline='')
		self.csvwriter = csv.writer(self.outfile)
		self.format_str = '%-30s%-20s%-10s%-20s%-20s'
		self.header_printed = False
		self.header = ('Time', 'IP', 'Type', 'Question', 'Record')
		

	def _dns_lookup(self, data):
		"""
		Passes the data to the specified dns_server and returns the response
		"""
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.sendto(data, (self.dns_server, self.dns_port))
		return sock.recvfrom(4096)[0] # (data, addr)


	def _write_log(self, addr, data):
		"""
		Writes a new row in the csvfile
		"""

		# first row?
		if not self.header_printed:
			self.csvwriter.writerow(self.header)
			print(self.format_str % self.header)
			self.header_printed = True

		# get data
		record = DNSRecord.parse(data)
		qtype = self._qtypes[record.questions[0].qtype]
		request = str(record.questions[0].qname)
		response = record.rr[0].rdata
		row = (datetime.now().isoformat(), addr[0], qtype, request, response)
		
		# log and print data
		self.csvwriter.writerow(row)
		print(self.format_str % row)


	def run(self):
		"""
		Starts the server listening and waits for a connection
		"""
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			sock.bind((self.bind_address, self.bind_port))
			print("[*INFO] Listening on %s:%d\n" % (self.bind_address, self.bind_port))

			while True:
			    data, addr = sock.recvfrom(4096)
			    response = self._dns_lookup(data)
			    sock.sendto(response, addr)
			    self._write_log(addr, response)

		except KeyboardInterrupt:
			self._cleanup()


	def _cleanup(self):
		print('\n[*INFO] Cleaning up...')
		self.outfile.close()


if __name__ == '__main__':
	"""
	Run the server
	"""
	parser = argparse.ArgumentParser(description='This script will run a proxy server on the specified IP/port and proxy the queries to the specified DNS server and back to the requester.  Each request is logged in the specified file.')
	parser.add_argument('--bind-ip', type=str, default='127.0.0.1', help='Address the server should bind to.  The default is 127.0.0.1.')
	parser.add_argument('--bind-port', type=int, default=5053, help='Port the server should bind to.  The default is 5053.')
	parser.add_argument('--dns-ip', type=str, default='8.8.8.8', help='Address of the DNS server that should be queried.  The default is 8.8.8.8.')
	parser.add_argument('--dns-port', type=int, default=53, help='Port of the DNS server that should be queried.  The default is 53.')
	parser.add_argument('--output', type=str, default='output.csv', help='Path the output CSV file.  The default value is output.csv.')
	args = parser.parse_args()
	
	kwargs = {
		'bind_address': args.bind_ip,
		'bind_port': args.bind_port,
		'dns_server': args.dns_ip,
		'dns_port': args.dns_port,
		'output_path': args.output,
	}

	server = DNS_Proxy(**kwargs)
	server.run()
