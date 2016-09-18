#!/usr/bin/env bash
# Cory Nance
# FreeIPA server install script
# 9/15/2016

# source: https://gist.github.com/econchick/58e2885bef9f76d4d977

SERVER_IP_ADDR=192.168.19.15
SERVER_FQDN=`hostname`
SERVER_NAME=`hostname | cut -d. -f 1 | tr '[:upper:]' '[:lower:]'`
IPA_REALM=TEST.NET
IPA_DOMAIN=test.net
FORWARDER=10.0.2.3
PASSWORD=password

# update the server and install packages
yum update -y
yum install ipa-server bind-dyndb-ldap ipa-server-dns -y

# configure hosts file
echo "Configuring /etc/hosts"
echo "127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4" > /etc/hosts
echo "::1 localhost localhost.localdomain localhost6 localhost6.localdomain6" >> /etc/hosts
ips=$(ip addr show | grep 'inet ' | tail -2 | awk '{print $2}' | awk -F "/" '{print $1}')
for ip in $ips; do
	echo "$ip `hostname` `hostname -s`" >> /etc/hosts
done

# configure resolv.conf
echo "Configuring /etc/resolv.conf"
echo "search $IPA_DOMAIN" > /etc/resolv.conf
echo "nameserver $SERVER_IP_ADDR" >> /etc/resolv.conf
echo "nameserver $FORWARDER" >> /etc/resolv.conf
echo "nameserver 8.8.4.4" >> /etc/resolv.conf

# install IPA server
ipa-server-install --setup-dns --forwarder=$FORWARDER -r $IPA_REALM --hostname=$SERVER_FQDN -n $IPA_DOMAIN -a $PASSWORD -p $PASSWORD -U

# test kinit
echo $PASSWORD | kinit admin



