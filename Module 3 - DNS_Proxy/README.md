# DNS_Proxy

## Purpose
The idea for this script came from Saumil Shah.  Saumil requested:
> A DNS proxy that logs all DNS query requests. Perhaps such a tool already exists, but I've not come across an easy to deploy implementation. Modifying dnsmasq to do this would be the shortest path.

Rather than modifying `dnsmasq` I thought this would be a good opportunity to play with sockets in Python.  Indeed it was and I also learned of a library called `dnslib` that can parse DNS queries.


## Summary 

The script is setup to listen on the specified address and port for UDP connections.  Once one is received it hands it off to a DNS server, receives the response, logs the data to a CSV file, and ultimately relays the response back to the requestor.  


## Dependencies
- Python 3
- dnslib

## Usage
```
usage: dns_proxy.py [-h] [--bind-ip BIND_IP] [--bind-port BIND_PORT]
                    [--dns-ip DNS_IP] [--dns-port DNS_PORT] [--output OUTPUT]

This script will run a proxy server on the specified IP/port and proxy the
queries to the specified DNS server and back to the requester. Each request is
logged in the specified file.

optional arguments:
  -h, --help            show this help message and exit
  --bind-ip BIND_IP     Address the server should bind to. The default is
                        127.0.0.1.
  --bind-port BIND_PORT
                        Port the server should bind to. The default is 5053.
  --dns-ip DNS_IP       Address of the DNS server that should be queried. The
                        default is 8.8.8.8.
  --dns-port DNS_PORT   Port of the DNS server that should be queried. The
                        default is 53.
  --output OUTPUT       Path the output CSV file. The default value is
                        output.csv.
```


## Future Development
- Use the server built into dnslib
- Save all DNS Questions and Resource Records (currently only saving the first of each)
- Add zone files to override the default responses





