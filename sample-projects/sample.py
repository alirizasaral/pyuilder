import sys
import os
import traceback
from optparse import OptionParser
sys.path.append('..')

from pyuilder.nexus import Nexus
from pyuilder.maven import Maven
from pyuilder.dockerlayer import DockerController
from pyuilder.utils import *


def usage():
    print "Usage: python sample.py <application-name> <version>"

def check_usage():
    if len (sys.argv) != 3:
        print "Commandline arguments missing, provided only " + str(len (sys.argv))
        usage()
        exit()

def print_prominent(msg):
    print ""
    print "-" * 128
    print "- " + msg + " " + ("-" * (128 - len(msg) - 3))
    print "-" * 128
    print ""

def setup():
    controller = DockerController()
    nexus = Nexus(client= controller.cli, endpoint='http://127.0.0.1/nexus', username='admin', password='admin123')
    mvn = Maven(client= controller.cli, skip_tests=False)
    return mvn, nexus

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-f", "--folder", dest="application_folder",
                  help="Application Folder", metavar="FILE")
    parser.add_option("-v", "--version", type="string", dest="application_version",
                  help="Application Version")
    (options, args) = parser.parse_args()

    print options.application_folder

    try:
    	mvn, nexus = setup()

        # -------------- compile & unit-test ---------------- 
        mvn.update_version(options.application_folder, options.application_version)
        application_package = mvn.package(options.application_folder)

        # -------------- publish ----------------------------
        artifact = nexus.upload(repository='snapshots', package=application_package)
        print artifact

        # -------------- deploy to stage --------------------
        

        # -------------- smoke-test -------------------------

        # -------------- notify Release Candidate Ready --------------------------

        print_prominent("build completed successfully")
    except:
        e = sys.exc_info()[0]
        print("Build failed. Interrupting: ")
        traceback.print_exc()
        exit(1)



