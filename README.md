---

# JavaScript XSS Scanner 🔍  

An **advanced automated scanner** for detecting **Cross-Site Scripting (XSS) vulnerabilities** in JavaScript applications. This tool **analyzes full source code**, leverages **AST-based detection**, and **bypasses security defenses** like WAFs and CSP restrictions.  

## 🚀 Features  

🔹 **Full Source Code Analysis** – Scans all JavaScript code from a given URL, including inline scripts, linked files, and dynamically loaded content.  
🔹 **AST-Based XSS Detection** – Uses **Abstract Syntax Trees (ASTs)** to identify dangerous sinks like `innerHTML`, `eval()`, and `document.write()`.  
🔹 **Framework Detection for Custom Payloads** – Adapts payloads based on detected frameworks (React, Vue, Angular, etc.).  
🔹 **WAF & Security Header Detection** – Identifies Web Application Firewalls (WAFs) and analyzes security headers for misconfigurations.  
🔹 **Risk Scoring System** – Assigns risk levels based on input handling, CSP policies, and WAF restrictions.  
🔹 **Comprehensive Report Generation** – Outputs detected vulnerabilities, suggested payloads, and potential WAF bypass strategies.  

---

## 📦 Installation  

### Prerequisites  
- **Python 3.x**  
- **pip** (Python package manager)  

### Install Dependencies  
Clone the repository and install required dependencies:  

```bash
git clone https://github.com/yourusername/js-xss-scanner.git  
cd js-xss-scanner  
pip install -r requirements.txt  
```

---

## ⚡ Usage  

Run the scanner with the following command:  

```bash
❯ noglob python3 src/main.py --website url_here
```

### Example:  
```bash
❯ noglob python3 src/main.py --website https://example.com
```

---

## 🛠️ How It Works  

### 1️⃣ Full Source Code Analysis  
- Fetches **all JavaScript** from the target URL.  
- Parses **inline scripts**, **linked scripts**, and **dynamically loaded scripts**.  

### 2️⃣ AST-Based XSS Detection (Powered by Esprima)  
- Uses **Abstract Syntax Trees (ASTs)** for precise detection.  
- Finds **dangerous sinks**, including:  
  - `innerHTML`  
  - `document.write()`  
  - `eval()`  
  - `setTimeout()`  
  - `setInterval()`  
  - `location.href` / `window.location`  

### 3️⃣ Framework-Specific Payloads  
- Detects if the site is using **React, Vue, Angular**, etc.  
- Generates **framework-specific XSS payloads**:  
  - **React** → `dangerouslySetInnerHTML`  
  - **Vue** → `v-html`  
  - **Angular** → `bypassSecurityTrustHtml`  

### 4️⃣ WAF & Security Headers Analysis  
- Detects **WAF providers** (Cloudflare, Akamai, ModSecurity).  
- Analyzes **Content-Security-Policy (CSP)**, **X-XSS-Protection**, and other headers.  
- Adjusts **payloads dynamically** to bypass security restrictions.  

### 5️⃣ Risk Scoring System  
- Assigns **risk levels** based on:  
  - How user input is used in JavaScript.  
  - CSP rules (checks if inline scripts are allowed).  
  - WAF behavior (determines if payloads are blocked).  

### 6️⃣ Report Generation  
- Outputs a **structured vulnerability report** containing:  
  - **Detected vulnerabilities** (type, location, risk score).  
  - **Suggested payloads** for further exploitation.  
  - **Potential WAF bypass strategies**.  

---

## 📄 Example Output  

```plaintext
[+] Scanning https://example.com
[✓] Found 3 inline scripts, 2 external scripts, 1 dynamically loaded script
[!] Potential XSS Sink Detected: innerHTML at line 56 (Medium Risk)
[!] Potential XSS Sink Detected: eval() at line 102 (High Risk)
[+] Framework detected: React
[+] Generating React-specific XSS payloads...
[!] Content-Security-Policy found (Unsafe inline scripts allowed)
[!] WAF Detected: Cloudflare
[+] Adjusting payloads to bypass WAF restrictions...
[✓] Report saved: reports/example_com_scan.txt
```

---

## 🛡️ Disclaimer  

This tool is intended **for security research and educational purposes only**.  
Do **not** use it on sites you **do not own** or **lack permission to test**.  

---

## 🤝 Contributing  

1. **Fork** the repository.  
2. **Create** a new branch (`feature-xyz`).  
3. **Commit** your changes.  
4. **Push** to your branch.  
5. **Submit** a Pull Request!  

---

## 📜 License  

MIT License – Free to use and modify.  

---

## 📬 Contact  

For issues, suggestions, or contributions, **open an issue** or reach out on GitHub!  
