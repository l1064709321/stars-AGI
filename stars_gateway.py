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
        return f'''# STARS-Gateway v0.1.2 - Nginx Configuration
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
# STARS-Gateway v0.1.2

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
            if '/status' in request:
                body = json.dumps(self.gateway.get_status(), indent=2, default=str)
                ct = "application/json"
            elif '/attacks' in request:
                body = json.dumps(self.gateway.get_recent_attacks(20), indent=2, default=str)
                ct = "application/json"
            elif '/report' in request:
                body = self.gateway.generate_report()
                ct = "text/plain"
            elif '/star' in request:
                body = json.dumps({
                    'current_star': self.gateway.current_star,
                    'star_history': self.gateway.star_history[-10:],
                }, indent=2, ensure_ascii=False, default=str)
                ct = "application/json; charset=utf-8"
            else:
                body = json.dumps({
                    'endpoints': ['/status', '/attacks', '/report', '/star'],
                    'version': self.gateway.version,
                }, indent=2)
                ct = "application/json"
            response = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: {ct}\r\n"
                f"Content-Length: {len(body.encode('utf-8'))}\r\n"
                f"Connection: close\r\n"
                f"\r\n{body}"
            )
            client.sendall(response.encode('utf-8'))
        except Exception:
            pass
        finally:
            client.close()


# ==================== 主网关类 ====================

class STARGateway:

    def __init__(self, config: dict = None):
        config = config or {}
        self.version = "0.1.2"
        self._start_time = datetime.now()
        self.is_emperor_mode = config.get('emperor_mode', False)

        self.cf_config = CloudflareConfig(
            api_token=config.get('cf_api_token', ''),
            zone_id=config.get('cf_zone_id', ''),
            email=config.get('cf_email', ''),
        )

        # 自动检测 AidLux 路径
        if os.path.exists('/aidlux'):
            base = '/aidlux/stars_gateway'
            nginx_conf = f'{base}/nginx'
            modsec_conf = f'{base}/modsecurity'
            crs_conf = f'{base}/modsecurity/crs'
        else:
            nginx_conf = config.get('nginx_config_dir', '/etc/nginx')
            modsec_conf = config.get('modsec_dir', '/etc/nginx/modsecurity')
            crs_conf = config.get('crs_dir', '/etc/nginx/modsecurity/crs')

        self.nginx_config = NginxConfig(
            server_name=config.get('server_name', 'example.com'),
            upstream_host=config.get('upstream_host', '127.0.0.1'),
            upstream_port=config.get('upstream_port', 3000),
            config_dir=nginx_conf,
            modsec_dir=modsec_conf,
            crs_dir=crs_conf,
        )

        self.cf_manager = CloudflareManager(self.cf_config)
        self.nginx_gen = NginxConfigGenerator(self.nginx_config, self.cf_manager)
        self.modsec_parser = ModSecurityLogParser()
        self.threat_intel = ThreatIntelligence()
        self.status_api = StatusAPIServer(self)

        self.current_star: dict = {}
        self.star_history: List[dict] = []
        self._ip_profiles: Dict[str, IPProfile] = {}
        self._attack_events: List[AttackEvent] = []
        self._blocked_ips: Set[str] = set()
        self._lock = threading.Lock()

        self._metrics = {
            'total_attacks': 0,
            'attacks_blocked': 0,
            'cf_blocks': 0,
            'attacks_by_type': defaultdict(int),
        }

        self._stop_events: List[threading.Event] = []
        self._running = False

        self._setup_logging()
        self.logger = logging.getLogger('STARS')

    def _setup_logging(self):
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(name)s] [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'stars_gateway.log'),
                logging.StreamHandler(),
            ]
        )

    # ==================== 星宿选择 ====================

    def _select_star(self) -> str:
        if self.is_emperor_mode:
            star = StarSystem.get_emperor_star()
            self.logger.info("紫微降临")
        else:
            star = StarSystem.get_random_star()

        self.current_star = {
            'name': star,
            'selected_at': datetime.now().isoformat(),
            'session_id': hashlib.sha256(
                f"{star}:{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12],
        }
        self.star_history.append(self.current_star)
        if len(self.star_history) > 100:
            self.star_history = self.star_history[-50:]
        return star

    def _display_startup_banner(self):
        star = self._select_star()
        star_display = StarSystem.get_startup_display(star)
        os.system('cls' if platform.system() == 'Windows' else 'clear')

        mode = "帝星专属" if star == "紫微" else "周天星斗"
        total_stars = StarSystem.get_star_count()

        print(star_display)
        print(f"""
    ┌──────────────────────────────────────────────┐
    │  STARS-Gateway v{self.version:<30}│
    │  模式: {mode:<39}│
    │  当值: {star:<39}│
    │  周天: {total_stars} 颗星{' ' * (32 - len(str(total_stars)))}│
    │  会话: {self.current_star['session_id']:<39}│
    │  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<39}│
    ├──────────────────────────────────────────────┤
    │  平台: {platform.system():<39}│
    │  Cloudflare: {'已配置' if self.cf_config.is_configured else '未配置':<34}│
    │  威胁情报: abuse.ch + Emerging Threats       │
    │  检测引擎: ModSecurity + OWASP CRS           │
    │  状态接口: http://127.0.0.1:9090             │
    └──────────────────────────────────────────────┘
        """)
        self.logger.info(f"当值星宿: {star} | 周天星斗: {total_stars} 颗")

    # ==================== IP 管理 ====================

    def get_or_create_profile(self, ip: str) -> IPProfile:
        with self._lock:
            if ip not in self._ip_profiles:
                self._ip_profiles[ip] = IPProfile(ip=ip)
            profile = self._ip_profiles[ip]
            profile.last_seen = datetime.now()
            profile.request_count += 1
            return profile

    def process_attack(self, ip: str, attack_type: AttackType,
                       detail: str, source: str = "local") -> BlockAction:
        profile = self.get_or_create_profile(ip)
        with self._lock:
            profile.violations += 1
            profile.attack_types.append(attack_type)
            profile.reputation = max(0, profile.reputation - 20)
            self._metrics['total_attacks'] += 1
            self._metrics['attacks_by_type'][attack_type.value] += 1

        action = self._determine_action(profile, attack_type)

        event = AttackEvent(
            timestamp=datetime.now(), ip=ip, attack_type=attack_type,
            detail=detail[:200], source=source,
            action_taken=action.value, blocked=(action == BlockAction.BLOCK),
        )

        if action == BlockAction.BLOCK:
            self._block_ip(ip, profile, source)
            with self._lock:
                self._metrics['attacks_blocked'] += 1
        elif action == BlockAction.CHALLENGE and self.cf_config.is_configured:
            self.cf_manager.challenge_ip(ip, f"STARS: {attack_type.value}")

        with self._lock:
            self._attack_events.append(event)
            if len(self._attack_events) > 10000:
                self._attack_events = self._attack_events[-5000:]

        star_name = self.current_star.get('name', '?')
        self.logger.warning(
            f"[{star_name}] ATTACK IP={ip} Type={attack_type.value} "
            f"Rep={profile.reputation} Action={action.value}"
        )
        return action

    def _determine_action(self, profile: IPProfile,
                          attack_type: AttackType) -> BlockAction:
        critical = {AttackType.SQL_INJECTION, AttackType.COMMAND_INJECTION, AttackType.SSRF}
        if attack_type in critical and profile.violations >= 2:
            return BlockAction.BLOCK
        if profile.reputation < 20:
            return BlockAction.BLOCK
        if profile.violations == 1:
            return BlockAction.CHALLENGE
        if self.threat_intel.is_known_bad(profile.ip):
            return BlockAction.BLOCK
        if profile.reputation >= 50:
            return BlockAction.LOG_ONLY
        return BlockAction.BLOCK

    def _block_ip(self, ip: str, profile: IPProfile, source: str):
        with self._lock:
            self._blocked_ips.add(ip)
            profile.blocked_until = datetime.now() + timedelta(hours=24)
        if self.cf_config.is_configured:
            if self.cf_manager.block_ip(ip, f"STARS auto: {source}"):
                with self._lock:
                    self._metrics['cf_blocks'] += 1
        self._update_nginx_rules()
        self.logger.warning(f"[{self.current_star.get('name', '?')}] BLOCKED {ip}")

    def _update_nginx_rules(self):
        try:
            with self._lock:
                blocked = set(self._blocked_ips)
                threat_ips = set(self.threat_intel.known_bad_ips)
            self.nginx_gen.write_threat_intel_ips(threat_ips)
            self.nginx_gen.write_configs(blocked)
            threading.Thread(target=self.nginx_gen.reload_nginx, daemon=True).start()
        except Exception as e:
            self.logger.error(f"Failed to update Nginx rules: {e}")

    # ==================== 后台任务 ====================

    def _start_background_task(self, target, name: str, *args):
        stop_event = threading.Event()
        self._stop_events.append(stop_event)

        def wrapper():
            while not stop_event.is_set():
                try:
                    target(*args, stop_event)
                except TypeError:
                    target(*args)
                except Exception as e:
                    self.logger.error(f"Task {name} error: {e}")
                if not stop_event.is_set():
                    time.sleep(1)

        thread = threading.Thread(target=wrapper, daemon=True, name=name)
        thread.start()

    def _threat_intel_loop(self, stop_event: threading.Event):
        while not stop_event.is_set():
            self.threat_intel.update_all()
            stop_event.wait(3600)

    def _modsec_monitor_loop(self, stop_event: threading.Event):
        def on_attack(parsed):
            self.process_attack(
                parsed.get('ip', 'unknown'),
                parsed.get('attack_type', AttackType.UNKNOWN),
                parsed.get('message', ''),
                source="modsecurity",
            )
        self.modsec_parser.tail_log("/var/log/nginx/modsec_audit.log", on_attack, stop_event)

    def _status_reporter_loop(self, stop_event: threading.Event):
        while not stop_event.is_set():
            status = self.get_status()
            star = self.current_star.get('name', '?')
            self.logger.info(
                f"[{star}] Attacks: {status['metrics']['total_attacks']} "
                f"Blocked: {status['metrics']['attacks_blocked']} "
                f"Tracked: {status['metrics']['tracked_ips']}"
            )
            stop_event.wait(60)

    def _ip_cleanup_loop(self, stop_event: threading.Event):
        while not stop_event.is_set():
            stop_event.wait(300)
            if stop_event.is_set():
                break
            now = datetime.now()
            with self._lock:
                expired = [
                    ip for ip, p in self._ip_profiles.items()
                    if p.blocked_until and p.blocked_until < now
                    and (now - p.last_seen) > timedelta(hours=1)
                ]
                for ip in expired:
                    del self._ip_profiles[ip]
                if len(self._ip_profiles) > 50000:
                    sorted_ips = sorted(
                        self._ip_profiles.items(), key=lambda x: x[1].last_seen
                    )
                    for ip, _ in sorted_ips[:10000]:
                        del self._ip_profiles[ip]

    # ==================== 状态与报告 ====================

    def get_status(self) -> dict:
        with self._lock:
            return {
                'version': self.version,
                'uptime': str(datetime.now() - self._start_time).split('.')[0],
                'current_star': self.current_star,
                'metrics': {
                    'total_attacks': self._metrics['total_attacks'],
                    'attacks_blocked': self._metrics['attacks_blocked'],
                    'cf_blocks': self._metrics['cf_blocks'],
                    'tracked_ips': len(self._ip_profiles),
                    'blocked_ips': len(self._blocked_ips),
                    'attacks_by_type': dict(self._metrics['attacks_by_type']),
                },
                'threat_intel': {
                    'last_update': (
                        self.threat_intel.last_update.isoformat()
                        if self.threat_intel.last_update else None
                    ),
                    'known_bad_ips': len(self.threat_intel.known_bad_ips),
                },
                'cloudflare': {'configured': self.cf_config.is_configured},
                'system': {
                    'cpu': psutil.cpu_percent(),
                    'memory': psutil.virtual_memory().percent,
                },
            }

    def get_recent_attacks(self, limit: int = 50) -> List[dict]:
        with self._lock:
            events = self._attack_events[-limit:]
            return [
                {
                    'timestamp': e.timestamp.isoformat(),
                    'ip': e.ip, 'type': e.attack_type.value,
                    'detail': e.detail[:100], 'source': e.source,
                    'action': e.action_taken, 'blocked': e.blocked,
                }
                for e in reversed(events)
            ]

    def generate_report(self) -> str:
        status = self.get_status()
        star = self.current_star.get('name', '?')
        lines = [
            "=" * 60,
            f"  STARS-Gateway v{self.version}",
            f"  当值星宿: {star}",
            f"  周天星斗: {StarSystem.get_star_count()} 颗",
            f"  时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 60,
            "",
            f"  攻击总数: {status['metrics']['total_attacks']}",
            f"  已拦截:   {status['metrics']['attacks_blocked']}",
            f"  CF 封禁:  {status['metrics']['cf_blocks']}",
            f"  追踪IP:   {status['metrics']['tracked_ips']}",
            f"  封禁IP:   {status['metrics']['blocked_ips']}",
            f"  威胁库:   {status['threat_intel']['known_bad_ips']} 条",
            "",
            "[攻击分布]",
        ]
        for atype, count in status['metrics']['attacks_by_type'].items():
            lines.append(f"  {atype}: {count}")

        lines.extend(["", "[星宿历史]"])
        for s in self.star_history[-5:]:
            lines.append(f"  {s['selected_at'][:19]} - {s['name']}")

        lines.append("=" * 60)
        return "\n".join(lines)

    # ==================== 启动/停止 ====================

    def initialize(self):
        self.logger.info(f"STARS-Gateway v{self.version} initializing...")
        self.threat_intel.update_all()
        self.nginx_gen.write_configs(set())
        self.nginx_gen.write_threat_intel_ips(self.threat_intel.known_bad_ips)
        self.logger.info("Initialization complete")

    def start(self):
        self._running = True
        self._display_startup_banner()
        self.initialize()

        self._start_background_task(self._threat_intel_loop, "ThreatIntel")
        self._start_background_task(self._modsec_monitor_loop, "ModSecMonitor")
        self._start_background_task(self._status_reporter_loop, "StatusReporter")
        self._start_background_task(self._ip_cleanup_loop, "IPCleanup")

        self.status_api.start()

        star_name = self.current_star.get('name', '?')
        print(f"\n    ★ {star_name} 当值，网关运行中 ★")
        print(f"    状态: curl http://127.0.0.1:9090/status")
        print(f"    星宿: curl http://127.0.0.1:9090/star")
        print(f"    报告: curl http://127.0.0.1:9090/report")
        print(f"    Ctrl+C 停止\n")

    def stop(self):
        star_name = self.current_star.get('name', '?')
        self.logger.info(f"{star_name} 退位，正在关闭...")
        self._running = False
        for event in self._stop_events:
            event.set()
        self.status_api.stop()
        time.sleep(1)
        print(self.generate_report())

    def run(self):
        self.start()
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()


# ==================== 入口 ====================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════╗
    ║           STARS-Gateway v0.1.2                  ║
    ║           周天星斗守护系统                       ║
    ╚══════════════════════════════════════════════════╝
    """)

    emperor_mode = os.getenv('STARS_EMPEROR', '').lower() in ('true', '1', 'yes')

    gateway = STARGateway({
        'emperor_mode': emperor_mode,
        'cf_api_token': os.getenv('CF_API_TOKEN', ''),
        'cf_zone_id': os.getenv('CF_ZONE_ID', ''),
        'server_name': os.getenv('SERVER_NAME', 'example.com'),
        'upstream_host': os.getenv('UPSTREAM_HOST', '127.0.0.1'),
        'upstream_port': int(os.getenv('UPSTREAM_PORT', '3000')),
    })

    def signal_handler(sig, frame):
        gateway.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    gateway.run()
