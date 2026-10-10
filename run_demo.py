import subprocess
import time
import os
import sys
import socket

# ==============================================================================
#  COLORS & VISUALS
# ==============================================================================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def log_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {title} ==={Colors.ENDC}")

def log_info(msg):
    print(f"{Colors.GREEN}[INFO] {msg}{Colors.ENDC}")

def log_cmd(msg):
    print(f"{Colors.BLUE}[CMD] {msg}{Colors.ENDC}")

def log_err(msg):
    print(f"{Colors.FAIL}[ERROR] {msg}{Colors.ENDC}")

# ==============================================================================
#  DYNAMIC PORT RESOLUTION
# ==============================================================================
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port, exclude_ports=[]):
    port = start_port
    while port < 65535:
        if port not in exclude_ports and not is_port_in_use(port):
            return port
        port += 1
    raise Exception("No free ports found!")

# ==============================================================================
#  CONFIGURATION
# ==============================================================================
CONFIG = {
    "EJBCA_ADMIN_PASS": "ejbca_admin_pass",
    "EJBCADB_USER": "ejbca",
    "EJBCADB_PASS": "ejbca",
    "MARIADB_ROOT_PASS": "foo123",
    "KC_ADMIN_USER": "admin",
    "KC_ADMIN_PASS": "admin",
    "KC_DB_USER": "keycloak",
    "KC_DB_PASS": "keycloak",
    "KC_DB_URL": "jdbc:postgresql://postgres:5432/keycloak",
    "KC_REALM": "ejbca-realm",
    "KC_CLIENT": "ejbca-admin",
    "KC_USER": "pkiadmin",
    "KC_USER_PASS": "password123",
    "CA_NAME": "PQCRootCA",
    "CA_DN": "CN=PQC Root CA,O=JSIGroup,C=local",
    "TOKEN_NAME": "PQCToken",
    "TOKEN_PWD": "foo123",
    "EJBCA_BIN": "/opt/keyfactor/bin/ejbca.sh"
}

def load_env_file():
    env_path = ".env"
    if not os.path.exists(env_path):
        return
    log_info(f"Loading configuration from {env_path}...")
    try:
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    k, v = k.strip(), v.strip()
                    if k == "EJBCA_ADMIN_PASSWORD": CONFIG["EJBCA_ADMIN_PASS"] = v
                    elif k == "EJBCADB_PASSWORD": CONFIG["EJBCADB_PASS"] = v
                    elif k == "MARIADB_ROOT_PASSWORD": CONFIG["MARIADB_ROOT_PASS"] = v
                    elif k == "KEYCLOAK_DB_PASSWORD": CONFIG["KC_DB_PASS"] = v
    except Exception as e:
        log_err(f"Failed to parse .env: {e}")
        sys.exit(1)

# ==============================================================================
#  HELPER FUNCTIONS
# ==============================================================================
def run_cmd(command, ignore_errors=False):
    log_cmd(command)
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        if not ignore_errors:
            log_err(f"Command failed with code {e.returncode}")
            if "docker-compose up" in command:
                print(f"\n{Colors.WARNING}--- CONTAINER LOGS (DEBUG) ---{Colors.ENDC}")
                subprocess.run("docker logs postgres", shell=True)
                subprocess.run("docker logs mariadb", shell=True)
                print(f"{Colors.WARNING}-----------------------------{Colors.ENDC}\n")
            sys.exit(1)
        else:
            print(f"{Colors.WARNING}Command failed (ignored){Colors.ENDC}")

def run_docker_exec(container, command, ignore_errors=False):
    run_cmd(f"docker exec {container} {command}", ignore_errors)

def run_script_in_container(container, script_content):
    clean_content = script_content.strip()
    subprocess.run(
        f"docker exec -i {container} sh -c 'cat > /tmp/setup.sh'",
        input=clean_content.encode(),
        shell=True,
        check=True
    )
    run_cmd(f"docker exec {container} chmod +x /tmp/setup.sh")
    run_cmd(f"docker exec {container} /tmp/setup.sh")
    run_cmd(f"docker exec {container} rm /tmp/setup.sh")

