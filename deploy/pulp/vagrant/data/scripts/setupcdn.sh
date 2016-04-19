#!/bin/bash

F_INJECTFILE="/tmp/cdn_inject";

yum install wget httpd mod_ssl -y;
ln -s /var/lib/pulp /var/www/streamer;
echo "SSLInsecureRenegotiation On" > $F_INJECTFILE;
sed -i "/#SSLCryptoDevice ubsec/r $F_INJECTFILE" /etc/httpd/conf.d/ssl.conf &> /dev/null;
systemctl enable httpd;
systemctl start httpd;
