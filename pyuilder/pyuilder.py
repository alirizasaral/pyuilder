from __future__ import print_function
from docker import Client, tls
from io import BytesIO
import platform
import os
import sys
import re
import datetime
import random

class DockerOutputConsoleWriter:

	def __init__(self, delegate=None):
		self.delegate = delegate

	def format(self, line):
		return str(line).replace('\n', '')

	def print(self, line):
		line = self.format(line)
		if len(line.strip()) > 1:
			print(line)

	def process(self, line):
		try:
			stream = eval(line)
			for key, value in stream.iteritems():
				self.print("[" + key + "] " + self.format(value), end="", flush=True)
				if self.delegate != None:
					self.delegate.process(str(value))
		except:
			self.print(line)
			if self.delegate != None:
				self.delegate.process(line)

class FileContentCollector:

	def __init__(self, delegate = None):
		self.delegate = delegate
		self.content = ""

	def process(self, line):
		self.content += "\n"
		self.content += line
		if self.delegate != None:
			self.delegate.process(line)

class FirstLineCapturer:

	def __init__(self, delegate = None):
		self.delegate = delegate
		self.result = None	

	def process(self, line):
		if self.result == None:
			self.result = line
		if self.delegate != None:
			self.delegate.process(line)

class DockerOutpurProcessor:

	def process(self, response, delegate=None):
		for line in response:
			if delegate != None:
				delegate.process(line)

class DockerFileBuilder:

	def __init__(self):
		self.__maintainer = None
		self.__from = None
		self.__runs = []
		self.__envs = []
		self.__data_to_copy = []

	def inherits(self, baseImage):
		self.__from = baseImage
		return self

	def maintainer(self, maintainer):
		self.__maintainer = maintainer
		return self

	def run(self, run):
		self.__runs.append(run)
		return self

	def env(self, name, value):
		self.__envs.append(name + "=" + value)
		return self

	def build(self):
		content = "FROM " + self.__from
		if self.__maintainer:
			content = content + "\nMAINTAINER " + self.__maintainer
		if len(self.__runs) > 0:
			for run in self.__runs:
				content = content + "\nRUN " + run
		if len(self.__envs) > 0:
			for env in self.__envs:
				content = content + "\nENV " + env
		return content

class DockerController:

	WORKSPACE_IMAGE = 'pyuilder/workspace:latest'
	CONTAINER_NAME = "workspace"

	def __init__(self):
		self.modules = []
		self.outputProcessor = DockerOutpurProcessor()
		self.proxy = self.guess_proxy()

	def guess_proxy(self):
		if "http_proxy" in os.environ.keys():
			print("Proxy detected: " + os.environ["http_proxy"])
			return (os.environ["http_proxy"], os.environ["https_proxy"], os.environ["no_proxy"])
		else:
			return None

	def add_module(self, module):
		print("registering module " + str(module))
		self.modules.append(module)

	def set_proxy(self, http_proxy, https_proxy, no_proxy):
		self.proxy = (http_proxy, https_proxy, no_proxy)

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
		if self.proxy:
			dockerfile.env("http_proxy", self.proxy[0])
			dockerfile.env("https_proxy", self.proxy[1])
			dockerfile.env("no_proxy", self.proxy[2])
			dockerfile.run("echo \"Acquire::http::Proxy \\\"" + self.proxy[0] + "\\\";\" >> /etc/apt/apt.conf")
		dockerfile.run("apt-get update")
		
		for module in self.modules:
			if "get_load_statements" in dir(module):
				for statement in module.get_load_statements():
					dockerfile.run(statement)
		f = BytesIO(dockerfile.build().encode('utf-8'))
		self.outputProcessor.process(self.cli.build(
			fileobj=f, rm=True, tag=workspaceImage, buildargs=self.get_build_args()
		), DockerOutputConsoleWriter())

	def get_build_args(self):
		if self.proxy:
			return {"http_proxy": self.proxy[0], "https_proxy": self.proxy[1], "no_proxy": self.proxy[2]}
		else:
			return {}

	def remove_latest_container(self):
		containers = self.cli.containers(all=True, filters={"name": self.CONTAINER_NAME})
		for container in containers:
			self.cli.stop(container['Id'])
			self.cli.remove_container(container['Id'])


	def start_container(self, workspaceImage):
		volumes_for_modules, binds_for_modules = self.get_volumes_for_modules()
		self.remove_latest_container()
		print("starting with volumes " + str(binds_for_modules))
		if len(volumes_for_modules) > 0:
			container = self.cli.create_container(image=workspaceImage, command='bash', name=self.CONTAINER_NAME, detach=True, stdin_open=True, tty=True, volumes=volumes_for_modules, host_config=self.cli.create_host_config(binds=binds_for_modules))
		else:
			container = self.cli.create_container(image=workspaceImage, command='bash', name=self.CONTAINER_NAME, detach=True, stdin_open=True, tty=True)
		self.container_id = container.get('Id')
		response = self.cli.start(container=self.container_id)

	def get_volumes_for_modules(self):
		volumes = []
		binds = []
		for module in self.modules:
			if "get_volumes" in dir(module) and module.get_volumes():
				for volume in module.get_volumes():
					volumes.append(volume.split(':')[1])
					binds.append(volume)
		return volumes, binds

	def execute(self, command, outputProcessor=None):
		print(command)
		cmd = self.cli.exec_create(container=self.container_id, stdout=True, stderr=True, cmd=command)
		self.outputProcessor.process(self.cli.exec_start(exec_id=cmd.get('Id'), stream=True), DockerOutputConsoleWriter(outputProcessor))
		response = self.cli.exec_inspect(cmd.get('Id'))
		if not (response['ExitCode'] == 0):
			print("Command returned exit-code " + str(response['ExitCode']))
			print("Interrupting...")
			sys.exit(1)

	def read_file(self, filename):
		fileContentCollector = FileContentCollector()
		self.execute("cat " + filename, fileContentCollector)
		return fileContentCollector.content

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

	def parent(self):
		path = self.path
		if path.endswith("/"):
			path = subpath[-1]
		path = "/".join(path.split("/")[0:-1])
		return Folder(path)

	def subfolder(self, subpath):
		if subpath.startswith("/"):
			subpath = subpath[1:]
		return Folder(self.pathname() + "/" + subpath)

	def __repr__(self):
		return "Folder(" + self.path + ")"