# LIVE HEALTH CHECK
def wait_for_live_status(container, description, timeout=300):
    msg_visible = f"\rWaiting for {description} (Live Check)..."
    msg_hidden  = f"\r{' ' * len(msg_visible)}" 
    start_time = time.time()
    
    health_cmd = f"docker exec {container} curl -k -f -s -o /dev/null https://localhost:8443/ejbca/publicweb/healthcheck/ejbca"
    
    while True:
        current_time = time.time()
        if current_time - start_time > timeout:
            sys.stdout.write(msg_hidden)
            print(f"\r{Colors.FAIL}[ERROR] Timeout waiting for {description}{Colors.ENDC}\n")
            sys.exit(1)

        try:
            subprocess.run(health_cmd, shell=True, check=True)
            sys.stdout.write(msg_hidden)
            sys.stdout.write(f"\r{Colors.GREEN}[INFO] {description} is ONLINE (Confirmed Live){Colors.ENDC}                         \n")
            sys.stdout.flush()
            return
        except subprocess.CalledProcessError:
            pass

        cycle = current_time % 1.0
        if cycle < 0.5: sys.stdout.write(msg_visible)
        else: sys.stdout.write(msg_hidden)
        sys.stdout.flush()
        time.sleep(0.5)

# LOG CHECK (Initial Boot)
def wait_for_log_initial(container, search_strings, description, timeout=300):
    if isinstance(search_strings, str): search_strings = [search_strings]
    msg_visible = f"\rWaiting for {description}..."
    msg_hidden  = f"\r{' ' * len(msg_visible)}" 
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            res = subprocess.run(f"docker logs {container}", shell=True, capture_output=True, text=True)
            for s in search_strings:
                if s in (res.stdout + res.stderr):
                    sys.stdout.write(msg_hidden)
                    sys.stdout.write(f"\r{Colors.GREEN}[INFO] {description} is ONLINE.{Colors.ENDC}                         \n")
                    sys.stdout.flush()
                    return
        except: pass
        
        cycle = time.time() % 1.0
        if cycle < 0.5: sys.stdout.write(msg_visible)
        else: sys.stdout.write(msg_hidden)
        sys.stdout.flush()
        time.sleep(0.5)
    
    print(f"\n{Colors.FAIL}[ERROR] Timeout waiting for {description}{Colors.ENDC}")
    sys.exit(1)

