#!/usr/bin/env python3

# Cory Nance
# detectnet.py - This script/tool will detect the network scope of the network in which the machine that is running it
#                is attached. It will report back the network IP, subnet, gateway, and list of live hosts within that
#                range.
# 26 August 2016

import os
import sys
import shutil
import socket
import argparse
import ipaddress
import subprocess
from threading import Thread


def windows():
    """
    Uses the ipconfig command to create a dict containing the hostname and list of interfaces.
    Each interface contains name, ip_address, subnet_mask, and gateway. 
    :return: The dict containing hostname and interfaces.
    """
    ipconfig_output = subprocess.check_output(['ipconfig', '/all'], universal_newlines=True)
    interfaces = []
    for line in ipconfig_output.split('\n'):
        line = line.strip()

        if line.startswith('Host Name'):
            host = line.split(': ')[1]
        elif line.startswith('Ethernet adapter'):
            name = line[17:-1]
        elif line.startswith('Physical Address'):
            mac = line.split(': ')[1]
        elif line.startswith('IPv4 Address'):
            ip_address = line.split(': ')[1].split('(')[0]
        elif line.startswith('Subnet Mask'):
            mask = line.split(': ')[1]
        elif line.startswith('Default Gateway'):
            gateway = line.split(': ')[1]
        elif line.startswith('NetBIOS over Tcpip'):
            interface = {
                'name': name,
                'mac': mac,
                'ip': ip_address,
                'subnet_mask': mask,
                'gateway': gateway,
            }
            interfaces.append(interface)
    return {
        'hostname': host,
        'interfaces': interfaces,
    }


def ifconfig(macOS=False):
    """
    Uses the ifconfig command to create a dict containing the hostname and list of interfaces.
    Each interface contains name, ip_address, subnet_mask, and gateway.
    :return: The dict containing hostname and interfaces.
    """
    # grab hostname
    host = subprocess.check_output('hostname', universal_newlines=True).strip()

    # get interfaces, ips, and subnet masks
    ifconfig_output = subprocess.check_output('ifconfig', universal_newlines=True)
    interfaces = []
    for line in ifconfig_output.split('\n'):
        if not line.startswith(' ') and not line.startswith('\t'):
            name = line.split(':')[0]

        if name in ['lo', 'lo0']:
            continue

        line = line.strip()
        if line.startswith('inet '):
            tokens = line.split()
            ip_address = tokens[1]
            mask = tokens[3]
            if mask.startswith('0x'):
                octets = [mask[2:][i:i+2] for i in range(0, len(mask), 2)]
                octets = [str(int(octet, 16)) for octet in octets[:-1]]
                mask = '.'.join(octets)
            interface = {
                'name': name,
                'ip': ip_address,
                'subnet_mask': mask,
                'gateway': '',
            }
            interfaces.append(interface)

    # get default route for interfaces
    cmd = ['route', '-n']
    if macOS:
        cmd += ['get', 'default']
    route_output = subprocess.check_output(cmd, universal_newlines=True)
    for line in route_output.split('\n'):
        if macOS:
            line = line.strip()
            if line.startswith('gateway'):
                gateway = line.split(': ')[1]
            elif line.startswith('interface'):
                name = line.split(': ')[1]
        else:
            tokens = line.split()
            if len(tokens) > 0 and tokens[0] == '0.0.0.0':
                name = tokens[7]
                gateway = tokens[1]

    for interface in interfaces:
        if interface['name'] == name:
            interface['gateway'] = gateway

    return {
        'hostname': host,
        'interfaces': interfaces,
    }


def ip():
    """
    Uses the ip command to create a dict containing the hostname and list of interfaces.
    Each interface contains name, ip_address, subnet_mask, and gateway. 
    :return: The dict containing hostname and interfaces.
    """
    # grab hostname
    host = subprocess.check_output('hostname', universal_newlines=True).strip()

    # get interfaces, ips, and subnet masks
    ip_output = subprocess.check_output(['ip', 'addr', 'show'], universal_newlines=True)
    interfaces = []
    for line in ip_output.split('\n'):
        if len(line) > 0 and line[0].isdigit():
            name = line.split(':')[1].split(':')[0].strip()

        if name == 'lo':
            continue

        line = line.strip()
        if line.startswith('inet '):
            tokens = line.split()
            ipv4_interface = ipaddress.IPv4Interface(tokens[1])
            ip_address = str(ipv4_interface.ip)
            mask = str(ipv4_interface.netmask)

            interface = {
                'name': name,
                'ip': ip_address,
                'subnet_mask': mask,
            }
            interfaces.append(interface)

    # get default route for interfaces
    ip_output = subprocess.check_output(['ip', 'route', 'show'], universal_newlines=True)
    for line in ip_output.split('\n'):
        if line.startswith('default'):
            tokens = line.split()
            gateway = tokens[2]
            name = tokens[4]
            for interface in interfaces:
                if interface['name'] == name:
                    interface['gateway'] = gateway

    return {
        'hostname': host,
        'interfaces': interfaces,
    }


