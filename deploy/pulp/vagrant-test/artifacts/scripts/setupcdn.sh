#!/bin/bash

F_INJECTFILE="/tmp/cdn_inject";
F_PULPCONF="/etc/httpd/conf.d/pulp_docker.conf";

yum install wget httpd mod_ssl -y;
ln -s /var/lib/pulp /var/www/streamer;
echo "SSLInsecureRenegotiation On" > $F_INJECTFILE;
sed -i "/#SSLCryptoDevice ubsec/r $F_INJECTFILE" /etc/httpd/conf.d/ssl.conf &> /dev/null;
cat <<EOF >> $F_PULPCONF
#
# Apache configuration file for Pulp's Docker support
#

# -- HTTPS Repositories ---------

# This prevents mod_mime_magic from adding content-type and content-encoding headers, which will confuse the Docker
# client.
MimeMagicFile NEVER_EVER_USE

# Docker v2
Alias /pulp/docker/v2 /var/www/streamer/docker/v2/web
<Directory /var/www/pub/docker/v2/web>
    Header set Docker-Distribution-API-Version "registry/2.0"
    SSLRequireSSL
    Options FollowSymlinks Indexes
</Directory>

# Docker v1
Alias /pulp/docker/v1 /var/www/streamer/docker/v1/web
<Directory /var/www/pub/docker/v1/web>
    SSLRequireSSL
    Options FollowSymLinks Indexes
</Directory>
EOF
systemctl enable httpd;
systemctl start httpd;
