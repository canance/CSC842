# Module 1 - detectnet.py

## Purpose
This script will detect the network scope of the network in which the machine that is running it is attached.  It will report back the hostname, interfaces, and list of live hosts within that range.  Each interface consists of a name, network IP, subnet, and gateway.


## Usage
```
usage: detectnet.py [-h] [--threads THREADS] [--out OUT] [--no-scan]

This script will detect the network scope of the network in which the machine
that is running it is attached. It will report back the hostname, interfaces,
and list of live hosts within that range. Each interface consists of a name,
network IP, subnet, and gateway.

optional arguments:
  -h, --help         show this help message and exit
  --threads THREADS  maximum number of threads to use
  --out OUT          send output to a text file
  --no-scan          skip scanning for live hosts
```

## Testing
This script has been tested and is working on:
- Mac OS X El Capitan
- Windows 10
- Linux

## Further Ideas
- Incorporate `nmap` for network scanning
- Use `scapy` for network scanning
- Create different output formats (HTML, JSON, etc)
- Add ability to FTP the data to a central server


## Dependencies

### Windows
- `ipconfig`

### Linux
- `hostname`
- `ip` or `ifconfig`

### Mac OSX
- `hostname`
- `ifconfig`

## Installation
This script requires Python 3.3 or higher.  All libraries used should be included with a standard Python installation.
