import os
import re
import shutil
import subprocess
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    send_from_directory,
    send_file,
    escape,
    flash,
)
from werkzeug.utils import secure_filename
from datetime import datetime

from tokengenerator import add_used, check_used_token, check_token_valid

ALLOWED_EXTENSIONS = set(["fasta"])


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_string(
    in_string: str, info: str, token_as: str = None, remove_token: bool = False
):
    if in_string is None:
        info = "Input is None"
        return False, None
    else:
        in_string = str(in_string)
        check = bool(re.match("^[A-Za-z0-9_-]+[A-Za-z0-9_.-]*$", in_string))
    if not check:
        flash(info)
        if remove_token:
            os.system(f"python3 tokenremove.py --token {token_as}")
        return False, None
    else:
        return True, secure_filename(escape(in_string))


def fasta_check(fasta_path: str, max_protein: int = 3):
    """check fasta file for number of sequences"""
    header_count = 0
    with open(fasta_path, "r") as fasta:
        for i in fasta:
            if i.startswith(">"):
                header_count += 1
            if header_count > max_protein:
                return 2
    if header_count == 0:
        return 1
    elif header_count > max_protein:
        return 2
    return 0


def remove_token_after_crash(token_in):
    os.system(f"python3 tokenremove.py --token {token_in}")


def add_string(nmodels: str, amber_rel: str, nrecyles: str):
    """get additional setting in the colabfold call string"""
    nmodels_add = f"--num-models {nmodels}"
    amber_rel_add = ""
    if amber_rel == "amber_relax":
        amber_rel_add = f" --amber --use-gpu-relax"
    nrecyles_add = ""
    if nrecyles != "auto":
        nrecyles_add = f" --num-recycle {nrecyles}"
    return " " + nmodels_add + amber_rel_add + nrecyles_add + " --zip"


def ip_log(req, access, fpath="log_files"):
    ip_addr = req.environ.get("HTTP_X_FORWARDED_FOR", req.remote_addr)
    with open(os.path.join(fpath,"ip.log"), "a+") as iplog:
        ip_string = f"{datetime.now().strftime('%d%m%y_%H%M%S')},{ip_addr},{access}\n"
        iplog.write(ip_string)


