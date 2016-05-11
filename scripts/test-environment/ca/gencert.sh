#!/bin/bash
THEID=$1;
openssl genrsa -out intermediate/private/${THEID}.key.pem 2048
chmod 400 intermediate/private/${THEID}.key.pem 2048;
openssl req -config intermediate/openssl.cnf -key intermediate/private/${THEID}.key.pem -new -sha256 -out intermediate/csr/${THEID}.csr.pem -subj "/C=GB/ST=London/L=/O=CentOS Devcloud/OU=CCCP/CN=${THEID}";
openssl ca -config intermediate/openssl.cnf -extensions server_cert -days 375 -notext -md sha256 -in intermediate/csr/${THEID}.csr.pem -out intermediate/certs/${THEID}.cert.pem;
chmod 444 intermediate/certs/${THEID}.cert.pem
