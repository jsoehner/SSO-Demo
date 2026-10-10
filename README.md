➜  SSO-Demo git:(main) ✗ python3 run_demo_v2_fixed.py 


=== STAGE 0: Init & Port Scanning ===
[INFO] EJBCA HTTPS: localhost:443
[INFO] EJBCA HTTP:  localhost:80
[INFO] Keycloak:    localhost:8080
Cleaning up old containers...
[CMD] docker-compose down -v --remove-orphans
[+] down 8/8
 ✔ Container ejbca               Removed                                                                                                                                                                   1.3s
 ✔ Container keycloak            Removed                                                                                                                                                                   0.2s
 ✔ Container postgres            Removed                                                                                                                                                                   0.1s
 ✔ Container mariadb             Removed                                                                                                                                                                   0.4s
 ✔ Volume sso-demo_mariadb_data  Removed                                                                                                                                                                   0.0s
 ✔ Volume sso-demo_ejbca_data    Removed                                                                                                                                                                   0.0s
 ✔ Volume sso-demo_postgres_data Removed                                                                                                                                                                   0.0s
 ✔ Network sso-demo_pki-network  Removed                                                                                                                                                                   0.2s
Generating docker-compose.yml...

=== STAGE 1: Starting Keycloak & Postgres ===
[CMD] docker-compose up -d keycloak
[+] up 4/4
 ✔ Network sso-demo_pki-network  Created                                                                                                                                                                   0.0s
 ✔ Volume sso-demo_postgres_data Created                                                                                                                                                                   0.0s
 ✔ Container postgres            Healthy                                                                                                                                                                   5.7s
 ✔ Container keycloak            Started                                                                                                                                                                   5.7s
[INFO] PostgreSQL Database is ONLINE.                         
[INFO] Keycloak Service is ONLINE.                         

=== STAGE 2: Starting EJBCA & MariaDB ===
[CMD] docker-compose up -d ejbca
[+] up 4/4
 ✔ Volume sso-demo_ejbca_data   Created                                                                                                                                                                    0.0s
 ✔ Volume sso-demo_mariadb_data Created                                                                                                                                                                    0.0s
 ✔ Container mariadb            Started                                                                                                                                                                    0.2s
 ✔ Container ejbca              Started                                                                                                                                                                    0.2s
[INFO] MariaDB Database is ONLINE.                         
[INFO] EJBCA Service is ONLINE.                         

=== STAGE 3: PKI Config ===
[PKI] Creating and configuring cryptotoken...
[CMD] docker exec ejbca /opt/keyfactor/bin/ejbca.sh cryptotoken create --token PQCToken --pin foo123 --type SoftCryptoToken --autoactivate TRUE
2026-03-30 21:56:13,816+0000 INFO  [org.ejbca.ui.cli.cryptotoken.CryptoTokenCreateCommand] (main) CryptoToken with id -260928852 created successfully.
[PKI] Generating ML-DSA-65 PQC key (this takes ~60 seconds)...
[CMD] docker exec ejbca /opt/keyfactor/bin/ejbca.sh cryptotoken generatekey --token PQCToken --alias signKey --keyspec ML-DSA-65
2026-03-30 21:56:15,778+0000 INFO  [org.ejbca.ui.cli.cryptotoken.CryptoTokenGenerateCommand] (main) Key pair generated successfully.
[PKI] Generating RSA2048 default key...
[CMD] docker exec ejbca /opt/keyfactor/bin/ejbca.sh cryptotoken generatekey --token PQCToken --alias defaultKey --keyspec RSA2048
2026-03-30 21:56:17,786+0000 INFO  [org.ejbca.ui.cli.cryptotoken.CryptoTokenGenerateCommand] (main) Key pair generated successfully.
[PKI] Generating RSA2048 test key...
[CMD] docker exec ejbca /opt/keyfactor/bin/ejbca.sh cryptotoken generatekey --token PQCToken --alias testKey --keyspec RSA2048
2026-03-30 21:56:20,016+0000 INFO  [org.ejbca.ui.cli.cryptotoken.CryptoTokenGenerateCommand] (main) Key pair generated successfully.
[PKI] Initializing Management CA with ML-DSA-65 keys...
[CMD] docker exec ejbca /opt/keyfactor/bin/ejbca.sh ca init "PQCRootCA" "CN=PQC Root CA,O=JSIGroup,C=local" soft "foo123" ML-DSA-65 ML-DSA-65 3650 null ML-DSA-65
2026-03-30 21:56:21,791+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Initializing CA
2026-03-30 21:56:21,791+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Generating rootCA keystore:
2026-03-30 21:56:21,791+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA Type:x509
2026-03-30 21:56:21,791+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA name: PQCRootCA
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) SuperAdmin CN: null
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) DN: CN=PQC Root CA,O=JSIGroup,C=local
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA token type: soft
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA token password: hidden
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Keytype: ML-DSA-65
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Keyspec: ML-DSA-65
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Validity: 3650d
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Policy ID: null
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Signature alg: ML-DSA-65
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Certificate profile: ROOTCA
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA token properties: {}
2026-03-30 21:56:21,792+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Signed by: Self signed
2026-03-30 21:56:21,795+0000 INFO  [org.ejbca.ui.cli.ca.BaseCaAdminCommand] (main) Initalizing authorization module with caid=1541684306 and superadmin CN 'null'.
2026-03-30 21:56:22,508+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Creating CA...
2026-03-30 21:56:22,609+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CAId for created CA: 1541684306
2026-03-30 21:56:22,609+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Created and published initial CRL.
2026-03-30 21:56:22,609+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA initialized
2026-03-30 21:56:22,609+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Note that open browser sessions may have to be restarted to interact with this CA.
[PKI] Creating 'Keycloak' CA with RSA2048 keys...
[CMD] docker exec ejbca /opt/keyfactor/bin/ejbca.sh ca init 'Keycloak' 'CN=Keycloak Stub,O=JSI' soft 'foo123' RSA2048 RSA2048 3650 null SHA256WithRSA
2026-03-30 21:56:24,344+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Initializing CA
2026-03-30 21:56:24,344+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Generating rootCA keystore:
2026-03-30 21:56:24,344+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA Type:x509
2026-03-30 21:56:24,344+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA name: Keycloak
2026-03-30 21:56:24,344+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) SuperAdmin CN: null
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) DN: CN=Keycloak Stub,O=JSI
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA token type: soft
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA token password: hidden
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Keytype: RSA2048
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Keyspec: RSA2048
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Validity: 3650d
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Policy ID: null
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Signature alg: SHA256WithRSA
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Certificate profile: ROOTCA
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA token properties: {}
2026-03-30 21:56:24,345+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Signed by: Self signed
2026-03-30 21:56:24,353+0000 INFO  [org.ejbca.ui.cli.ca.BaseCaAdminCommand] (main) Initalizing authorization module with caid=-554238639 and superadmin CN 'null'.
2026-03-30 21:56:25,218+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Creating CA...
2026-03-30 21:56:25,295+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CAId for created CA: -554238639
2026-03-30 21:56:25,295+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Created and published initial CRL.
2026-03-30 21:56:25,295+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) CA initialized
2026-03-30 21:56:25,295+0000 INFO  [org.ejbca.ui.cli.ca.CaInitCommand] (main) Note that open browser sessions may have to be restarted to interact with this CA.
[PKI] All PKI operations completed!

