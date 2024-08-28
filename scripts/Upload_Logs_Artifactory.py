#!/usr/bin/env python3
import datetime
import os
import re
from os import walk
import requests
import sys
import uuid
import tempfile
import zipfile
import shutil
import tempfile
import tarfile



def excludeFunction(filename):
    x=os.path.basename(filename)
    if x.startswith('Apz') or x.startswith('x86_64'):
        return True
    else:
        return False



def dataPreparation(path):

    listFiles=os.listdir(path)
    # get a temporary directory
    tmpDest = tempfile.mkdtemp()
    dest = os.path.join(tmpDest, 'cop')
    os.mkdir(dest)

    for file in listFiles:
        if file.endswith('.zip'):
            filePath=path + '/' + file
            zipFile = zipfile.ZipFile(filePath)
            for names in zipFile.namelist():
                zipFile.extract(names,dest)
            zipFile.close()

    now = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    filetgz = 'clh' + '_' + now + '.tar.gz'
    #outTarFile=os.path.join(tmpDest, 'copFile.tar.gz')
    outTarFile=os.path.join(tmpDest, filetgz)
    
    with tarfile.open(outTarFile, "w:gz") as tar:
        tar.add(dest, arcname='apzmw', exclude=excludeFunction)
    tar.close()

    return tmpDest,outTarFile
                                                                                        


dirname = sys.argv[1] + "/"

tmpdir,k = dataPreparation(dirname)
print (tmpdir,k)
dest=os.path.join(tmpdir, 'cop')
shutil.rmtree(dest)
#sys.exit(1)

print("Started upload process of CNF Log files to Artifactory.")
# Calculating the current month as a 2-digit Integer
date_now = datetime.datetime.now()
month = date_now.strftime("%m")
year = date_now.strftime("%Y")

if len(sys.argv) <= 2:
    print("$ {0} <log_path> <status> <testcase_name> (<uuid>)".format(sys.arg[0]))
    sys.exit(1)
# Later change uuid to be extracted from spinnaker
#logs_path = sys.argv[1] + "/"# "/proj/cloud_cicd/RAVNF/logs/cnf_logs/"
logs_path = tmpdir + "/"# "/proj/cloud_cicd/RAVNF/logs/cnf_logs/"

status = sys.argv[2]
testcase_name = sys.argv[3]

#if len(sys.argv) > 4:
#    uuid = sys.argv[4] + "/"  # "a5151ed4-3247-4532-851d-f26ae46b32fe/"
#else:
uuid = "{0}".format(uuid.uuid4())

#stesso come testcase_name
pipeline = sys.argv[3]
number  = sys.argv[4]
startime = sys.argv[5]
endtime = sys.argv[6]




if status not in [ "SUCCEEDED", "FAILED" ]:
    print("Status=SUCCEEDED/FAILED")
    sys.exit(1)

arm_repository = "https://arm.sero.gic.ericsson.se/artifactory/proj-lexicon-generic-local/"
arm_upload_path = "mscaxe_pipeline_analyzer/data/" + year + "/" + month + "/" + uuid + "/"
#arm_upload_path = "datalake/input_data/mscaxe/runs/" + status.lower() + "/" + year + "/" + month + "/" + uuid + "/"


#credentials
with open(".sdnrad.creds") as f:
    line = f.readlines()
user = line[0].split(' ')[3]
password = line[0].split(' ')[5].replace('\n','')


# Retrieving all stored Logs from the directory
logs = []
for (dirpath, dirnames, filenames) in walk(logs_path):
    logs.extend(filenames)
    break
if len(logs) > 0:
    print("Log files successfully collected in directory {0}".format(uuid))
else:
    raise RuntimeError("No files found for UUID {0}".format(uuid))


#
# Create a file called artifact.info in which the filenames are stored
#
#try:
#    fileHandler = open(logs_path + "artifact.info", "w")
#    for log in logs:
#        fileHandler.write(log + "\n")
#    fileHandler.write("artifact.info\n")
#    fileHandler.write(status + "\n")
#    fileHandler.write(testcase_name)
#    fileHandler.close()
#    print("Artifact.info file created in directory {0}".format(logs_path))
#    logs.extend(["artifact.info"])
#except FileNotFoundError:
#    raise RuntimeError("Artifact.info file could not be created.")
#


# Create a file called run_info.yaml in which the filenames are stored
try:
    fileHandler = open(logs_path + "run_info.yaml", "w")

    fileHandler.write('pipeline: ' + pipeline + " " + number + "\n")
    fileHandler.write('status: '+ status + "\n")
    fileHandler.write("start_timestamp: '" + startime + "'\n")
    fileHandler.write("end_timestamp: '" + endtime  + "'\n")
    fileHandler.write('artifacts: ' + "\n")
    for log in logs:
        fileHandler.write('- '+ log + "\n")
    fileHandler.write('run_id: ' + uuid + "\n")
    fileHandler.close()
    print("run_info.yaml file created in directory {0}".format(logs_path))
    logs.extend(["run_info.yaml"])
except FileNotFoundError:
    raise RuntimeError("run_info.yaml file could not be created.")



# Uploading every file of the directory to artifactory
print("Uploading to {0}".format(arm_repository + arm_upload_path))
for file in logs:
    r = requests.put(arm_repository + arm_upload_path + file,
                     data=open(logs_path + file, 'rb'),
                     auth=(user, password))
    if r.status_code == 201:
        print("{0} successfully uploaded to artifactory.".format(file))
    else:
        print("Something went wrong when uploading file {0}. Request gave response code {1}.".format(file, r.status_code))
        raise RuntimeError("Artifactory Upload failed.")


shutil.rmtree(logs_path)

# Remove the artifact.info from the log directory
# Files in directory might be needed for other processing
#if os.path.exists(logs_path + "artifact.info"):
#    os.remove(logs_path + "artifact.info")
#    print("artifact.info successfully removed from logs directory.")
#else:
#    print("artifact.info could not be deleted, as path {0}/artifact.info could not be found.".format(logs_path))





