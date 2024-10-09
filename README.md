**Intro**
This web-server framework simulate how certificate chaining can be deployed when communicating handshakes across 2 web-browsers.

**Generate Root Certificate (self-signed)**  
```
# Generate root private key    
openssl genrsa -out rootCA.key 2048

# Generate root certificate    
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 1024 -out rootCA.crt -subj "/C=AU/ST=VIC/O=Khoa/CN=rootCA"
```

**Generate IntermediateA Certificate (signed by Root)**  
```
# Generate Intermediate A private key    
openssl genrsa -out intermediateA.key 2048

# Create Intermediate A CSR    
openssl req -new -key intermediateA.key -out intermediateA.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=IntermediateA"

# Sign Intermediate A CSR with Root CA     
openssl x509 -req -in intermediateA.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out intermediateA.crt -days 500 -sha256 -extfile openssl_intermediate.cnf -extensions v3_intermediate_ca
```

**Generate IntermediateB Certificate (signed by IntermediateA)**  
```
# Generate Intermediate B private key  
openssl genrsa -out intermediateB.key 2048

# Create Intermediate B CSR  
openssl req -new -key intermediateB.key -out intermediateB.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=IntermediateB"

# Sign Intermediate B CSR with Intermediate A  
openssl x509 -req -in intermediateB.csr -CA intermediateA.crt -CAkey intermediateA.key -CAcreateserial -out intermediateB.crt -days 500 -sha256 -extfile openssl_intermediate.cnf -extensions v3_intermediate_ca
```


**Generate Host1 and Host2 Certificates (signed by IntermediateB)**  
# Host1 
```
openssl genrsa -out host1.key 2048
openssl req -new -key host1.key -out host1.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=host1"
openssl x509 -req -in host1.csr -CA intermediateB.crt -CAkey intermediateB.key -CAcreateserial -out host1.crt -days 500 -sha256 -extfile openssl_host.cnf -extensions v3_req
```

# Host2 
```
openssl genrsa -out host2.key 2048
openssl req -new -key host2.key -out host2.csr -subj "/C=AU/ST=VIC/O=Khoa/CN=host2"
openssl x509 -req -in host2.csr -CA intermediateB.crt -CAkey intermediateB.key -CAcreateserial -out host2.crt -days 500 -sha256 -extfile openssl_enduser.cnf -extensions v3_end_user
```


Hint: You can just download the certs chaining configured. Or deploying them using bash command, either way.


**Concatenate Certificates for Verification**  
```
# Concatenate Intermediate Certificates for Chain Verification  
cat intermediateB.crt intermediateA.crt > chain_intermediateB_A.crt

# Verify the Certificate Chain  
openssl verify -CAfile rootCA.crt -untrusted intermediateA.crt intermediateB.crt
openssl verify -CAfile rootCA.crt -untrusted chain_intermediateB_A.crt host1.crt
openssl verify -CAfile rootCA.crt -untrusted chain_intermediateB_A.crt host2.crt

# Create Full Chains for Host Certs  
cat host1.crt intermediateB.crt intermediateA.crt rootCA.crt > fullchain_host1.crt
cat host2.crt intermediateB.crt intermediateA.crt rootCA.crt > fullchain_host2.crt

# Verify the Full Chains    
openssl verify -CAfile rootCA.crt -untrusted chain_intermediateB_A.crt fullchain_host1.crt
openssl verify -CAfile rootCA.crt -untrusted chain_intermediateB_A.crt fullchain_host2.crt
```

**Usage**  
```
python3 -m http.server 8080
```
```
python3 server.py fullchain_host1.crt host1.key rootCA.crt
```


Once deploy your server and localhost port, access the website via  
http://localhost:8080/user1.html  
http://localhost:8080/user2.html