@injectDockerController
class WorkspaceManager:

	def __init__(self, **kwargs):
		self.mapped_paths = kwargs.get("mapped_paths")

	def get_volumes(self):
		return self.mapped_paths

	def createTmpFolder(self):
		now = datetime.datetime.utcnow()
		path = "/tmp/" + now.strftime("%d%m%Y%H%M%S") + str(random.randint(10, 99))
		self.ctl.execute("mkdir -p " + path)
		return Folder(path)

	def get(self, folder):
		return Folder(folder)

@injectDockerController
class CloudFoundryDeployment:

	def __init__(self, endpoint, username, password, organization, application):
		self.endpoint = endpoint
		self.username = username
		self.password = password
		self.build_pack = None
		self.hostname = None
		self.organization = organization
		self.application = application
		self.env = None

	def with_app_name(self, name):
		self.appName = name
		return self

	def to_space(self, name):
		self.space = name
		return self

	def with_hostname(self, hostname):
		self.hostname = hostname
		return self

	def with_build_pack(self, pack):
		self.build_pack = pack
		return self

	def with_env(self, **kwargs):
		self.env = kwargs
		return self

	def set_app_environment_variables(self):
		for key, value in self.env.iteritems():
			self.set_app_environment_variable(key, value)		

	def set_app_environment_variable(self, key, value):
		self.ctl.execute('cf set-env {} {} "{}"'.format(self.appName, key, value))

	def restage(self):
		self.ctl.execute('cf restage {}'.format(self.appName))		

	def execute(self):
		self.ctl.execute("cf login -a {} -u {} -p {} -o {} -s {} --skip-ssl-validation".format(self.endpoint, self.username, self.password, self.organization, self.space))
		cmd = "cf push {} -p {}".format(self.appName, self.application.pathname())
		if self.build_pack:
			cmd += " -b {}".format(self.build_pack)
		if self.hostname:
			cmd += " --hostname {}".format(self.hostname)
		if self.env:
			self.set_app_environment_variables()
		self.ctl.execute(cmd)



@injectDockerController
class CloudFoundry:

	def __init__(self, **kwargs):
		self.endpoint = kwargs.get("endpoint")
		self.username = kwargs.get("username")
		self.password = kwargs.get("password")
		self.organization = kwargs.get("organization")

	def new_deployment(self, application):
		return CloudFoundryDeployment(self.endpoint, self.username, self.password, self.organization, application)

	def get_load_statements(self):
		return ["apt-get -y install wget",
				"wget -O /tmp/cf-cli.deb https://cli.run.pivotal.io/stable?release=debian64\&version=6.22.1",
				"dpkg -i /tmp/cf-cli.deb  && apt-get install -f"]

class MVNPackage:

	def __init__(self):
		self.artifact = None
		self.version = None
		self.group = None
		self.type = None
		self.binary = None
		self.files = []

	def __repr__(self):
		return self.name + " " + self.version

class MVNOutputProcessor:

	def __init__(self):
		self.package = None

	def process(self, line):
		if self.package == None:
			self.capture_package(line)
		else:
			self.enhance_package_data(line)

	def enhance_package_data(self, line):
		m = re.search('Building ([/.*\S.*/]+): ([/.*\S.*/]+)', line)
		if m != None and len(m.groups()) == 2:
			self.package.type = m.group(1)
			self.package.binary = Folder(m.group(2))

	def capture_package(self, line):
		package = None
		m = re.search('Building ([/.*\S.*/]+) ([/.*\S.*/]+)', line)
		if m != None and len(m.groups()) == 2:
			package = MVNPackage()
		self.package = package

