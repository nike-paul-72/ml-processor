# winning-team-gitops

This project was created by a team from CIS working under the CIS Cy Ops Challenge. 

The goal was to increase the prioritization of vulnerability remediation by enriching the vulnerability data with external data sources (Palo Alto zone information), and then, using manually created training data, use ML to add a confidence score that indicates which vulnerabilities are likely properly scored. 

Note, this code includes a sample .env.  Modify for your target environment.  Note, you may want to run in a virtualenv if your system supports it [virtual env how-to](https://akshayranganath.github.io/How-to-create-dev-environment-for-python/). 

Setup:

`pip3 install -r requirements.txt`   (Will install all required python packages). 

There are 3 ways to run the code.

`python3 application.py`  (runs the web front end.  Can trigger each of the tasks via web interface, if they are runnable). All tasks are run on background threads, will avoid running same task concurrently.

`python3 cli-predictor.py`   (runs ALL of the tasks, in order, on background threads, if needed.  Can force to run commands even if the data already exists and is current.  This is used as a scheduled job) 

`python3 just_run_it.py`   (this runs a single task, interactively.  See -h for help, -c <command to run> to run a command, -f to force the command to run even if files are current).  Primary used for testing / debugging.

`python3 just_run_it.py -h`  (this runs a single task, interactively.  See -h for help, -c <command to run> to run a command, -f to force the command to run even if files are current).  Primary used for testing / debugging.

## DEPLOYMENT:

1. Create a role in AWS IAM that allows EC2 access to an S3 bucket [EC2 to S3 Bucket Role](https://aws.amazon.com/premiumsupport/knowledge-center/s3-instance-access-bucket/) Record the Role Name.
2. Create an S3 bucket in the same region where the EC2 instance will be deployed. Record the Bucket Name.
3. Create a data folder and a code folder in that S3 bucket.
4. Get / generate SSL/TLS key (named server_key.pem) and certificate (named server_cert.pem) place in a "servercerts" sub-folder with the code base.  
5. Zip the code based and place in the code folder on the s3 bucket named (mlai.zip)
6. Run the Cloud Formation script (*.yaml) to deploy the desired solution

**us-west-2.ec2.run-cli-predictor-v1.yaml** - Builds an EC2 instance and then runs the full task cycle.  Once that completes, use Cloud Formation to delete the stack.  We recommend using an C4.8xLarge for this. Note, this script only allows SSH access (to review logs, etc).

**us-west-2.ec2.run-flask-v1.yaml** - Builds an EC2 instance, sets up the web services, grants SSL/TLS access. It provides ready download of the emitted files and the option to selectively run one or more tasks.  Note, for long running hosts, we recommend a low end machine.  If you anticipate running the tasks frequently, use a large host. 


### NOTE on .ENV File

This file exists in the git repo.  That said, your local copy will be ignored for git check in.  Additionally, the server cloudformation scripts automatically generate one for their environment. For most development purposes, the only changes needed is the path to store / read data files ('data_path').  Note, this will accept a relative path (e.g. ./data)

`data_path = /data/s3/cis-ops-challenge/data` - This is the path to write / read the data files.

`host_in_twisted = False` - Use the Twisted multithreaded WSGI web server. For development leave false to use the standard single threaded python web host. 

`builtin_port = 5000` - The port to run on when running in the builtin server.

`twisted_port = 8080` - The port to run on when running using the twisted web server.

`twisted_ip = 127.0.0.1` - The IP address for twisted to listen on.  In production, we filter to just local host requests as we use NGINX to accept requests on port 80 (redirected to 443) and for TLS termination (on port 443) 

`show_bar = True` - Not in use.
