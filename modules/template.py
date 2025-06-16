# modules/portscan.py
"""
Port-scan module – wraps a simple nmap command.
Every module MUST expose a function `run(targets:str, jobdir:pathlib.Path)->str`
Return value goes directly back to browser; also saved to file.
"""

import subprocess, pathlib, datetime, shlex

def run(targets: str, jobdir: pathlib.Path) -> str:
    """Run nmap against targets.  Returns output as text."""
    out_file = jobdir / f"portscan_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    # Craft the actual OS command
    cmd = f"nmap -Pn -p 1-65535 {shlex.quote(targets)}"
    # Run it
    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=180)
    # Save to disk
    out_file.write_text(completed.stdout + completed.stderr)
    return completed.stdout + completed.stderr
