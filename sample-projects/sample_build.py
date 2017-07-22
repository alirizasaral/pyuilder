import sys
import os
import logging

sys.path.append('..')

from pyuilder.dockerlayer import Container

logger = logging.getLogger("pyuilder")
logger.setLevel(logging.INFO)

def create_mvn_container(work_dir):
	return Container("alirizasaral/maven-with-proxy:3", volumes={'/tmp/m2': {'bind': '/root/.m2', 'mode': 'rw'},
		                                                       work_dir: {'bind': '/workspace', 'mode': 'rw'}}, 
		                                              working_dir='/workspace', stdout=True, stderr=True)

def create_findbugs_container(work_dir):
	return Container("recruitsumai/findbugs:latest", volumes={work_dir: {'bind': '/workdir', 'mode': 'rw'}})
	
if __name__ == '__main__': 
	work_dir = os.path.dirname(os.path.realpath(__file__)) + "/employee-controller"
	
	with create_mvn_container(work_dir) as container:
		container.mvn("clean package")
		container.mkdir("./target/report")

