from docker import Client, tls
from io import BytesIO
import platform
import os

def print_docker_reponse(response):
	for line in response:
		try:
			stream = eval(line)
			for key, value in stream.iteritems():
				print "[" + key + "] " + str(value)
		except:
			print line

class DockerFileBuilder:

	def __init__(self):
		self.__maintainer = None
		self.__from = None
		self.__runs = []

	def inherits(self, baseImage):
		self.__from = baseImage
		return self

	def maintainer(self, maintainer):
		self.__maintainer = maintainer
		return self

	def run(self, run):
		self.__runs.append(run)
		return self

	def build(self):
		content = "FROM " + self.__from
		if self.__maintainer:
			content = content + "\nMAINTAINER " + self.__maintainer
		if len(self.__runs)>0:
			for run in self.__runs:
				content = content + "\nRUN " + run
		return content

class DockerController:

	WORKSPACE_IMAGE = 'pyuilder/workspace:latest'

	def __init__(self):
		self.modules = []

	def add_module(self, module):
		print "registering module " + str(module)
		self.modules.append(module)

	def start(self):
		self.cli = self.create_client()
		self.build_container_image(DockerController.WORKSPACE_IMAGE)
		self.start_container(DockerController.WORKSPACE_IMAGE)

	def create_client(self):
		if platform.system() == 'Windows':
			certs = os.environ['DOCKER_CERT_PATH']
			tls_config = tls.TLSConfig(  client_cert=(certs + '\\cert.pem', certs + '\\key.pem'), verify=certs + '\\ca.pem')
			return Client(base_url=os.environ['DOCKER_HOST'], version="auto", tls=tls_config)
		else:
			return Client(base_url='unix://var/run/docker.sock', version="auto")

	def build_container_image(self, workspaceImage):
		dockerfile = DockerFileBuilder().inherits("ubuntu").maintainer("Ali Riza Saral <aliriza.saral@gmail.com>")		
		dockerfile.run("apt-get update")
		
		for module in self.modules:
			for statement in module.get_load_statements():
				dockerfile.run(statement)
		
		f = BytesIO(dockerfile.build().encode('utf-8'))
		print_docker_reponse(self.cli.build(
			fileobj=f, rm=True, tag=workspaceImage
		))

	def start_container(self, workspaceImage):
		volumes_for_modules, binds_for_modules = self.get_volumes_for_modules()
		print "starting with volumes " + str(volumes_for_modules)
		if len(volumes_for_modules) > 0:
			container = self.cli.create_container(image=workspaceImage, command='bash', name="workspace", detach=True, stdin_open=True, tty=True, volumes=volumes_for_modules, host_config=self.cli.create_host_config(binds=binds_for_modules))
		else:
			container = self.cli.create_container(image=workspaceImage, command='bash', name="workspace", detach=True, stdin_open=True, tty=True)
		self.container_id = container.get('Id')
		response = self.cli.start(container=self.container_id)

	def get_volumes_for_modules(self):
		volumes = []
		binds = []
		for module in self.modules:
			if "get_volumes" in dir(module):
				for volume in module.get_volumes():
					volumes.append(volume.split(':')[1])
					binds.append(volume)
		return volumes, binds

	def execute(self, command):
		print(command)
		cmd = self.cli.exec_create(container=self.container_id, stdout=True, stderr=True, cmd=command)
		print_docker_reponse(self.cli.exec_start(exec_id=cmd.get('Id'), stream=True))

	def stop(self):
		self.cli.stop(self.container_id)
		self.cli.remove_container(self.container_id)

ctl = DockerController()



def injectDockerController(clazz):
	oldInit = clazz.__init__
	def init(self, *args, **kwargs):
		oldInit(self, *args, **kwargs)
		self.__dict__['ctl'] = ctl
		ctl.add_module(self)
	clazz.__init__ = init
	return clazz

class Folder:

	def __init__(self, path):
		self.path = path

	def pathname(self):
		return self.path

	def subfolder(self, subpath):
		if subpath.startswith("/"):
			subpath = subpath[1:]
		return Folder(self.pathname() + "/" + subpath)

class WorkspaceManager:

	def createNew(self):
		return Folder("/tmp")


@injectDockerController
class MVN:

	def __init__(self, **kwargs):
		self.repository_path = kwargs.get("repository_path")

	def get_volumes(self):
		if self.repository_path:
			return [self.repository_path + ":/root/.m2/repository/"]
		else:
			return []

	def get_load_statements(self):
		return ["apt-get -y install openjdk-8-jdk",
				"apt-get -y install maven"]

	def package(self, workDir):
		self.ctl.execute("mvn -f " + workDir.pathname() + " package")
		return ""

	def __str__(self):
		return "Maven"

@injectDockerController
class GitCloneJob:

	def __init__(self, url):
		self.url = url
		self.options = {}

	def configure(self, option, value):
		self.options[option] = value
		return self

	def print_options(self):
		if self.options:
			result = "-c"
			for option, value in self.options.iteritems():
				result += " " + option + "=" + value
			return result
		else:
			return ""


	def to(self, folder):
		self.ctl.execute("git " + self.print_options() + " clone " + self.url + " " + folder.pathname())

@injectDockerController
class Git:

	def __init__(self):
		pass

	def get_load_statements(self):
		return ["apt-get -y install git-all"]

	def clone(self, url):
		return GitCloneJob(url)

	def __str__(self):
		return "Git"



"""
try:
	mvn = MVN()
	git = Git()
	ctl.start()
finally:
	pass
	#ctl.stop()
"""

