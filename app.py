# app.py
import os, datetime, importlib.util, pathlib, subprocess, logging, json
from flask import Flask, request, jsonify, send_from_directory, render_template

BASE_DIR      = pathlib.Path(__file__).parent.resolve()
JOB_ROOT      = BASE_DIR / "jobs"
MODULE_DIR    = BASE_DIR / "modules"
LOG_DIR       = BASE_DIR / "logs"
LOG_FILE      = LOG_DIR / "commands.log"

# ------------------------------------------------------------------ logging
LOG_DIR.mkdir(exist_ok=True)
logging.basicConfig(
    filename=LOG_FILE,
    format="%(asctime)s %(message)s",
    level=logging.INFO
)

# ------------------------------------------------------------------ load modules dynamically
def load_modules():
    """return dict  {command_name: python_function}"""
    commands = {}
    for py in MODULE_DIR.glob("*.py"):
        spec = importlib.util.spec_from_file_location(py.stem, py)
        mod  = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "run"):
            commands[py.stem] = mod.run
    return commands

COMMANDS = load_modules()

# ------------------------------------------------------------------ helpers
def timestamp():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")

def ensure_job_dir(jobname):
    jobdir = JOB_ROOT / jobname
    jobdir.mkdir(parents=True, exist_ok=True)
    return jobdir

def save_targets(jobdir, targets):
    file = jobdir / "targets.txt"
    with open(file, "w") as f:
        f.write(targets.strip() + "\n")

# ------------------------------------------------------------------ flask
app = Flask(__name__, static_folder="")

@app.route("/")
def index():
    return render_template("index.html", modules=list(COMMANDS.keys()))

@app.route("/api/run", methods=["POST"])
def api_run():
    data       = request.get_json(force=True)
    cmd_name   = data.get("command")
    targets    = data.get("targets", "").strip()
    jobname    = data.get("job").strip().replace(" ", "_")

    if cmd_name not in COMMANDS:
        return jsonify({"error": "Unknown command"}), 400

    jobdir     = ensure_job_dir(jobname)
    save_targets(jobdir, targets)

    # ------------- run the module
    start      = timestamp()
    output     = COMMANDS[cmd_name](targets, jobdir)        # <- module returns plain text
    end        = timestamp()

    # log
    logging.info(f"{cmd_name} | {jobname} | {targets} | start:{start} end:{end}")

    return jsonify({"ok":True, "out":output})

@app.route("/api/log", methods=["GET"])
def api_log():
    with open(LOG_FILE) as f:
        return "<pre style='white-space:pre-wrap'>" + f.read() + "</pre>"

# ------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