def create_app():
    app = Flask(__name__, template_folder="./templates", static_folder="./static")
    app.config["TEMPLATES_AUTO_RELOAD"]
    out_dir = "/mnt/ssd2/colabfold/"
    max_jobs = 10
    max_tokens = 3
    log_path = "log_files"
    if not os.path.isdir(log_path):
        os.mkdir(log_path)

    app.secret_key = b'_7#t9k"w2F5z\n\xec]/'

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500

    @app.route("/")
    def running():
        num_proc = sum(1 for line in open("/var/pid_storage/pid_store.txt"))
        if num_proc >= max_jobs:
            return redirect(url_for("busy"))
        ip_log(request, "home")
        return render_template("index.html", number=num_proc)

    @app.route("/busy")
    def busy():
        return render_template("busy.html")

    @app.route("/inputerror")
    def error():
        ip_log(request, "inputerror")
        return render_template("input_error.html")

    @app.route("/exceeded")
    def exceeded():
        ip_log(request, "exceeded")
        return render_template("exceeded.html")

    @app.route("/submitted")
    def submitted():
        return render_template("submitted.html")

    @app.route("/overused_token")
    def overused_token():
        ip_log(request, "overused_token")
        return render_template("overused_token.html")

    @app.route("/changes")
    def changes():
        ip_log(request, "changes")
        return render_template("changes.html")

    @app.route("/guide")
    def guide():
        ip_log(request, "guide")
        return render_template("guide.html")

    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        ip_log(request, "upload")
        num_proc = sum(1 for line in open("/var/pid_storage/pid_store.txt"))
        if num_proc >= max_jobs:
            return redirect(url_for("busy"))
        if request.method == "POST":
            file = request.files["file"]

            token = request.form.get("token_in")

            t_check, _ = allowed_string(token, info="Insecure Token")
            if not t_check:
                return redirect(url_for("upload"))
            if not check_token_valid(token):
                flash("Invalid Token")
                return redirect(url_for("upload"))
            if not check_used_token(token, max_tokens):
                return redirect(url_for("overused_token"))

            if file and allowed_file(file.filename):
                add_used(token)
                user_dir = request.form.get("user")
                u_check1, sec_user_dir = allowed_string(
                    user_dir,
                    info="User name contains forbidden characters",
                    token_as=token,
                    remove_token=True,
                )
                if not u_check1:
                    remove_token_after_crash(token)
                    return redirect(url_for("upload"))
                user_path = os.path.join(out_dir, sec_user_dir)
                if not os.path.isdir(user_path):
                    os.mkdir(user_path)

                filename_in = file.filename
                u_check2, sec_filename = allowed_string(
                    filename_in,
                    info="File name contains forbidden characters",
                    token_as=token,
                    remove_token=True,
                )
                if not u_check2:
                    remove_token_after_crash(token)
                    return redirect(url_for("upload"))
                filename_pre = sec_filename.split(".")[0]
                sec_filename = "".join(list(filename_pre)[:15])
                new_name = f"{sec_filename}_{datetime.now().strftime('%d%m%y_%H%M%S')}"
                dir_name = os.path.join(user_path, new_name)
                os.mkdir(dir_name)
                new_filename = f"{new_name}.fasta"
                fasta_loc = os.path.join(dir_name, new_filename)
                file.save(fasta_loc)

                input_check = fasta_check(fasta_loc)
                if input_check == 1:
                    os.system(f"rm -r {dir_name}")
                    remove_token_after_crash(token)
                    return redirect(url_for("error"))
                elif input_check == 2:
                    os.system(f"rm -r {dir_name}")
                    remove_token_after_crash(token)
                    return redirect(url_for("exceeded"))

                nmodels_in = request.form.get("num_models")
                nm_check, sec_nmodels_in = allowed_string(
                    nmodels_in, info="Invalid number of models"
                )
                if not nm_check:
                    remove_token_after_crash(token)
                    return redirect(url_for("upload"))

                amberrel_in = request.form.get("amber_relax")
                if amberrel_in is not None:
                    ar_check, sec_amberrel_in = allowed_string(
                        amberrel_in, info="Invalid amber relax"
                    )
                    if not ar_check:
                        remove_token_after_crash(token)
                        return redirect(url_for("upload"))
                else:
                    sec_amberrel_in = amberrel_in

                ncycles_in = request.form.get("num_recycles")
                nc_check, sec_ncycles_in = allowed_string(
                    ncycles_in, info="Invalid number of recycles"
                )
                if not nc_check:
                    remove_token_after_crash(token)
                    return redirect(url_for("upload"))

                additional_settings = add_string(
                    sec_nmodels_in, sec_amberrel_in, sec_ncycles_in
                )

                cfold_out = os.path.join(dir_name, "out")
                scheduler_path = "/home/cfolding/.scheduler/schedule.sh"
                colabfold_path = (
                    "/home/cfolding/colabfold_batch/colabfold-conda/bin/colabfold_batch"
                )
                folding = f"bash {scheduler_path} '{colabfold_path} {fasta_loc} {cfold_out} {additional_settings}'"

                zipping = f"mv {cfold_out}/*.zip {dir_name}.zip"
                removing = f"rm -r {dir_name}"
                token_removing = f"python3 tokenremove.py --token {token}"
                nohup_path = f"/mnt/ssd2/cf_nohup/{new_name}.out"

                os.system(
                    "nohup sh -c "
                    + '"'
                    + f"{folding} && {zipping} && {removing} ; {token_removing}"
                    + '"'
                    + f" > {nohup_path} &"
                )
                return redirect(url_for("submitted"))
            else:
                return redirect(url_for("error"))
        return render_template("upload.html")

    @app.route("/download", methods=["GET", "POST"])
    def download():
        ip_log(request, "download")
        if request.method == "POST":
            uname_in = request.form.get("user")
            d_check1, sec_uname = allowed_string(
                uname_in, info="User name contains forbidden characters"
            )
            if not d_check1:
                return redirect(url_for("download"))
            redir_url = f"/download_files?user={sec_uname}"
            if not os.path.isdir(os.path.join(out_dir, sec_uname)):
                flash("Invalid user name")
                return redirect(url_for("download"))
            return redirect(redir_url)
        return render_template("download_user.html")

    @app.route("/download_files", methods=["GET", "POST"])
    def download_files():
        user_name_in = request.args.get("user", None)
        # check if user name contains forbidden characters
        d_check2, sec_user_name = allowed_string(
            user_name_in, info="User name contains forbidden characters"
        )
        if not d_check2:
            return redirect(url_for("download"))
        # check if user name exists
        user_path_ = os.path.join(out_dir, sec_user_name)
        if not os.path.isdir(user_path_):
            flash("Invalid user name")
            return redirect(url_for("download"))
        # request file for download
        if request.method == "POST":
            redir_url = f"/download_files?user={sec_user_name}"
            req_file = request.form.get("file")
            # check if no file was selected
            if req_file is None:
                flash("No file present")
                return redirect(redir_url)
            # check if file name contains forbidden characters
            d_check3, sec_req_file = allowed_string(
                req_file, info="File name contains forbidden characters"
            )
            if not d_check3:
                return redirect(redir_url)
            # check if it exists
            req_file_path = os.path.join(user_path_, sec_req_file)
            if not os.path.isfile(req_file_path):
                flash("File doesn't exist")
                return redirect(redir_url)
            return send_file(req_file_path)

        files = [
            os.path.join(user_path_, i) for i in os.listdir(user_path_) if ".zip" in i
            ]
        files.sort(key=os.path.getmtime)
        files = [os.path.split(i)[1] for i in files]
        files = files[::-1]
        return render_template("download_files.html", files=files)

    @app.route("/example/")
    def example():
        ip_log(request, "example")
        return render_template(
            "example.html", files=[i for i in os.listdir("example") if ".fasta" in i]
        )

    @app.route("/example/<filename>")
    def example_file(filename):
        e_check, sec_filename = allowed_string(
            filename, info="File name contains forbidden characters"
        )
        if not e_check:
            return redirect(url_for("example"))
        if not os.path.isfile(os.path.join("example", sec_filename)):
            flash("File doesn't exist")
            return redirect(url_for("example"))
        return send_from_directory("example", sec_filename)

    return app


if __name__ == "__main__":
    pass