@injectDockerController
class MVN:

	def __init__(self, **kwargs):
		self.repository_path = kwargs.get("repository_path")
		self.proxy_set = False

	def get_volumes(self):
		if self.repository_path:
			return [self.repository_path + ":/root/.m2/repository/"]
		else:
			return []

	def get_proxy_configuration(self):
		host = self.ctl.proxy[0].split("://")[1].split(":")[0]
		protocol = self.ctl.proxy[0].split("://")[0]
		port = self.ctl.proxy[0].split(":")[-1]
		no_proxy = self.ctl.proxy[2].replace(",", "|")
		return host, protocol, port, no_proxy

	def create_proxy_settings(self):
		host, protocol, port, no_proxy = self.get_proxy_configuration()
		print ("host is " + host)
		settings = """<settings xmlns=\"http://maven.apache.org/SETTINGS/1.0.0"
					  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
					  xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
					                      https://maven.apache.org/xsd/settings-1.0.0.xsd">
					  <proxies>
					   <proxy>
					      <id>my-proxy</id>
					      <active>true</active>
					      <protocol>{}</protocol>
					      <host>{}</host>
					      <port>{}</port>
					      <nonProxyHosts>localhost</nonProxyHosts>
					    </proxy>
					  </proxies>
					</settings>""".format(protocol, host, port, no_proxy).replace("\n", "").replace("\t", "").replace("\"", "\\\"")
		return settings

	def check_and_set_proxy(self):
		settings = self.create_proxy_settings()
		if self.ctl.proxy and not self.proxy_set:
			self.ctl.execute("bash -c \"echo '" + settings + "' > ~/.m2/settings.xml\"")
			self.proxy_set = True

	def get_load_statements(self):
		load_statements = ["apt-get -y install openjdk-8-jdk",
				"apt-get -y install maven"]
		return load_statements

	def update_version(self, workDir, version):
		self.check_and_set_proxy()
		self.ctl.execute("mvn -f {} versions:set -DnewVersion={}".format(workDir.pathname(), version))

	def parse_pom_properties(self, pomFile):
		content = self.ctl.read_file(pomFile.pathname())
		props = {}
		for line in content.split('\n'):
			temp = line.strip().split('=')
			if len(temp) == 2:
				props[temp[0]] = temp[1]
		return props

	def package(self, workDir):
		self.check_and_set_proxy()
		packageCapturer = MVNOutputProcessor()
		self.ctl.execute("mvn -f {} package".format(workDir.pathname()), packageCapturer)
		pomProperties = self.parse_pom_properties(packageCapturer.package.binary.parent().subfolder("maven-archiver/pom.properties"))
		packageCapturer.package.artifact = pomProperties['artifactId']
		packageCapturer.package.group = pomProperties['groupId']
		packageCapturer.package.version = pomProperties['version']
		return packageCapturer.package

	def __str__(self):
		return "Maven"

@injectDockerController
class Nexus:

	def __init__(self, **kwargs):
		self.endpoint = kwargs.get("endpoint")
		self.username = kwargs.get("username")
		self.password = kwargs.get("password")

	def get_load_statements(self):
		return ["apt-get -y install curl"]

	def upload(self, package, repository):
		cmd = "curl -v -F r={} -F hasPom=false -F e={} -F g={} -F a={} -F v={} -F p={} -F file=@{}".format(repository, package.type, package.group, package.artifact, package.version, package.type, package.binary.pathname())
		#for file in package.files:
		#	cmd += " -F file=@{}".format(file.pathname())
		cmd += " -u {}:{} {}/service/local/artifact/maven/content".format(self.username, self.password, self.endpoint)
		self.ctl.execute(cmd)

	def download(self, repository, group, artifact, version, destFile):
		self.ctl.execute("curl -o {} {}/service/local/artifact/maven/content?g={}&a={}&v={}&r={}".format(destFile.pathname(), self.endpoint, group, artifact, version, repository))
		return destFile


@injectDockerController
class NPM:
	def __init__(self):
		pass

	def get_load_statements(self):
		return ["apt-get -y install npm"]

	def update_version(self, workDir, version):
		self.ctl.execute("bash -c 'cd {}; npm version {}'".format(workDir.pathname(), version))

	def calculate_credentials(self, username, password):
		resultCapturer = FirstLineCapturer()
		self.ctl.execute("bash -c 'echo -n \'{}:{}\' | openssl base64'".format(username, password), resultCapturer)
		return resultCapturer.result

	def configure(self, username, password, email):
		credentials = self.calculate_credentials(username, password)
		self.ctl.execute("npm config set email {}".format(email))
		self.ctl.execute("npm config set _auth {}".format(credentials))

	def publish_internal(self, appFolder, endpoint):
		self.ctl.execute("bash -c 'cd {}; npm publish --registry {}'".format(appFolder, endpoint))

	def publish(self, workDir, **kwargs):
		endpoint = kwargs.get("endpoint")
		username = kwargs.get("username")
		password = kwargs.get("password")
		email = kwargs.get("email")
		self.configure(username, password, email)
		self.publish_internal(workDir.pathname(), endpoint)


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
		return folder

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

