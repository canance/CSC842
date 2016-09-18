# Cory Nance
# vnc server install script
# 9/15/2016


SERVER_IP_ADDR=192.168.19.15
SERVER_FQDN=ipaserver.test.net
SERVER_NAME=ipaserver
IPA_REALM=TEST.NET
IPA_DOMAIN=test.net
CLIENT_IP_ADDR=192.168.19.25
CLIENT_FQDN=`hostname`
CLIENT_NAME=`hostname | cut -d. -f 1 | tr '[:upper:]' '[:lower:]'`
PASSWORD=password

# configure /etc/hosts
echo "Configuring /etc/hosts ..."
echo "127.0.0.1 localhost localhost.localdomain localhost4 localhost4.localdomain4" > /etc/hosts
echo "::1 	localhost localhost.localdomain localhost6 localhost6.localdomain6" >> /etc/hosts
echo "$CLIENT_IP_ADDR    $CLIENT_FQDN $CLIENT_NAME" >> /etc/hosts
echo "192.168.19.20      client.test.net client" >> /etc/hosts
echo "192.168.19.15      ipaserver.test.net ipaserver" >> /etc/hosts

# configure /etc/resolv.conf
echo "Configuring /etc/resolv.conf"
echo "search $IPA_DOMAIN" > /etc/resolv.conf
echo "nameserver $SERVER_IP_ADDR" >> /etc/resolv.conf

# update and install software packages
yum update -y
yum groupinstall "Desktop" "Desktop Platform" "X Window System" "Fonts" -y
yum install xorg-x11-fonts-Type1 tigervnc-server ipa-client ipa-admintools -y

# edit /etc/krb5.conf
sed -i 's/# default_realm = EXAMPLE.COM/ default_realm = TEST.NET/g' /etc/krb5.conf

echo "Installing IPA client ..."
ipa-client-install --enable-dns-updates --ssh-trust-dns -p admin -w $PASSWORD -U

echo "Testing kinit"
echo $PASSWORD | kinit admin

