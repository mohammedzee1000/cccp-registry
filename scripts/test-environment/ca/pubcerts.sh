#!/bin/sh
INTDIR="/root/ca/intermediate";
HTTPDIR="/var/www/html";
CATRUST="ca-chain.cert.pem";
INTKEY="intermediate.key.pem";
INTCERT="intermediate.cert.pem";

CRTDIR="${INTDIR}/certs";
PRIVDIR="${INTDIR}/private";


HCERTSDIR="${HTTPDIR}/certs";
HCADIR="${HCERTSDIR}/ca";
HCRTDIR="${HCERTSDIR}/crt";
HPRIVDIR="${HCERTSDIR}/tls/private";
INDEXFILE="${HTTPDIR}/index.html";

PCADIR="certs/ca";
PCRTDIR="certs/crt";
PPRIVDIR="certs/tls/private";

echo "Initializing...";

if [ ! -d ${HCERTSDIR} ]; then
	mkdir -p ${HCERTSDIR};
fi

if [ ! -d ${HCADIR} ]; then
	mkdir -p ${HCADIR};
fi

if [ ! -d ${HCRTDIR} ]; then
	mkdir -p ${HCRTDIR};
fi

if [ ! -d ${HPRIVDIR} ]; then
	mkdir -p ${HPRIVDIR};
fi

echo "Exporting certs to http server : ";

echo "CA Certifcate : ${PCADIR}/${CATRUST} <br /><br />" > ${INDEXFILE};
rm -rf "${HCERTSDIR}/${CATRUST}"
cp "${CRTDIR}/${CATRUST}" "${HCADIR}/${CATRUST}";

echo "Private Keys : <br /><br />" >> ${INDEXFILE};
echo "<code>">> ${INDEXFILE};

# Copy all private keys
rm -rf ${HPRIVDIR}/*;
for privitem in `ls ${PRIVDIR}`; do

	if [ "${privitem}" != "${INTKEY}" ]; then
		
		echo "${PPRIVDIR}/${privitem} <br />" >> ${INDEXFILE};
		cp "${PRIVDIR}/${privitem}" "${HPRIVDIR}/${privitem}";
	fi
done
echo "</code><br />" >> ${INDEXFILE}

echo "<br /> Public Keys : <br /><br />" >> ${INDEXFILE};
echo "<code>">> ${INDEXFILE};

# Copy all public keys
rm -rf ${HCRTDIR}/*;
for privitem in `ls ${CRTDIR}`; do

	if [ "${privitem}" != "${CATRUST}" -a "${privitem}" != ${INTCERT} ]; then
		
		echo "${PCRTDIR}/${privitem} <br />" >> ${INDEXFILE};
		cp "${CRTDIR}/${privitem}" "${HCRTDIR}/${privitem}";
	fi
done
echo "</code>">> ${INDEXFILE};

# Handle perms
chmod -R 777 ${HCERTSDIR};

echo "Index : ";
cat ${INDEXFILE};

