#!/usr/bin/env bash
# Cory Nance
# FreeIPA client install script
# 9/15/2016

# source: https://gist.github.com/econchick/d461058791281e45ec17

SERVER_IP_ADDR=192.168.19.15
SERVER_FQDN=ipaserver.test.net
SERVER_NAME=ipaserver
IPA_REALM=TEST.NET
IPA_DOMAIN=test.net
CLIENT_IP_ADDR=192.168.19.20
CLIENT_FQDN=`hostname`
CLIENT_NAME=`hostname | cut -d. -f 1 | tr '[:upper:]' '[:lower:]'`
PASSWORD=password

echo "Configuring /etc/hosts ..."
echo "127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4" > /etc/hosts
echo "::1 	localhost localhost.localdomain localhost6 localhost6.localdomain6" >> /etc/hosts
echo "$CLIENT_IP_ADDR    $CLIENT_FQDN $CLIENT_NAME" >> /etc/hosts
echo "192.168.19.25      vncserver.test.net vncserver" >> /etc/hosts

echo "Configuring /etc/resolv.conf"
echo "search $IPA_DOMAIN" > /etc/resolv.conf
echo "nameserver $SERVER_IP_ADDR" >> /etc/resolv.conf

# updating and install ipa-client and apache2
yum update -y
yum install ipa-client ipa-admintools httpd mod_auth_kerb -y

# edit /etc/krb5.conf
sed -i 's/# default_realm = EXAMPLE.COM/ default_realm = TEST.NET/g' /etc/krb5.conf

echo "Installing IPA client ..."
ipa-client-install --enable-dns-updates --ssh-trust-dns -p admin -w $PASSWORD -U

echo "Testing kinit"
echo $PASSWORD | kinit admin

echo "Enrolling Apache as a service on the IPA Server"
ipa service-add HTTP/$CLIENT_FQDN

echo "Getting keytab from IPA Server to Client"
ipa-getkeytab -s $SERVER_FQDN -p HTTP/$CLIENT_FQDN -k /etc/httpd/http.keytab

echo "Changing ownership of keytab"
chown apache:apache /etc/httpd/http.keytab

echo "Testing Apache keytab"
kinit -kt /etc/httpd/http.keytab -p HTTP/$CLIENT_FQDN

echo "Re-kiniting as admin"
echo $PASSWORD | kinit admin