# ==============================================================================
#  MAIN EXECUTION
# ==============================================================================
def main():
    clear_screen()
    try:
        log_section("STAGE 0: Init & Port Scanning")
        load_env_file()
        
        # 1. FORCED PORTS
        ejbca_https = 443
        
        # 2. Dynamic Ports
        kc_port = find_available_port(8080)
        try:
            if not is_port_in_use(80):
                ejbca_http = 80
            else:
                ejbca_http = find_available_port(8081, exclude_ports=[kc_port])
        except:
             ejbca_http = find_available_port(8081, exclude_ports=[kc_port])

        log_info(f"EJBCA HTTPS: localhost:{ejbca_https}")
        log_info(f"EJBCA HTTP:  localhost:{ejbca_http}")
        log_info(f"Keycloak:    localhost:{kc_port}")

        CONFIG['EJBCA_BASE_URL'] = f"https://localhost"
        CONFIG['EJBCA_ADMIN_URL'] = f"https://localhost/ejbca/adminweb"
        CONFIG['EJBCA_RA_URL'] = f"https://localhost/ejbca/ra"
        CONFIG['KC_PUBLIC_URL'] = f"http://localhost:{kc_port}"
        CONFIG['KC_ISSUER_URL'] = f"http://localhost:{kc_port}/realms/{CONFIG['KC_REALM']}"

        if os.path.exists("docker-compose.yml"):
            print("Cleaning up old containers...")
            run_cmd("docker-compose down -v --remove-orphans", ignore_errors=True)
        
        print("Generating docker-compose.yml...")
        
        compose_content = f"""
services:
  # --- EJBCA ---
  ejbca:
    image: keyfactor/ejbca-ce:latest
    container_name: ejbca
    hostname: localhost
    restart: unless-stopped
    ports:
      - "{ejbca_http}:8080"
      - "{ejbca_https}:8443"
    environment:
      - DATABASE_JDBC_URL=jdbc:mariadb://mariadb:3306/ejbca
      - DATABASE_USER={CONFIG['EJBCADB_USER']}
      - DATABASE_PASSWORD={CONFIG['EJBCADB_PASS']}
      - SUPERADMIN_CN=superadmin
      - SUPERADMIN_PASSWORD={CONFIG['EJBCA_ADMIN_PASS']}
      - WEBCONF_HTTPSERVER_HOSTNAME=localhost
      - WEBCONF_HTTPSERVER_HTTPSPORT={ejbca_https}
      - WEBCONF_HTTPSERVER_PUBHTTPSPORT={ejbca_https}
      - WEBCONF_HTTPSERVER_PRIVHTTPSPORT={ejbca_https}
      - WEBCONF_HTTPSERVER_PUBHTTPPORT={ejbca_http}
    depends_on:
      - mariadb
    networks:
      - pki-network
    volumes:
      - ejbca_data:/var/lib/ejbca
    extra_hosts:
      - "localhost:host-gateway" 

  mariadb:
    image: mariadb:10.11
    container_name: mariadb
    restart: unless-stopped
    environment:
      - MYSQL_ROOT_PASSWORD={CONFIG['MARIADB_ROOT_PASS']}
      - MYSQL_DATABASE=ejbca
      - MYSQL_USER={CONFIG['EJBCADB_USER']}
      - MYSQL_PASSWORD={CONFIG['EJBCADB_PASS']}
    networks:
      - pki-network
    volumes:
      - mariadb_data:/var/lib/mysql

  # --- KEYCLOAK ---
  keycloak:
    image: quay.io/keycloak/keycloak:26.0
    container_name: keycloak
    restart: unless-stopped
    command: start-dev
    ports:
      - "{kc_port}:8080"
    environment:
      - KEYCLOAK_ADMIN={CONFIG['KC_ADMIN_USER']}
      - KEYCLOAK_ADMIN_PASSWORD={CONFIG['KC_ADMIN_PASS']}
      - KC_DB=postgres
      - KC_DB_URL={CONFIG['KC_DB_URL']}
      - KC_DB_USERNAME={CONFIG['KC_DB_USER']}
      - KC_DB_PASSWORD={CONFIG['KC_DB_PASS']}
      - KC_HOSTNAME_URL=http://localhost:{kc_port}
      - KC_HOSTNAME_STRICT=false
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - pki-network
    extra_hosts:
      - "localhost:host-gateway"

  postgres:
    image: postgres:15
    container_name: postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=keycloak
      - POSTGRES_USER={CONFIG['KC_DB_USER']}
      - POSTGRES_PASSWORD={CONFIG['KC_DB_PASS']}
    networks:
      - pki-network
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U {KC_DB_USER} -d keycloak"]
      interval: 5s
      timeout: 5s
      retries: 5
      start_period: 15s

networks:
  pki-network:
    driver: bridge

volumes:
  ejbca_data:
  mariadb_data:
  postgres_data:
"""
        with open("docker-compose.yml", "w") as f:
            f.write(compose_content)

        # ==========================================
        # STAGE 1: Keycloak & Postgres
        # ==========================================
        log_section("STAGE 1: Starting Keycloak & Postgres")
        run_cmd("docker-compose up -d keycloak")
        
        # 1. Postgres Check
        wait_for_log_initial("postgres", ["database system is ready to accept connections"], "PostgreSQL Database")
        # 2. Keycloak Check
        wait_for_log_initial("keycloak", ["Listening on: http://0.0.0.0:8080", "Running the server"], "Keycloak Service")
        
        time.sleep(2)

        # ==========================================
        # STAGE 2: EJBCA & MariaDB
        # ==========================================
        log_section("STAGE 2: Starting EJBCA & MariaDB")
        run_cmd("docker-compose up -d ejbca")
        
        # 3. MariaDB Check
        wait_for_log_initial("mariadb", ["ready for connections", "mysqld: ready for connections"], "MariaDB Database")
        # 4. EJBCA Check
        wait_for_log_initial("ejbca", ["Health check now reports application status", "Deployment of artifact EJBCA"], "EJBCA Service")
        
        # FIX: Add live health check and wait for EJBCA to fully initialize
        log_info("Waiting for EJBCA to fully initialize...")
        wait_for_live_status("ejbca", "EJBCA Health Check", timeout=60)

        log_section("STAGE 3: PKI Config")

        bin = CONFIG['EJBCA_BIN']
        run_docker_exec("ejbca", f"{bin} cryptotoken create --token {CONFIG['TOKEN_NAME']} --pin {CONFIG['TOKEN_PWD']} --type SoftCryptoToken --autoactivate TRUE", ignore_errors=True)
        run_docker_exec("ejbca", f"{bin} cryptotoken generatekey --token {CONFIG['TOKEN_NAME']} --alias signKey --keyspec ML-DSA-65", ignore_errors=True)
        run_docker_exec("ejbca", f"{bin} cryptotoken generatekey --token {CONFIG['TOKEN_NAME']} --alias defaultKey --keyspec RSA2048", ignore_errors=True)
        run_docker_exec("ejbca", f"{bin} cryptotoken generatekey --token {CONFIG['TOKEN_NAME']} --alias testKey --keyspec RSA2048", ignore_errors=True)
        run_docker_exec("ejbca", f"{bin} ca init \"{CONFIG['CA_NAME']}\" \"{CONFIG['CA_DN']}\" soft \"{CONFIG['TOKEN_PWD']}\" ML-DSA-65 ML-DSA-65 3650 null ML-DSA-65", ignore_errors=True)
        
        print(f"{Colors.BLUE}[CMD] Creating 'Keycloak' CA...{Colors.ENDC}")
        run_docker_exec("ejbca", f"{bin} ca init 'Keycloak' 'CN=Keycloak Stub,O=JSI' soft '{CONFIG['TOKEN_PWD']}' RSA2048 RSA2048 3650 null SHA256WithRSA", ignore_errors=True)

        log_section("STAGE 4: Keycloak Config")
        adm = "/opt/keycloak/bin/kcadm.sh"
        run_docker_exec("keycloak", f"{adm} config credentials --server http://localhost:8080 --realm master --user {CONFIG['KC_ADMIN_USER']} --password {CONFIG['KC_ADMIN_PASS']}")
        run_docker_exec("keycloak", f"{adm} create realms -s realm={CONFIG['KC_REALM']} -s enabled=true", ignore_errors=True)
        
        redirects = f'"{CONFIG["EJBCA_BASE_URL"]}/*"'
        run_docker_exec("keycloak", f"{adm} create clients -r {CONFIG['KC_REALM']} -s clientId={CONFIG['KC_CLIENT']} -s protocol=openid-connect -s publicClient=false -s redirectUris=[{redirects}] -s enabled=true", ignore_errors=True)
        run_docker_exec("keycloak", f"{adm} create users -r {CONFIG['KC_REALM']} -s username={CONFIG['KC_USER']} -s enabled=true", ignore_errors=True)
        run_docker_exec("keycloak", f"{adm} set-password -r {CONFIG['KC_REALM']} --username {CONFIG['KC_USER']} --new-password {CONFIG['KC_USER_PASS']}")

        log_section("STAGE 5: SSO Integration")
        
        # FIX: Removed --tokentype and changed --with to "Username"
        bash_script = f"""#!/bin/bash
EJBCA_BIN="{CONFIG['EJBCA_BIN']}"

echo ">> Registering Provider..."
$EJBCA_BIN config oauth addoauthprovider \\
  --label "Keycloak" \\
  --type "Keycloak" \\
  --url "{CONFIG['KC_ISSUER_URL']}" \\
  --realm "{CONFIG['KC_REALM']}" \\
  --client "{CONFIG['KC_CLIENT']}" \\
  --audience "{CONFIG['KC_CLIENT']}" \\
  --skewlimit 1500 || echo "Provider exists"

echo ">> Mapping Role (Match: Username)..."
MAX_RETRIES=20
COUNT=0

until $EJBCA_BIN roles addrolemember \\
  --role "Super Administrator Role" \\
  --caname "Keycloak" \\
  --with "Username" \\
  --value "{CONFIG['KC_USER']}"; do
  
    echo ">> Role mapping failed. Retrying ($((COUNT+1))/$MAX_RETRIES)..."
    sleep 3
    COUNT=$((COUNT+1))
    
    if [ $COUNT -ge $MAX_RETRIES ]; then
       echo "ERROR: Failed to map role after retries."
       exit 1
    fi
done

echo ">> Role mapping SUCCESSFUL."
"""
        run_script_in_container("ejbca", bash_script)

        print(f"\n{Colors.HEADER}========================================================")
        print(" DEPLOYMENT SUCCESSFUL")
        print("========================================================")
        print(f"{Colors.BOLD}(Cmd+Click links to open){Colors.ENDC}")
        print(f" 1. EJBCA Admin:  {Colors.UNDERLINE}{CONFIG['EJBCA_ADMIN_URL']}{Colors.ENDC}")
        print(f" 2. EJBCA RA:     {Colors.UNDERLINE}{CONFIG['EJBCA_RA_URL']}{Colors.ENDC}")
        print(f" 3. Keycloak:     {Colors.UNDERLINE}{CONFIG['KC_PUBLIC_URL']}{Colors.ENDC}")
        print("--------------------------------------------------------")
        print(f" 4. Login User:   {CONFIG['KC_USER']}")
        print(f" 5. Login Pass:   {CONFIG['KC_USER_PASS']}")
        print(f" 6. KC Admin:     {CONFIG['KC_ADMIN_USER']} / {CONFIG['KC_ADMIN_PASS']}")
        print(f"========================================================{Colors.ENDC}")

    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)

if __name__ == "__main__":
    main()
