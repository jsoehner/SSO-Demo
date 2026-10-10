## 🛡️ Cryptographic Bill of Materials (CBOM) & PQC Migration Assessment

**Format**: CycloneDX (v1.6) | **Total Components**: 2 | **Crypto Assets**: 2

### 📊 Post-Quantum Migration Scorecard

| Metric | Count | Migration Status |
|---|---|---|
| **Post-Quantum Ready (PQC)** | **1** | 🟢 Quantum-Resistant (NIST FIPS 203/204/205) |
| **Quantum-Vulnerable (Backlog)** | **1** | 🔴 At Risk of 'Harvest Now, Decrypt Later' |
| **Classical Symmetric / Hashing** | **0** | 🟡 Classical Security (Requires AES-256 / SHA-256+) |
| **Asymmetric PQC Migration Progress** | **50.0%** | (1 of 2 asymmetric primitives migrated) |

### ✅ Post-Quantum Cryptography Migrated Assets

| Component Name | Primitive | Key/Parameter Set | PQC Standard | Location(s) |
|---|---|---|---|---|
| `ML-DSA-65` | signature | N/A | NIST FIPS 204 (ML-DSA) | `run_demo_v2.py:317`<br>`run_demo_v2.py:318`<br>`run_demo_v2.py:326`<br>`run_demo_v2.py:327` |

### ⚠️ Quantum-Vulnerable Assets & Remediation Plan

| Component / Algorithm | Type / Primitive | Key Length / Curve | Recommended Target | Source Location(s) & Code Context |
|---|---|---|---|---|
| **`RSA-2048`**<br><sub>RSA-2048</sub> | algorithm / signature | 2048 | **ML-KEM-768 / Kyber (FIPS 203)** | `run_demo_v2.py:320`<br><sub><code>print(f"{Colors.CYAN}[PKI] Generating RSA2048 default key...{Colors.ENDC}")</code></sub><br><br>`run_demo_v2.py:321`<br><sub><code>run_docker_exec("ejbca", f"{bin} cryptotoken generatekey --token {CONFIG['TOKEN_NAME']} --alias defaultKey --keyspec RSA</code></sub><br><br>`run_demo_v2.py:323`<br><sub><code>print(f"{Colors.CYAN}[PKI] Generating RSA2048 test key...{Colors.ENDC}")</code></sub><br><br>`run_demo_v2.py:324`<br><sub><code>run_docker_exec("ejbca", f"{bin} cryptotoken generatekey --token {CONFIG['TOKEN_NAME']} --alias testKey --keyspec RSA204</code></sub><br><br>`run_demo_v2.py:329`<br><sub><code>print(f"{Colors.CYAN}[PKI] Creating 'Keycloak' CA with RSA2048 keys...{Colors.ENDC}")</code></sub><br><br>`run_demo_v2.py:330`<br><sub><code>run_docker_exec("ejbca", f"{bin} ca init 'Keycloak' 'CN=Keycloak Stub,O=JSI' soft '{CONFIG['TOKEN_PWD']}' RSA2048 RSA204</code></sub> |

### 🔒 Classical Symmetric & Digest Assets
