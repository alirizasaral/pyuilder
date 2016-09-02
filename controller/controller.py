from docker import Client
from io import BytesIO

def print_docker_reponse(response):
	for line in response:
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
		self.cli = Client(base_url='unix://var/run/docker.sock')
		self.build_container_image(DockerController.WORKSPACE_IMAGE)
		self.start_container(DockerController.WORKSPACE_IMAGE)

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
		container = self.cli.create_container(image=workspaceImage, command='bash', name="workspace", detach=True, stdin_open=True, tty=True)
		self.container_id = container.get('Id')
		response = self.cli.start(container=self.container_id)

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

	def __init__(self):
		pass

	def get_load_statements(self):
		#self.ctl.execute("add-apt-repository -y ppa:webupd8team/java")
		#self.ctl.execute("apt-get update")
		#self.ctl.execute("echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections")
		#self.ctl.execute("echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections")
		#self.ctl.execute("apt-get -y install oracle-java7-installer ")
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

	def to(self, folder):
		self.ctl.execute("git clone " + self.url + " " + folder.pathname())

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

