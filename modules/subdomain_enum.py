import subprocess, pathlib, datetime, shlex

def run(targets:str, jobdir:pathlib.Path)->str:
    outfile = jobdir / f"subenum_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.txt"
    cmd     = f"subfinder -d {shlex.quote(targets)}"
    c       = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
    outfile.write_text(c.stdout + c.stderr)
    return c.stdout + c.stderr
