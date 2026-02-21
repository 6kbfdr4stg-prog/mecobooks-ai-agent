"""
AutoDebugAgent - Phase 11
Tự động quét, phát hiện lỗi và báo cáo về Telegram.
Chạy mỗi ngày lúc 05:00 SA (trước các Agent khác).
"""
import ast
import os
import re
import sys
import logging
import datetime
import subprocess
import traceback
from html.parser import HTMLParser
from pathlib import Path

# Load env vars
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auto_debug_agent")

# ─── HTML Structure Checker ───────────────────────────────────────────────────
class HTMLDepthChecker(HTMLParser):
    """Checks that all HTML tags are properly balanced."""
    BLOCK_TAGS = {'div', 'section', 'article', 'main', 'aside', 'header', 'footer', 'nav', 'form', 'table', 'tbody', 'thead', 'tr', 'ul', 'ol', 'li'}

    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag in self.BLOCK_TAGS:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.BLOCK_TAGS:
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            else:
                self.errors.append(f"Unexpected </{tag}> (stack top: {self.stack[-1] if self.stack else 'empty'})")

    @property
    def final_depth(self):
        return len(self.stack)


# ─── AutoDebugAgent ───────────────────────────────────────────────────────────
class AutoDebugAgent:
    """
    Quét codebase, phát hiện lỗi phổ biến, tự sửa những gì có thể,
    và gửi báo cáo qua Telegram.
    """

    # Python files to skip (auto-generated, legacy, one-off scripts)
    SKIP_FILES = {
        'migrate_to_docker.sh', 'cloudflared', 'test_', 'debug_',
        'check_', 'diag', 'fix_', 'upgrade_ui.py', 'fix_structure.py',
        'fix_mobile_cards.py'
    }

    # Required env vars that must exist at runtime
    REQUIRED_ENV_VARS = [
        'TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID',
        'HARAVAN_SHOP_URL', 'HARAVAN_ACCESS_TOKEN',
        'GEMINI_API_KEY'
    ]

    # Dangerous patterns to flag in code
    DANGEROUS_PATTERNS = [
        (r"product\['(\w+)'\]", "Bare dict access product['{0}'] — use product.get('{0}') instead"),
        (r"item\['(\w+)'\]",    "Bare dict access item['{0}'] — use item.get('{0}') instead"),
        (r"data\['(\w+)'\]",    "Bare dict access data['{0}'] — may raise KeyError"),
        (r'except:\s*$',        "Bare 'except:' — should be 'except Exception as e:'"),
        (r'print\(.*password.*\)', "Possible password leak in print statement"),
    ]

    def __init__(self):
        self.base_dir = BASE_DIR
        self.python_files = self._collect_python_files()
        self.html_files = self._collect_html_files()
        self.issues = []       # (severity, file, line, message, auto_fixed)
        self.fixes_applied = 0
        logger.info(f"🔍 AutoDebugAgent initialized — scanning {len(self.python_files)} Python files, {len(self.html_files)} HTML files")

    def _should_skip(self, path: str) -> bool:
        name = os.path.basename(path)
        return any(skip in name for skip in self.SKIP_FILES)

    def _collect_python_files(self):
        py_files = []
        for root, dirs, files in os.walk(self.base_dir):
            # Skip virtual envs, git, cache, library dirs
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'lib', 'node_modules', '.venv', 'venv', 'psutil_backup', 'psutil-7.2.2.dist-info'}]
            for f in files:
                if f.endswith('.py') and not self._should_skip(f):
                    py_files.append(os.path.join(root, f))
        return py_files

    def _collect_html_files(self):
        html_files = []
        for root, _, files in os.walk(os.path.join(self.base_dir, 'templates')):
            for f in files:
                if f.endswith('.html'):
                    html_files.append(os.path.join(root, f))
        return html_files

    # ── Check 1: Python Syntax ─────────────────────────────────────────────
    def check_python_syntax(self):
        """Parse every .py file with ast to catch SyntaxErrors."""
        ok_count = 0
        for fpath in self.python_files:
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    source = f.read()
                ast.parse(source, filename=fpath)
                ok_count += 1
            except SyntaxError as e:
                self.issues.append({
                    'severity': 'ERROR',
                    'file': os.path.relpath(fpath, self.base_dir),
                    'line': e.lineno,
                    'message': f"SyntaxError: {e.msg}",
                    'auto_fixed': False
                })
            except Exception as e:
                self.issues.append({
                    'severity': 'WARN',
                    'file': os.path.relpath(fpath, self.base_dir),
                    'line': 0,
                    'message': f"Could not parse: {e}",
                    'auto_fixed': False
                })
        logger.info(f"✅ Syntax check: {ok_count}/{len(self.python_files)} files OK")

    # ── Check 2: Dangerous Code Patterns ──────────────────────────────────
    def check_dangerous_patterns(self):
        """Scan source files for risky patterns that likely cause KeyErrors."""
        pattern_hits = 0
        for fpath in self.python_files:
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                for lineno, line in enumerate(lines, start=1):
                    for pattern, msg_template in self.DANGEROUS_PATTERNS:
                        matches = re.findall(pattern, line)
                        for match in matches:
                            key = match if isinstance(match, str) else match[0]
                            # Skip lines that already use .get(
                            if '.get(' in line:
                                continue
                            message = msg_template.format(key)
                            self.issues.append({
                                'severity': 'WARN',
                                'file': os.path.relpath(fpath, self.base_dir),
                                'line': lineno,
                                'message': message,
                                'auto_fixed': False
                            })
                            pattern_hits += 1
            except Exception:
                pass
        logger.info(f"⚠️  Pattern check: {pattern_hits} risky patterns found")

    # ── Check 3: Missing Environment Variables ─────────────────────────────
    def check_env_vars(self):
        """Verify all required environment variables are set."""
        from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, HARAVAN_ACCESS_TOKEN, GEMINI_API_KEY
        env_map = {
            'TELEGRAM_BOT_TOKEN': TELEGRAM_BOT_TOKEN,
            'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
            'HARAVAN_ACCESS_TOKEN': HARAVAN_ACCESS_TOKEN,
            'GEMINI_API_KEY': GEMINI_API_KEY,
        }
        missing = []
        for var, val in env_map.items():
            if not val or val.strip() == '':
                missing.append(var)
                self.issues.append({
                    'severity': 'ERROR',
                    'file': '.env / config.py',
                    'line': 0,
                    'message': f"Missing required env var: {var}",
                    'auto_fixed': False
                })
        if missing:
            logger.warning(f"🔴 Missing env vars: {missing}")
        else:
            logger.info(f"✅ All {len(env_map)} required env vars are set")

    # ── Check 4: HTML Structure Balance ───────────────────────────────────
    def check_html_structure(self):
        """Check that every HTML file has balanced block-level tags."""
        for hpath in self.html_files:
            try:
                with open(hpath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                checker = HTMLDepthChecker()
                checker.feed(content)
                if checker.final_depth != 0:
                    self.issues.append({
                        'severity': 'WARN',
                        'file': os.path.relpath(hpath, self.base_dir),
                        'line': 0,
                        'message': f"HTML imbalance — {checker.final_depth} unclosed tags remain. Unmatched: {checker.stack[-3:]}",
                        'auto_fixed': False
                    })
                elif checker.errors:
                    for err in checker.errors[:3]:
                        self.issues.append({
                            'severity': 'WARN',
                            'file': os.path.relpath(hpath, self.base_dir),
                            'line': 0,
                            'message': f"HTML error: {err}",
                            'auto_fixed': False
                        })
                else:
                    logger.info(f"✅ HTML OK: {os.path.basename(hpath)}")
            except Exception as e:
                logger.warning(f"Could not check HTML {hpath}: {e}")

    # ── Check 5: API Health Ping ───────────────────────────────────────────
    def check_api_health(self):
        """Try to reach the deployed Render /health endpoint."""
        import requests
        endpoints = [
            ("https://mecobooks-ai-agent.onrender.com/health", "Render /health"),
        ]
        for url, label in endpoints:
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    logger.info(f"✅ {label}: {resp.status_code}")
                else:
                    self.issues.append({
                        'severity': 'WARN',
                        'file': label,
                        'line': 0,
                        'message': f"HTTP {resp.status_code} — server might be restarting",
                        'auto_fixed': False
                    })
            except requests.exceptions.ConnectionError:
                self.issues.append({
                    'severity': 'WARN',
                    'file': label,
                    'line': 0,
                    'message': "Could not connect — server might be sleeping (Render free tier spin-up)",
                    'auto_fixed': False
                })
            except Exception as e:
                self.issues.append({
                    'severity': 'WARN',
                    'file': label,
                    'line': 0,
                    'message': f"Health check error: {e}",
                    'auto_fixed': False
                })

    # ── Check 6: Import Dependencies ──────────────────────────────────────
    def check_imports(self):
        """Parse each file's imports and flag missing third-party packages."""
        stdlib = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else set()
        local_modules = {'config', 'database', 'haravan_client', 'llm_service', 'woocommerce_client', 'ai_agents', 'utils', 'scheduler'}
        for fpath in self.python_files:
            try:
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    source = f.read()
                tree = ast.parse(source)
                for node in ast.walk(tree):
                    if isinstance(node, (ast.Import, ast.ImportFrom)):
                        mod = node.names[0].name.split('.')[0] if isinstance(node, ast.Import) else (node.module or '').split('.')[0]
                        if mod and mod not in stdlib and mod not in local_modules:
                            try:
                                __import__(mod)
                            except ImportError:
                                self.issues.append({
                                    'severity': 'ERROR',
                                    'file': os.path.relpath(fpath, self.base_dir),
                                    'line': node.lineno,
                                    'message': f"ImportError: '{mod}' is not installed",
                                    'auto_fixed': False
                                })
            except Exception:
                pass

    # ── Build Report & Telegram ───────────────────────────────────────────
    def _build_report(self, duration_s: float) -> str:
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        errors = [i for i in self.issues if i['severity'] == 'ERROR']
        warnings = [i for i in self.issues if i['severity'] == 'WARN']

        status_icon = "🔴" if errors else ("⚠️" if warnings else "✅")
        lines = [
            f"🔍 **AutoDebug Report** — {now}",
            f"{status_icon} {len(errors)} lỗi nghiêm trọng • {len(warnings)} cảnh báo",
            f"📁 Đã quét: {len(self.python_files)} file Python, {len(self.html_files)} file HTML",
            f"⏱️ Mất: {duration_s:.1f}s",
            "",
        ]

        if errors:
            lines.append("🚨 **LỖI NGHIÊM TRỌNG:**")
            for i in errors[:8]:
                fixed_str = " *(đề xuất sửa)*" if i['auto_fixed'] else ""
                lines.append(f"  • `{i['file']}:{i['line']}` — {i['message']}{fixed_str}")
            if len(errors) > 8:
                lines.append(f"  … và {len(errors) - 8} lỗi khác")
            lines.append("")

        if warnings:
            lines.append("⚠️ **CẢNH BÁO:**")
            for i in warnings[:8]:
                lines.append(f"  • `{i['file']}:{i['line']}` — {i['message']}")
            if len(warnings) > 8:
                lines.append(f"  … và {len(warnings) - 8} cảnh báo khác")
            lines.append("")

        if not errors and not warnings:
            lines.append("🎉 **Codebase sạch bóng! Không phát hiện vấn đề nào.**")

        return "\n".join(lines)

    def _save_report(self, report_text: str) -> str:
        report_dir = os.path.join(self.base_dir, "integrity_reports")
        os.makedirs(report_dir, exist_ok=True)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
        report_path = os.path.join(report_dir, f"auto_debug_{date_str}.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"# AutoDebug Report — {date_str}\n\n")
            f.write(report_text.replace("**", "").replace("`", "'"))
            f.write("\n\n## Issues Detail\n")
            for i in self.issues:
                f.write(f"- [{i['severity']}] `{i['file']}:{i['line']}` — {i['message']}\n")
        return report_path

    def run(self):
        """Run all checks and send Telegram report."""
        start = datetime.datetime.now()
        logger.info("🔍 [AutoDebug] Starting full project scan...")

        self.check_python_syntax()
        self.check_env_vars()
        self.check_dangerous_patterns()
        self.check_html_structure()
        self.check_api_health()
        self.check_imports()

        duration = (datetime.datetime.now() - start).total_seconds()
        report_text = self._build_report(duration)
        report_path = self._save_report(report_text)

        logger.info(f"📄 Report saved: {report_path}")
        print(report_text)

        # Send to Telegram
        try:
            from ai_agents.telegram_client import send_telegram_message
            # Telegram message is a shorter summary
            errors = [i for i in self.issues if i['severity'] == 'ERROR']
            warnings = [i for i in self.issues if i['severity'] == 'WARN']
            status = "🔴 Cần xử lý ngay!" if errors else ("⚠️ Có cảnh báo" if warnings else "✅ Hệ thống sạch")
            msg = (
                f"🔍 AutoDebug Agent — {datetime.datetime.now().strftime('%d/%m %H:%M')}\n"
                f"{status}\n"
                f"• Lỗi: {len(errors)} | Cảnh báo: {len(warnings)}\n"
                f"• Files quét: {len(self.python_files)} Python + {len(self.html_files)} HTML\n"
            )
            if errors:
                msg += "\n🚨 Lỗi nghiêm trọng:\n"
                for e in errors[:4]:
                    msg += f"  • {e['file']} — {e['message'][:60]}\n"
            if warnings:
                msg += "\n⚠️ Top cảnh báo:\n"
                for w in warnings[:3]:
                    msg += f"  • {w['file']} — {w['message'][:60]}\n"
            send_telegram_message(msg)
            logger.info("📤 Telegram notification sent")
        except Exception as e:
            logger.warning(f"Could not send Telegram: {e}")

        return {
            'status': 'success',
            'errors': len([i for i in self.issues if i['severity'] == 'ERROR']),
            'warnings': len([i for i in self.issues if i['severity'] == 'WARN']),
            'report_path': report_path,
            'output': report_text
        }


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    agent = AutoDebugAgent()
    result = agent.run()
    sys.exit(0 if result['errors'] == 0 else 1)
