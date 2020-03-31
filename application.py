import os, json, settings, sqlite3, hashlib, sys
from flask import Flask, request, redirect, url_for, render_template, flash, send_file, abort, Response, jsonify
from random import randint
from datetime import datetime
from NIKEutil.logger import logger
from NIKEml.taskRunner import nikeTaskRunner
from NIKEml.taskDefinitions import taskDefinitions
from NIKEml.status import nikeMLStatus
from os import path



###############################CONFIG#######################################
DATA_PATH = os.getenv("data_path")
HOST_IN_TWISTED = os.getenv("host_in_twisted")
BUILTINPORT =  os.getenv("builtin_port") if os.getenv("builtin_port") != "" else 8080
TWISTEDPORT = os.getenv("twisted_port") if os.getenv("twisted_port") != "" else 5000
TWISTEDIP = os.getenv("twisted_ip") if os.getenv("twisted_ip") != "" else "127.0.0.1"
TWISTEDLOGFILE = "app.log"
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
# Session seed, for per-session data
app.secret_key = os.urandom(24)
salt = "MySuperSecretSaltToCorrectAnErrorIMadeDurringDev"  # Have to hash the passwords otherwise you can SQL inject the password field and bypass my challenge. Duh


################################METHODS######################################
# Start up Stuff

# Start a twistd server
def twisted():
    # print 'Twisted on port {port}...'.format(port=TWISTEDPORT)
    # Only import these if we need them
    #
    print("Listening on {0}:{1}".format("0.0.0.0", TWISTEDPORT))
    from twisted.internet import reactor
    from twisted.web.server import Site
    from twisted.web.wsgi import WSGIResource
    from twisted.python import log as twisted_log
    print("Adding twisted logging")
    twisted_log.startLogging(file=open(TWISTEDLOGFILE, "w"))
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    site = Site(resource)
    reactor.listenTCP(int(TWISTEDPORT), site, interface=TWISTEDIP)
    reactor.run()

# start a built in flask server


def builtin():
    # print 'Built-in development server on port {port}...'.format(port=BUILTINPORT)
    app.run(host="0.0.0.0", port=int(BUILTINPORT), debug=True)

# END Start up Stuff

def log(event):
    print("[+] {0} - {1}".format(datetime.now(), event))


###############################VIEWS#######################################


# Health check
@app.route("/status", methods=['GET'])
def status():
    ip = request.remote_addr  # IP of visitor for logging
    return '{"status": "OK"}'

@app.route("/", methods=['GET'])
def index():
    ip = request.remote_addr  # IP of visitor for logging
    return render_template("index.html")



@app.route('/task/<task_name>', methods=['GET'])
def run_task(task_name):
    force = request.args.get('force',default=False)
    details = request.args.get('details',default=False)

    if not task_name in taskDefinitions.keys():
        pass
    else:
        if details: 
            return jsonify(taskDefinitions[task_name]) # Returns task definition
        else:
            taskRunner = nikeTaskRunner()
            result = taskRunner.runTask(task_name, force=force)
            return jsonify({"state": result.state, "status": result.status, "runnable": result.runnable, "forcible":result.forcible })

# TO DO: Consolidate api routes to one call with case-like statement on action request

@app.route('/api/status', methods=['GET'])
def get_status():
    status = nikeMLStatus()
    result = status.getStatus()
    return jsonify({"state": result.state, "status": result.result_text, "files": json.dumps(result.files)})

# list / get / post files to & from s3

@app.route("/files", methods=['GET','POST'])
@app.route("/files/", methods=['GET','POST'])
@app.route("/files/<file_name>", methods=['GET','POST'])
def files(file_name=""):
    logger.log("Tring to post file_name: " + file_name)
    if request.method == 'POST':
        file = request.files['file']
        learnFile = 'ML_Label_Results.xlsx'
        if file_name == learnFile and file.filename == learnFile:
            save_file = os.path.join(DATA_PATH, file.filename)
            logger.log("Attempting to save {0} to {1}".format(file.filename,save_file))
            file.save(save_file)
            return jsonify({"state": "Accepted", "status": "File {0} was accepted and saved to data path".format(file.filename)})
        else:
            logger.log("Rejected attempt to upload a file")
            return jsonify({"state": "Rejected", "status": "Unauthorized file attempted to be posted: {0} only {1} is allowed".format(file.filename,learnFile)})
    else:
        # Add code.  if app.log, then send CWD/app.log, if user-data.log (and it exists), send /var/log/user-data.log
        acceptable_filenames = ["paloalto.parquet","vmVulnerabilities.parquet","vmtopamapped.parquet","encoded_mapped_data.parquet","final_results.csv","ML_Label_Results.xlsx"]
        confidence = range(2,-1,-1)
        severity = range(10,-1, -1)
        for i in severity:
            for j in confidence:
                acceptable_filenames.append("final_results_sev_{0:02d}_conf_{1}.csv".format(i,str(j)))
        if(file_name == "app.log"):
            app_log = os.path.join(os.getcwd(), file_name)
            if path.isfile(app_log):
                return send_file(app_log)
            else:
                jsonify({"state": "Rejected", "status": "App log was not found at {0}".format(app_log)})
        elif (file_name == "user-data.log"):
            user_log = os.path.join("/var/log", file_name)
            if path.isfile(user_log):
                return send_file(user_log)
            else:
                return jsonify({"state": "Rejected", "status": "User-data log was not found at {0}".format(user_log)})
        elif file_name in acceptable_filenames:
            full_filepath = os.path.join(DATA_PATH,file_name)
            return send_file(full_filepath)
        else:
            return jsonify({"state": "List", "status": "Use /files/[file_name]. Acceptable file names are: {0}".format(",".join(acceptable_filenames))})






################################ERROR VIEWS######################################
@app.errorhandler(400)
def custom400(error):
    response = jsonify({'FAIL': error.description})
    return response


@app.errorhandler(403)
def error403(error):
    response = jsonify({'FAIL': error.description})
    return response


@app.errorhandler(404)
def error404(error):
    response = jsonify({'FAIL': error.description})
    return response


################################MAIN - RUN SETUP######################################
def startup():
    # find out if this is a twisted or builtin run
    parser = optparse.OptionParser(usage="%prog [options]  or type %prog -h (--help)")
    parser.add_option('--twisted', help='Twisted event-driven web server', action="callback", callback=twisted, type="int")
    parser.add_option('--builtin', help='Built-in Flask web development server', action="callback", callback=builtin, type="int")
    (options, args) = parser.parse_args()
    parser.print_help()

if __name__ == "__main__":
    log("Starting")
    if not sys.version_info >= (3, 5):
        log("Note, this solution needs python 3.5 or later. Run using python3 application.py. Exitting.")
    else:
        if("True" in HOST_IN_TWISTED):
            print("Starting Twisted Web Server")
            twisted()
        else:
            print("Starting Builtin Web Server")
            builtin()
