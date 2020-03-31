#/usr/bash

#This script creates a new certificate authority, then generates a client certificate issued by that CA

# Generate the CA key 
export password="SomePassword123!"
openssl genrsa -aes256 -passout pass:$password -out ca.pass.key 4096
openssl rsa -passin pass:$password  -in ca.pass.key -out ca.key
rm ca.pass.key
echo "#### ENTER THE CA DETAILS ####"
openssl req -new -x509 -days 3650 -key ca.key -out ca.pem

# Generate the client keu
export CLIENT_ID="web-client-01"
export CLIENT_SERIAL=01

openssl genrsa -aes256 -passout pass:$password -out $CLIENT_ID.pass.key 4096
openssl rsa -passin pass:$password -in $CLIENT_ID.pass.key -out $CLIENT_ID.key
rm CLIENT_ID.pass.key

#Generate the client CSR
echo "#### ENTER THE CLIENT DETAILS ####"
openssl req -new -key $CLIENT_ID.key -out $CLIENT_ID.csr

#Generate the client cert
openssl x509 -req -days 3650 -in $CLIENT_ID.csr -CA ca.pem -CAkey ca.key -set_serial $CLIENT_SERIAL -out $CLIENT_ID.pem