=== STAGE 4: Keycloak Config ===
[CMD] docker exec keycloak /opt/keycloak/bin/kcadm.sh config credentials --server http://localhost:8080 --realm master --user admin --password admin
Logging into http://localhost:8080 as user admin of realm master
[CMD] docker exec keycloak /opt/keycloak/bin/kcadm.sh create realms -s realm=ejbca-realm -s enabled=true
Created new realm with id 'ejbca-realm'
[CMD] docker exec keycloak /opt/keycloak/bin/kcadm.sh create clients -r ejbca-realm -s clientId=ejbca-admin -s protocol=openid-connect -s publicClient=false -s redirectUris=["https://localhost/*"] -s enabled=true
Cannot parse the JSON [unknown_error]
Command failed (ignored)
[CMD] docker exec keycloak /opt/keycloak/bin/kcadm.sh create users -r ejbca-realm -s username=pkiadmin -s enabled=true
Created new user with id 'de9a767f-da72-4074-9415-3e0d59f66579'
[CMD] docker exec keycloak /opt/keycloak/bin/kcadm.sh set-password -r ejbca-realm --username pkiadmin --new-password password123

=== STAGE 5: SSO Integration ===
[CMD] docker exec ejbca /opt/keyfactor/bin/ejbca.sh config oauth addoauthprovider --label PQCToken --type GENERIC --url http://localhost:8080/realms/ejbca-realm --realm ejbca-realm --client ejbca-admin --audience ejbca-admin --skewlimit 1500
2026-03-30 21:56:30,945+0000 INFO  [org.ejbca.ui.cli.config.oauth.AddOAuthProviderCommand] (main) Trusted OAuth Provider with label PQCToken added successfully!
[INFO] SSO Integration complete!

========================================================
 DEPLOYMENT SUCCESSFUL
========================================================
(Cmd+Click links to open)
 1. EJBCA Admin:  https://localhost/ejbca/adminweb
 2. EJBCA RA:     https://localhost/ejbca/ra
 3. Keycloak:     http://localhost:8080
--------------------------------------------------------
 4. Login User:   pkiadmin
 5. Login Pass:   password123
 6. KC Admin:     admin / admin
========================================================


## 🛡️ Security & Cryptographic Posture
This project tracks Software & Cryptographic Bill of Materials (SBOM & CBOM) and Post-Quantum Cryptography (PQC) readiness. See the latest [Cryptographic Audit & PQC Migration Report](docs/security/CRYPTOGRAPHIC_AUDIT.md).
