import os
import hashlib
from flask import (
    Flask,
    request,
    render_template,
    redirect,
    url_for,
    send_from_directory,
    send_file,
    flash,
)
from datetime import datetime

from tokengenerator import add_used, check_used_token, check_token_valid
from app_utils import (
    gen_key,
    get_key,
    allowed_file,
    allowed_string,
    fasta_check,
    json_check,
    remove_token_after_crash,
    add_string,
    ip_log,
    file_path_dict,
)
from make_bash import make_bash_file

FILE_PATHS = file_path_dict()

def hash_job(bash_file_path: str) -> str:
    name = bash_file_path.strip().split(" ")[-1]
    return hashlib.md5(name.encode()).hexdigest()[:10]


def create_app():
    app = Flask(__name__, template_folder="./templates", static_folder="./static")
    app.config["TEMPLATES_AUTO_RELOAD"]
    out_dir = FILE_PATHS["storage_base"]
    schedule_dir = f"{FILE_PATHS['loc_prod_path']}/schedule/"
    max_jobs = 10
    max_tokens = 3
    log_path = "log_files"
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

    # clear used tokens on app startup
    with open(f"{FILE_PATHS['loc_prod_path']}/tokens/used_tokens.txt", "w+"):
        pass

    # generates secret_key if not present
    gen_key(dir_name=log_path)
    # read secret_key
    app.secret_key = get_key()

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("500.html"), 500

    @app.route("/")
    def running():
        sched_path = f"{os.path.join(schedule_dir, 'execution_shedule.txt')}"
        if os.path.isfile(sched_path):
            num_proc = sum(1 for line in open(sched_path))
        else:
            num_proc = 0
        start_date = "01.01.1970"
        n_lines = 0
        with open("./schedule/log.file", "r") as lfile:
            for ci, i in enumerate(lfile):
                if ci == 0:
                    if len(i) > 0 and "~~" in i:
                        start_date = ".".join(i.split("~~")[1].split("-")[:3][::-1])
                n_lines += 1
        ip_log(request, "home")
        return render_template(
            "index.html", number=num_proc, start_date=start_date, n_jobs=n_lines
        )

    @app.route("/api/usage")
    def get_usage():
        sched_path = f"{os.path.join(schedule_dir, 'execution_shedule.txt')}"
        current_run = ""
        with open(sched_path, "r") as f:
            now = f.readline().strip("\n")
            if len(now) > 0:
                current_run = hash_job(now)
        cpu_usage = float(
            (
                os.popen(
                    "top -bn 2 -d 0.01 | grep '^%Cpu' | tail -n 1 | awk '{print $2+$4+$6}'"
                )
                .read()
                .strip()
                .replace(",", ".")
            )
        )
        try:
            cpu_usage = int(cpu_usage)
        except Exception as e:
            print(e)
            print(f"Error while checking cpu usage '{cpu_usage}'")
            cpu_usage = 0

        ram = (
            os.popen("free -m | awk 'NR==2{printf \"%s %s\", $3,$2 }'")
            .read()
            .strip()
            .split(" ")
        )
        if len(ram) != 2:
            ram_usage = 0
        else:
            try:
                used_ram = int(ram[0])
                total_ram = int(ram[1])
                ram_usage = int((used_ram / total_ram) * 100)
            except Exception as e:
                print(e)
                print(f"Error while checking ram usage '{ram_usage}'")
                ram_usage = 0

        gpu_usage = (
            os.popen(
                "nvidia-smi --query-gpu 'utilization.gpu' --format=csv,noheader,nounits"
            )
            .read()
            .strip()
        )
        try:
            gpu_usage = int(gpu_usage)
        except Exception as e:
            print(e)
            print(f"Error while checking gpu usage '{gpu_usage}'")
            gpu_usage = 0
        return {
            "cpu": cpu_usage,
            "gpu": gpu_usage,
            "ram": ram_usage,
            "current_job": current_run,
        }

    @app.route("/queue")
    def queue():
        sched_path = f"{os.path.join(schedule_dir, 'execution_shedule.txt')}"
        jobs = []
        with open(sched_path, "r") as sfile:
            for i in sfile:
                iname = hash_job(i.split(" ")[-1])
                jobs.append(iname)
        ip_log(request, "queue")
        return render_template("queue.html", jobs=jobs)

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
        # number of currently running/scheduled jobs
        sched_path = f"{os.path.join(schedule_dir, 'execution_shedule.txt')}"
        if os.path.isfile(sched_path):
            num_proc = sum(1 for line in open(sched_path))
        else:
            num_proc = 0
        if num_proc >= max_jobs:
            return redirect(url_for("busy"))
        if request.method == "POST":
            # get file
            file = request.files["file"]
            # get token
            token = request.form.get("token_in")
            # check token safety
            t_check, _ = allowed_string(token, info="Insecure Token")
            # token safe?
            if not t_check:
                return redirect(url_for("upload"))
            # token valid?
            if not check_token_valid(token):
                flash("Invalid Token")
                return redirect(url_for("upload"))
            # token usage?
            if not check_used_token(token, max_tokens):
                return redirect(url_for("overused_token"))
            # valid file?
            if file and allowed_file(file.filename):
                # add token to currently used ones
                add_used(token)
                # user
                user_dir = request.form.get("user")
                u_check1, sec_user_dir = allowed_string(
                    user_dir,
                    info="User name contains forbidden characters",
                    token_as=token,
                    remove_token=True,
                )
                # user name safe?
                if not u_check1:
                    remove_token_after_crash(token)
                    return redirect(url_for("upload"))
                user_path = os.path.join(out_dir, sec_user_dir)
                # user path safe?
                if not os.path.isdir(user_path):
                    os.mkdir(user_path)

                filename_in = file.filename
                u_check2, sec_filename = allowed_string(
                    filename_in,
                    info="File name contains forbidden characters",
                    token_as=token,
                    remove_token=True,
                )
                # file name safe?
                if not u_check2:
                    remove_token_after_crash(token)
                    return redirect(url_for("upload"))
                # add date to filename and cut if to long
                filename_pre = sec_filename.split(".")[0]
                sec_filename = "".join(list(filename_pre)[:30])
                new_name = f"{sec_filename}_{datetime.now().strftime('%d%m%y_%H%M%S')}"
                # create output dir
                dir_name = os.path.join(user_path, new_name)
                os.mkdir(dir_name)
                afv = 3
                if os.path.splitext(filename_in)[-1].replace(".", "").startswith("fa"):
                    afv = 2
                if afv == 2:
                    # save fasta file
                    new_filename = f"{new_name}.fasta"
                    fasta_loc = os.path.join(dir_name, new_filename)
                    file.save(fasta_loc)
                elif afv == 3:
                    # save json file
                    new_filename = f"{new_name}.json"
                    json_loc = os.path.join(dir_name, new_filename)
                    file.save(json_loc)

                if afv == 2:
                    input_check = fasta_check(fasta_loc)
                elif afv == 3:
                    input_check = json_check(json_loc, max_seqlen=10000)
                if input_check == 1:
                    flash("Invalid JSON formatting")
                    os.system(f"rm -r {dir_name}")
                    remove_token_after_crash(token)
                    return redirect(url_for("upload"))
                elif input_check == 2:
                    os.system(f"rm -r {dir_name}")
                    remove_token_after_crash(token)
                    return redirect(url_for("exceeded"))
                elif input_check == 3:
                    os.system(f"rm -r {dir_name}")
                    remove_token_after_crash(token)
                    return redirect(url_for("exceeded"))

                if afv == 2:
                    # check and get the additional_settings for colabfold
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
                    # generate commands that should be executed
                    cfold_out = os.path.join(dir_name, "out")
                    colabfold_path = FILE_PATHS["colabfold_path"]
                    folding = f"{colabfold_path} {fasta_loc} {cfold_out} {additional_settings} 2>&1 | tee {dir_name}/log.file"
                    git_hash = "echo 'No git hash available'"
                elif afv == 3:
                    cfold_out = os.path.join(dir_name, "out")
                    colabfold_path = FILE_PATHS["colabfold_path"]
                    folding = f"{FILE_PATHS['docker_path']} run --volume {dir_name}:/root/af_input --volume {cfold_out}:/root/af_output --volume {FILE_PATHS['weights_path']}:/root/models --volume {FILE_PATHS['db_path']}:/root/public_databases --gpus all alphafold3 python run_alphafold.py --json_path=/root/af_input/{os.path.basename(json_loc)} --model_dir=/root/models --output_dir=/root/af_output 2>&1 | tee {dir_name}/log.file"
                    git_hash = f"{FILE_PATHS['python_path']} {FILE_PATHS['loc_prod_path']}/git_hash_log.py --log_path {dir_name}/log.file"

                zipout = f"{FILE_PATHS['python_path']} {FILE_PATHS['loc_prod_path']}/zipping.py -f {dir_name} -d {dir_name}"
                token_removing = f"{FILE_PATHS['python_path']} {FILE_PATHS['loc_prod_path']}/tokenremove.py --token {token}"
                time_start = f'echo "START $(date +%Y-%m-%d_%H:%M:%S)" > {dir_name}/prediction_time.txt'
                time_end = f'echo "END   $(date +%Y-%m-%d_%H:%M:%S)" >> {dir_name}/prediction_time.txt'

                # create bash file to execute the folding and submit job
                bash_path = make_bash_file(
                    new_name,
                    [time_start, folding, time_end, git_hash, zipout, token_removing],
                )
                return render_template("submitted.html", job_hash=hash_job(bash_path))
            else:
                return redirect(url_for("error"))
        return render_template("upload.html")

    @app.route("/download", methods=["GET", "POST"])
    def download():
        ip_log(request, "download")
        if request.method == "POST":
            # get user name and redirect to its folder if safe and exists
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
        # sort files names in chronological order
        files.sort(key=os.path.getmtime)
        files = [os.path.split(i)[1] for i in files]
        files = files[::-1]
        return render_template("download_files.html", files=files)

    @app.route("/example/")
    def example():
        ip_log(request, "example")
        return render_template(
            "example.html",
            files_fasta=[i for i in os.listdir("example") if ".fasta" in i],
            files_json=[i for i in os.listdir("example") if ".json" in i],
            files_html=[i for i in os.listdir("example") if ".html" in i],
        )

    @app.route("/example/<filename>")
    def example_file(filename):
        # show example fasta files for download
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