def linux():
    """
    Checks whether ip or ifconfig is installed
    :return: a dict containing hostname and interfaces
    """
    # check for ip or ifconfig
    if shutil.which('ip'):
        return ip()
    elif shutil.which('ifconfig'):
        return ifconfig()
    else:
        print('ip or ifconfig are required!', file=sys.stderr)


def ping(address, valid_hosts):
    """
    Pings the address 1 time
    :param address: address to ping
    :param valid_hosts: a running list of valid outs
    :return: None
    """
    if sys.platform in ['Windows', 'win32']:
        try:
            ping_output = subprocess.check_output(['ping', address, '-n', '1'], universal_newlines=True)
            if 'Destination host unreachable' in ping_output:
                return
        except subprocess.CalledProcessError:
            return  # non-zero exit code
    else:
        ping_output = subprocess.run(['ping', '-c', '1', address], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        success = ping_output.returncode
        if success != 0:
            return
    try:
        hostname = socket.gethostbyaddr(address)[0]
    except socket.herror:
        hostname = ''  # host not found
    valid_hosts.append((address, hostname))


def find_hosts(network, valid_hosts, thread_count=20):
    """
    Loops through each ip address in the network and tries to ping it.
    :param network: IPv4Network object of the network to scan.
    :param valid_hosts: a running list of valid hosts that have been found.
    :param thread_count: number of threads to use for running the ping command.
    :return: None
    """
    threads = []
    for address in network:
        if address in [network.broadcast_address, network.network_address]:
            continue
        thread = Thread(target=ping, args=(str(address), valid_hosts))
        thread.start()
        threads.append(thread)
        while len(threads) > thread_count:
            for thread in threads:
                thread.join(0.1)
                if not thread.isAlive():
                    threads.remove(thread)
                    break

    for thread in threads:
        thread.join()


def print_data(data, out=sys.stdout):
    """
    Formats data returned from ip(), ifconfig(), or windows() and prints it to out.
    :param data: the dict returned from ip(), ifconfig(), or windows()
    :param out: where to send the output
    :return: None
    """
    hostname = 'Hostname: %s' % data['hostname']
    print(hostname, file=out)
    print('-' * len(hostname), file=out)
    for interface in data['interfaces']:
        print('Interface: %s' % interface['name'], file=out)
        print('\t%-20s%-10s' % ('IP', interface['ip']), file=out)
        print('\t%-20s%-10s' % ('Subnet Mask', interface['subnet_mask']), file=out)
        print('\t%-20s%-10s' % ('Gateway', interface['gateway']), file=out)
        print(file=out)


def print_hosts(valid_hosts, out=sys.stdout):
    """
    Formats valid_hosts and prints it to out.
    :param valid_hosts: a list of tuples containing (ip_address, hostname)
    :param out: where to send the output
    :return: None
    """
    print("Hosts:", file=out)
    print('\t%-20s%-20s' % ('IP', 'Hostname'), file=out)
    for address, hostname in valid_hosts:
        print('\t%-20s%-20s' % (address, hostname), file=out)


def main():
    """
    Determine what OS the script is running on.  Dispatch to the correct function
    in order to find interface data.  Then print data out to the terminal or specified file.
    :return: None
    """
    # parse args
    parser = argparse.ArgumentParser(
        description="""
        This script/tool will detect the network scope of the network in which the machine that is running it is
        attached. It will report back the network IP, subnet, gateway, and list of live hosts within that range.
        """)
    parser.add_argument('--threads', help='maximum number of threads to use', type=int, default=20)
    parser.add_argument('--out', help='send output to a text file', default=sys.stdout)
    parser.add_argument('--no-scan', help='skip scanning for live hosts', action='store_true')
    args = parser.parse_args()

    # check platform
    if sys.platform in ['linux', 'linux2']:
        data = linux()
    elif sys.platform == 'darwin':
        data = ifconfig(macOS=True)
    elif sys.platform in ['Windows', 'win32']:
        data = windows()
    else:
        print("Unrecognized platform detected: %s" % sys.platform, file=sys.stderr)
        sys.exit(1)

    if args.out == sys.stdout:
        print_data(data)
    else:
        with open(args.out, 'w') as out:
            print_data(data, out)

    if not args.no_scan:
        # find other hosts on networks
        valid_hosts = []
        for interface in data['interfaces']:
            if interface['gateway'] == '':
                continue
            iface = ipaddress.IPv4Interface('%s/%s' % (interface['ip'], interface['subnet_mask']))
            find_hosts(iface.network, valid_hosts, args.threads)

        if args.out == sys.stdout:
            print_hosts(valid_hosts)
        else:
            with open(args.out, 'a') as out:
                print_hosts(valid_hosts, out)


if __name__ == '__main__':
    main()
