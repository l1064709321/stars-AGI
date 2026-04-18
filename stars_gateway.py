#!/usr/bin/env python3
"""
STARS-Gateway v0.1.2 - 完整版
周天星斗守护系统
适配 AidLux / Linux / macOS / Windows
"""

import socket
import threading
import time
import re
import json
import logging
import platform
import hashlib
import subprocess
import os
import sys
import signal
import random
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Set
from concurrent.futures import ThreadPoolExecutor
from enum import Enum
import ipaddress
from pathlib import Path

# ==================== 依赖检查 ====================

def ensure_dependencies():
    required = {'psutil': 'psutil', 'requests': 'requests'}
    for module, package in required.items():
        try:
            __import__(module)
        except ImportError:
            print(f"[*] Installing {package}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

ensure_dependencies()
import psutil
import requests


# ==================== 星宿系统 ====================

class StarSystem:
    """周天星斗系统 - 三百六十五颗星"""

    EMPEROR_STAR = "紫微"

    BIG_DIPPER = ["天枢", "天璇", "天玑", "天权", "玉衡", "开阳", "摇光"]

    ZIWEI = [
        "北极", "太子", "帝", "庶子", "后宫",
        "四辅", "天乙", "太一",
        "左枢", "上宰", "少宰", "上弼", "少弼", "上卫", "少卫", "少丞",
        "右枢", "少尉", "上辅", "少辅", "上卫", "少卫", "上丞",
        "天枪", "天棓", "玄戈",
        "辅", "内厨", "天厨", "天牢", "太阳守",
        "势", "相", "三公", "天理", "文昌", "三师",
    ]

    TAIWEI = [
        "五帝座", "太子", "从官", "幸臣",
        "五诸侯", "九卿", "太微三公", "内屏", "谒者",
        "左执法", "右执法",
        "左上将", "左次将", "左次相", "左上相", "左垣末",
        "右上将", "右次将", "右次相", "右上相", "右垣末",
        "郎将", "郎位", "常陈", "虎贲",
        "少微", "长垣", "灵台", "明堂",
    ]

    TIANSHI = [
        "帝座", "候", "宦者", "斗", "斛", "列肆", "车肆", "市楼",
        "宗正", "宗人", "帛度", "屠肆", "宗", "天江", "天籥",
        "七公", "贯索", "女床",
    ]

    QINGLONG = [
        "角", "平道", "天田", "进贤", "周鼎", "天门", "平",
        "库楼", "柱", "衡", "南门",
        "亢", "大角", "折威", "摄提", "顿顽", "阳门",
        "氐", "亢池", "帝席", "梗河", "招摇", "天乳",
        "阵车", "骑官", "车骑", "天辐", "骑阵将军",
        "房", "钩钤", "键闭", "罚", "东咸", "西咸", "日", "从官",
        "心", "积卒",
        "尾", "神宫", "天江", "傅说", "鱼", "龟",
        "箕", "糠", "杵",
    ]

    XUANWU = [
        "斗", "建", "天弁", "鳖", "天鸡", "狗", "狗国", "天渊", "农丈人",
        "牛", "天田", "九坎", "河鼓", "织女", "左旗", "右旗",
        "天桴", "罗堰", "渐台", "辇道",
        "女", "离珠", "败瓜", "瓠瓜", "天津", "奚仲", "扶筐",
        "虚", "司命", "司禄", "司危", "司非", "哭", "泣",
        "天垒城", "败臼",
        "危", "坟墓", "盖屋", "虚梁", "天钱", "人", "杵", "臼",
        "室", "离宫", "雷电", "垒壁阵", "羽林军", "鈇钺",
        "北落师门", "八魁", "天纲", "土公吏", "螣蛇",
        "壁", "霹雳", "云雨", "天厩", "鈇锧", "土公",
    ]

    BAIHU = [
        "奎", "外屏", "天溷", "土司空", "军南门", "阁道", "附路", "王良", "策",
        "娄", "左更", "右更", "天仓", "天庾", "天大将军",
        "胃", "天廪", "天囷", "大陵", "天船", "积尸", "积水",
        "昴", "天阿", "月", "天阴", "刍藁", "天苑", "卷舌", "天谗", "砺石",
        "毕", "附耳", "天关", "天街", "天节", "诸王", "天高",
        "九州殊口", "五车", "柱", "咸池", "天潢", "参旗", "九斿", "天园",
        "觜", "司怪", "座旗",
        "参", "伐", "玉井", "军井", "屏", "厕", "屎",
    ]

    ZHUQUE = [
        "井", "钺", "水府", "天樽", "五诸侯", "北河", "积水", "积薪",
        "水位", "南河", "四渎", "阙丘", "军市", "野鸡", "孙", "子", "老人", "丈人",
        "鬼", "积尸", "爟", "天狗", "外厨", "天社", "天记",
        "柳", "酒旗",
        "星", "天相", "天稷", "轩辕", "内平",
        "张", "天庙",
        "翼", "东瓯",
        "轸", "左辖", "右辖", "长沙", "青丘", "军门", "土司空", "器府",
    ]

    # 补充到 364
    EXTRA = [
        "天关", "天枢", "天璇", "天玑", "天权", "玉衡", "开阳", "摇光",
        "天枪", "天棓", "玄戈", "天牢", "太阳守",
        "势", "相", "三公", "天理", "文昌", "三师",
        "五帝座", "太子", "从官", "幸臣",
        "五诸侯", "九卿", "内屏", "谒者",
        "左执法", "右执法", "郎将", "郎位", "常陈", "虎贲",
        "少微", "长垣", "灵台", "明堂",
        "帝座", "候", "宦者", "斗", "斛", "列肆", "车肆", "市楼",
        "宗正", "宗人", "帛度", "屠肆", "宗", "天江", "天籥",
        "七公", "贯索", "女床",
        "角", "平道", "天田", "进贤", "周鼎", "天门", "平",
        "库楼", "柱", "衡", "南门",
        "亢", "大角", "折威", "摄提", "顿顽", "阳门",
        "氐", "亢池", "帝席", "梗河", "招摇", "天乳",
        "阵车", "骑官", "车骑", "天辐", "骑阵将军",
        "房", "钩钤", "键闭", "罚", "东咸", "西咸", "日", "从官",
        "心", "积卒", "尾", "神宫", "傅说", "鱼", "龟",
        "箕", "糠", "杵",
    ]

    @classmethod
    def _get_all_stars(cls) -> list:
        all_stars = []
        all_stars.extend(cls.BIG_DIPPER)
        all_stars.extend(cls.ZIWEI)
        all_stars.extend(cls.TAIWEI)
        all_stars.extend(cls.TIANSHI)
        all_stars.extend(cls.QINGLONG)
        all_stars.extend(cls.XUANWU)
        all_stars.extend(cls.BAIHU)
        all_stars.extend(cls.ZHUQUE)
        # 去重
        seen = set()
        unique = []
        for s in all_stars:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        # 补齐到 364
        for s in cls.EXTRA:
            if s not in seen:
                seen.add(s)
                unique.append(s)
        # 如果还不够，用编号补齐
        idx = 1
        while len(unique) < 364:
            name = f"辅星{idx}"
            if name not in seen:
                seen.add(name)
                unique.append(name)
            idx += 1
        return unique[:364]

    @classmethod
    def get_star_count(cls) -> int:
        return len(cls._get_all_stars()) + 1

    @classmethod
    def get_random_star(cls) -> str:
        return random.choice(cls._get_all_stars())

    @classmethod
    def get_emperor_star(cls) -> str:
        return cls.EMPEROR_STAR

    @classmethod
    def get_startup_display(cls, star: str = None) -> str:
        if star is None:
            star = cls.get_random_star()
        if star == "紫微":
            return cls._style_emperor(star)
        styles = [cls._style_classic, cls._style_modern, cls._style_minimal, cls._style_stars]
        return random.choice(styles)(star)

    @classmethod
    def _style_emperor(cls, name: str) -> str:
        return f"""
    ╔══════════════════════════════════════════════════╗
    ║                                                  ║
    ║              ★ ★ ★ ★ ★ ★ ★ ★ ★               ║
    ║                                                  ║
    ║                    紫 微                         ║
    ║                                                  ║
    ║              ★ ★ ★ ★ ★ ★ ★ ★ ★               ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝"""

    @classmethod
    def _style_classic(cls, name: str) -> str:
        return f"""
    ╭──────────────────────────────────────────────╮
    │                                              │
    │              ★    {name:^10}    ★              │
    │                                              │
    ╰──────────────────────────────────────────────╯"""

    @classmethod
    def _style_modern(cls, name: str) -> str:
        return f"""
    ┌──────────────────────────────────────────────┐
    │                                              │
    │           ★  {name:^14}  ★           │
    │                                              │
    └──────────────────────────────────────────────┘"""

    @classmethod
    def _style_minimal(cls, name: str) -> str:
        return f"""
    {'─' * 50}

             ★  {name}  ★

    {'─' * 50}"""

    @classmethod
    def _style_stars(cls, name: str) -> str:
        stars_line = ""
        for _ in range(40):
            stars_line += random.choice([" ", " ", " ", "·", "✦", " ", " "])
        return f"""
    {'·' * 50}
    {stars_line}
    {'·' * 50}

               ★  {name}  ★

    {'·' * 50}"""


# ==================== 枚举 ====================

class ThreatLevel(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class AttackType(Enum):
    SQL_INJECTION = "SQL_INJECTION"
    XSS = "XSS"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    COMMAND_INJECTION = "COMMAND_INJECTION"
    SSRF = "SSRF"
    PROTOCOL_SMUGGLING = "PROTOCOL_SMUGGLING"
    SCANNER = "SCANNER"
    RATE_LIMIT = "RATE_LIMIT"
    BRUTE_FORCE = "BRUTE_FORCE"
    BOT = "BOT"
    CREDENTIAL_STUFFING = "CREDENTIAL_STUFFING"
    UNKNOWN = "UNKNOWN"

class BlockAction(Enum):
    ALLOW = "allow"
    CHALLENGE = "challenge"
    BLOCK = "block"
    LOG_ONLY = "log_only"


# ==================== 数据类 ====================

@dataclass
class CloudflareConfig:
    api_token: str = ""
    zone_id: str = ""
    email: str = ""
    api_base: str = "https://api.cloudflare.com/client/v4"

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

    @property
    def is_configured(self) -> bool:
        return bool(self.api_token and self.zone_id)


@dataclass
class NginxConfig:
    config_dir: str = "/etc/nginx"
    modsec_dir: str = "/etc/nginx/modsecurity"
    crs_dir: str = "/etc/nginx/modsecurity/crs"
    upstream_host: str = "127.0.0.1"
    upstream_port: int = 3000
    server_name: str = "example.com"
    listen_port: int = 443
    ssl_cert: str = "/etc/ssl/certs/server.crt"
    ssl_key: str = "/etc/ssl/private/server.key"


@dataclass
class IPProfile:
    ip: str
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    request_count: int = 0
    violations: int = 0
    attack_types: List[AttackType] = field(default_factory=list)
    reputation: int = 100
    blocked_until: Optional[datetime] = None
    source: str = "local"

    @property
    def threat_level(self) -> ThreatLevel:
        if self.reputation >= 80:
            return ThreatLevel.LOW
        elif self.reputation >= 50:
            return ThreatLevel.MEDIUM
        elif self.reputation >= 20:
            return ThreatLevel.HIGH
        return ThreatLevel.CRITICAL

    @property
    def is_blocked(self) -> bool:
        if self.blocked_until is None:
            return False
        return datetime.now() < self.blocked_until


@dataclass
class AttackEvent:
    timestamp: datetime
    ip: str
    attack_type: AttackType
    detail: str
    source: str
    action_taken: str
    blocked: bool


# ==================== Cloudflare 管理器 ====================

class CloudflareManager:
    CF_IP_RANGES = [
        "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22",
        "103.31.4.0/22", "141.101.64.0/18", "108.162.192.0/18",
        "190.93.240.0/20", "188.114.96.0/20", "197.234.240.0/22",
        "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13",
        "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22",
    ]
    _cf_networks: Optional[List] = None

    def __init__(self, config: CloudflareConfig):
        self.config = config
        self.logger = logging.getLogger('CF')
        self._semaphore = threading.Semaphore(5)
        self._last_request_time = 0
        self._min_interval = 0.2
        if CloudflareManager._cf_networks is None:
            CloudflareManager._cf_networks = [
                ipaddress.ip_network(c, strict=False) for c in self.CF_IP_RANGES
            ]

    def _api_request(self, method: str, endpoint: str,
                     data: dict = None, retries: int = 2) -> dict:
        if not self.config.is_configured:
            return {"success": False, "errors": ["CF not configured"]}
        url = f"{self.config.api_base}{endpoint}"
        for attempt in range(retries + 1):
            try:
                with self._semaphore:
                    now = time.time()
                    if now - self._last_request_time < self._min_interval:
                        time.sleep(self._min_interval - (now - self._last_request_time))
                    self._last_request_time = time.time()
                    if method == "GET":
                        resp = requests.get(url, headers=self.config.headers, timeout=10)
                    elif method == "POST":
                        resp = requests.post(url, headers=self.config.headers, json=data, timeout=10)
                    elif method == "DELETE":
                        resp = requests.delete(url, headers=self.config.headers, timeout=10)
                    else:
                        return {"success": False, "errors": [f"Unknown: {method}"]}
                if resp.status_code == 429:
                    time.sleep(int(resp.headers.get('Retry-After', 5)))
                    continue
                return resp.json()
            except requests.exceptions.Timeout:
                if attempt < retries:
                    time.sleep(2 ** attempt)
            except requests.RequestException as e:
                self.logger.error(f"CF API error: {e}")
                if attempt < retries:
                    time.sleep(2 ** attempt)
        return {"success": False, "errors": ["Max retries exceeded"]}

    def block_ip(self, ip: str, notes: str = "STARS block") -> bool:
        data = {"mode": "block", "configuration": {"target": "ip", "value": ip}, "notes": notes}
        result = self._api_request("POST", f"/zones/{self.config.zone_id}/firewall/access_rules/rules", data)
        if result.get("success"):
            self.logger.info(f"[CF-BLOCK] {ip}")
            return True
        return False

    def challenge_ip(self, ip: str, notes: str = "STARS challenge") -> bool:
        data = {"mode": "challenge", "configuration": {"target": "ip", "value": ip}, "notes": notes}
        result = self._api_request("POST", f"/zones/{self.config.zone_id}/firewall/access_rules/rules", data)
        return result.get("success", False)

    def is_cf_ip(self, ip: str) -> bool:
        try:
            addr = ipaddress.ip_address(ip)
            return any(addr in net for net in self._cf_networks)
        except ValueError:
            return False


# ==================== Nginx 配置生成器 ====================

class NginxConfigGenerator:
    def __init__(self, config: NginxConfig, cf_manager: CloudflareManager):
        self.config = config
        self.cf = cf_manager
        self.logger = logging.getLogger('Nginx-Gen')

    def generate_nginx_conf(self) -> str:
        cf_trust_ips = "\n".join(f"    set_real_ip_from {c};" for c in self.cf.CF_IP_RANGES)
        return f'''# STARS-Gateway v3.2 - Nginx Configuration
# Auto-generated: {datetime.now().isoformat()}

load_module modules/ngx_http_modsecurity_module.so;

worker_processes auto;
worker_rlimit_nofile 65535;

events {{
    worker_connections 16384;
    use epoll;
    multi_accept on;
}}

http {{
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    client_max_body_size 10m;
    client_body_buffer_size 128k;

    modsecurity on;
    modsecurity_rules_file {self.config.modsec_dir}/main.conf;

{cf_trust_ips}
    real_ip_header CF-Connecting-IP;
    real_ip_recursive on;

    limit_req_zone $binary_remote_addr zone=general:20m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=api:20m rate=30r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=10r/m;
    limit_conn_zone $binary_remote_addr zone=conn_per_ip:10m;

    log_format stars escape=json \'\'\'{{'
        "time": "$time_iso8601",
        "remote_addr": "$remote_addr",
        "request": "$request",
        "status": $status,
        "body_bytes_sent": $body_bytes_sent,
        "request_time": $request_time,
        "http_user_agent": "$http_user_agent",
        "http_cf_ray": "$http_cf_ray",
        "http_cf_connecting_ip": "$http_cf_connecting_ip"
    }}\'\'\';

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;
    ssl_session_tickets off;

    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    upstream backend {{
        server {self.config.upstream_host}:{self.config.upstream_port};
        keepalive 32;
    }}

    server {{
        listen {self.config.listen_port} ssl http2;
        listen [::]:{self.config.listen_port} ssl http2;
        server_name {self.config.server_name};
        ssl_certificate {self.config.ssl_cert};
        ssl_certificate_key {self.config.ssl_key};
        access_log /var/log/nginx/stars_access.log stars;
        error_log /var/log/nginx/stars_error.log warn;
        limit_conn conn_per_ip 50;

        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        location ~ /\\. {{ deny all; return 404; }}
        location ~* \\.(git|env|bak|sql|log|ini|conf)$ {{ deny all; return 404; }}
        location ~* ^/(wp-admin|wp-login|phpmyadmin|adminer) {{
            allow 10.0.0.0/8; allow 172.16.0.0/12; allow 192.168.0.0/16; deny all; return 403;
        }}

        location /api/ {{
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Request-ID $request_id;
        }}

        location ~* ^/(login|signin|auth|register) {{
            limit_req zone=login burst=3 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }}

        location /upload {{
            limit_req zone=upload burst=5 nodelay;
            client_max_body_size 10m;
            proxy_pass http://backend;
            proxy_set_header Host $host;
        }}

        location / {{
            limit_req zone=general burst=50 nodelay;
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Request-ID $request_id;
            proxy_http_version 1.1;
            proxy_set_header Connection "";
        }}

        location = /nginx-health {{
            access_log off;
            return 200 "healthy\\n";
        }}

        location = /stars-status {{
            allow 127.0.0.1; deny all;
            proxy_pass http://127.0.0.1:9090/status;
        }}
    }}

    server {{
        listen 80;
        server_name {self.config.server_name};
        location /.well-known/acme-challenge/ {{ root /var/www/certbot; }}
        location / {{ return 301 https://$host$request_uri; }}
    }}
}}'''

    def generate_modsec_main_conf(self) -> str:
        return f'''# ModSecurity Main Configuration
# STARS-Gateway v3.2

SecRuleEngine On
SecRequestBodyAccess On
SecResponseBodyAccess Off
SecRequestBodyLimit 13107200
SecRequestBodyNoFilesLimit 131072
SecRequestBodyLimitAction Reject

SecAuditEngine RelevantOnly
SecAuditLogRelevantStatus "^(?:5|4(?!04))"
SecAuditLog /var/log/nginx/modsec_audit.log
SecAuditLogType Serial
SecAuditLogParts ABIJDEFHZ
SecDebugLogLevel 0

SecDefaultAction "phase:1,deny,log,status:403"
SecDefaultAction "phase:2,deny,log,status:403"

SecArgumentSeparator "&"
SecCookieFormat 0
SecStatusEngine On
SecTmpDir /tmp/modsecurity_tmp
SecDataDir /tmp/modsecurity_data

Include {self.config.crs_dir}/crs-setup.conf
Include {self.config.crs_dir}/rules/*.conf
Include {self.config.modsec_dir}/custom-rules.conf'''

    def generate_custom_rules(self, blocked_ips: Set[str] = None) -> str:
        blocked_ips = blocked_ips or set()
        ip_section = ""
        if blocked_ips:
            ip_list = ", ".join(sorted(blocked_ips))
            # 修正语法错误：外层使用双引号，内部单引号无需转义
            ip_section = f"\nSecRule REMOTE_ADDR \"@ipMatch {ip_list}\" \\\n    \"id:1000001,phase:1,deny,status:403,log,msg:'STARS: Blocked IP'\"\n"
        return f'''# STARS-Gateway Custom Rules
# Generated: {datetime.now().isoformat()}
# Blocked: {len(blocked_ips)}

{ip_section}
SecRule ARGS|ARGS_NAMES|REQUEST_COOKIES "@rx (?i)(union\\s+(?:all\\s+)?select|\\bor\\b\\s+\\d+\\s*=\\s*\\d+)" \\
    "id:2000001,phase:2,deny,status:403,log,msg:\\'STARS: SQL Injection\\'"
SecRule ARGS "@rx (?i)(sleep\\s*\\(|benchmark\\s*\\(|waitfor\\s+delay)" \\
    "id:2000002,phase:2,deny,status:403,log,msg:\\'STARS: SQL Time-based\\'"
SecRule ARGS|REQUEST_BODY "@rx (?i)(<script[^>]*>|javascript\\s*:)" \\
    "id:2000010,phase:2,deny,status:403,log,msg:\\'STARS: XSS\\'"
SecRule REQUEST_URI|ARGS "@rx (\\.\\.[\\\\/]|%2e%2e)" \\
    "id:2000020,phase:1,deny,status:403,log,msg:\\'STARS: Path Traversal\\'"
SecRule ARGS "@rx [;|`]\\\\s*(?:cat|ls|id|whoami|wget|curl|bash|sh)" \\
    "id:2000030,phase:2,deny,status:403,log,msg:\\'STARS: Command Injection\\'"
SecRule ARGS "@rx (?i)(?:127\\\\.0\\\\.0\\\\.1|localhost|169\\\\.254\\\\.169\\\\.254)" \\
    "id:2000040,phase:2,deny,status:403,log,msg:\\'STARS: SSRF\\'"
SecRule REQUEST_HEADERS:User-Agent "@rx (?i)(sqlmap|nikto|nmap|masscan|gobuster|burpsuite)" \\
    "id:2000050,phase:1,deny,status:403,log,msg:\\'STARS: Scanner\\'"
SecRule REMOTE_ADDR "@ipMatchFromFile {self.config.modsec_dir}/threat_intel_ips.txt" \\
    "id:2000999,phase:1,deny,status:403,log,msg:\\'STARS: Known Malicious IP\\'"'''

    def write_configs(self, blocked_ips: Set[str] = None):
        blocked_ips = blocked_ips or set()
        configs = {
            f"{self.config.config_dir}/nginx.conf": self.generate_nginx_conf(),
            f"{self.config.modsec_dir}/main.conf": self.generate_modsec_main_conf(),
            f"{self.config.modsec_dir}/custom-rules.conf": self.generate_custom_rules(blocked_ips),
        }
        for path, content in configs.items():
            os.makedirs(os.path.dirname(path), exist_ok=True)
            if os.path.exists(path):
                try:
                    os.replace(path, f"{path}.bak")
                except OSError:
                    pass
            with open(path, 'w') as f:
                f.write(content)
            self.logger.info(f"Written: {path}")

    def write_threat_intel_ips(self, ips: Set[str]):
        path = f"{self.config.modsec_dir}/threat_intel_ips.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(f"# STARS Threat Intel IPs\n# Updated: {datetime.now().isoformat()}\n# Total: {len(ips)}\n")
            for ip in sorted(ips):
                f.write(f"{ip}\n")
        self.logger.info(f"Wrote {len(ips)} threat intel IPs")

    def reload_nginx(self) -> bool:
        try:
            r = subprocess.run(["nginx", "-t"], capture_output=True, text=True, timeout=10)
            if r.returncode != 0:
                self.logger.error(f"Nginx test failed:\n{r.stderr}")
                return False
            r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                self.logger.info("Nginx reloaded")
                return True
            self.logger.error(f"Nginx reload failed: {r.stderr}")
            return False
        except FileNotFoundError:
            self.logger.warning("Nginx not found, skipping reload")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("Nginx timeout")
            return False


# ==================== ModSecurity 日志解析器 ====================

class ModSecurityLogParser:
    IP_PATTERN = re.compile(r'$$client ([\d.:]+)$$')
    MSG_PATTERN = re.compile(r'msg "([^"]*)"')
    ATTACK_TYPE_MAP = {
        'SQL': AttackType.SQL_INJECTION,
        'XSS': AttackType.XSS,
        'traversal': AttackType.PATH_TRAVERSAL,
        'command': AttackType.COMMAND_INJECTION,
        'SSRF': AttackType.SSRF,
        'Scanner': AttackType.SCANNER,
    }

    def __init__(self):
        self.logger = logging.getLogger('ModSec-Parser')

    def parse_log_line(self, line: str) -> Optional[dict]:
        if "ModSecurity" not in line and "STARS:" not in line:
            return None
        result = {'timestamp': datetime.now().isoformat(), 'raw': line[:500]}
        ip_match = self.IP_PATTERN.search(line)
        if ip_match:
            result['ip'] = ip_match.group(1)
        msg_match = self.MSG_PATTERN.search(line)
        if msg_match:
            result['message'] = msg_match.group(1)
        result['attack_type'] = AttackType.UNKNOWN
        for keyword, atype in self.ATTACK_TYPE_MAP.items():
            if keyword.lower() in line.lower():
                result['attack_type'] = atype
                break
        return result

    def tail_log(self, log_path: str, callback, stop_event: threading.Event = None):
        stop_event = stop_event or threading.Event()
        while not stop_event.is_set():
            try:
                with open(log_path, 'r') as f:
                    f.seek(0, 2)
                    while not stop_event.is_set():
                        line = f.readline()
                        if line:
                            parsed = self.parse_log_line(line)
                            if parsed:
                                try:
                                    callback(parsed)
                                except Exception as e:
                                    self.logger.error(f"Callback error: {e}")
                        else:
                            time.sleep(0.1)
            except FileNotFoundError:
                self.logger.debug(f"Waiting for: {log_path}")
                time.sleep(5)
            except Exception as e:
                self.logger.error(f"Log tail error: {e}")
                time.sleep(5)


# ==================== 威胁情报聚合器 ====================

class ThreatIntelligence:
    THREAT_FEEDS = {
        'abuse_ch': "https://feodotracker.abuse.ch/downloads/ipblocklist.txt",
        'emerging_threats': "https://rules.emergingthreats.net/blockrules/compromised-ips.txt",
    }

    def __init__(self):
        self.logger = logging.getLogger('ThreatIntel')
        self.known_bad_ips: Set[str] = set()
        self.last_update: Optional[datetime] = None
        self._update_lock = threading.Lock()

    def _load_feed(self, name: str, url: str) -> Set[str]:
        ips = set()
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200:
                for line in resp.text.splitlines():
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    try:
                        ipaddress.ip_address(line)
                        ips.add(line)
                    except ValueError:
                        try:
                            ipaddress.ip_network(line, strict=False)
                            ips.add(line)
                        except ValueError:
                            pass
                self.logger.info(f"Loaded {len(ips)} from {name}")
            else:
                self.logger.warning(f"{name} status {resp.status_code}")
        except requests.RequestException as e:
            self.logger.error(f"Failed to load {name}: {e}")
        return ips

    def update_all(self):
        with self._update_lock:
            self.logger.info("Updating threat intelligence...")
            new_ips = set()
            for name, url in self.THREAT_FEEDS.items():
                new_ips.update(self._load_feed(name, url))
            self.known_bad_ips = new_ips
            self.last_update = datetime.now()
            self.logger.info(f"Threat intel updated: {len(self.known_bad_ips)} IPs")

    def is_known_bad(self, ip: str) -> bool:
        return ip in self.known_bad_ips


# ==================== 状态 API 服务器 ====================

class StatusAPIServer:
    def __init__(self, gateway: 'STARGateway', port: int = 9090):
        self.gateway = gateway
        self.port = port
        self.logger = logging.getLogger('StatusAPI')
        self._server_socket: Optional[socket.socket] = None
        self._running = False

    def start(self):
        self._running = True
        threading.Thread(target=self._serve, daemon=True).start()

    def stop(self):
        self._running = False
        if self._server_socket:
            self._server_socket.close()

    def _serve(self):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.settimeout(1.0)
        try:
            self._server_socket.bind(('127.0.0.1', self.port))
            self._server_socket.listen(5)
            self.logger.info(f"Status API: http://127.0.0.1:{self.port}")
            while self._running:
                try:
                    client, _ = self._server_socket.accept()
                    self._handle_request(client)
                except socket.timeout:
                    continue
                except Exception as e:
                    if self._running:
                        self.logger.error(f"Status API error: {e}")
        finally:
            if self._server_socket:
                self._server_socket.close()

    def _handle_request(self, client: socket.socket):
        try:
            client.settimeout(5.0)
            request = client.recv(4096).decode('utf-8', errors='ignore')
            if '/status' in req