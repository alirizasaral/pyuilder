import docker
import platform
import os
from utils import *
import sys
from docker.errors import ImageNotFound

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
        lines = ["FROM {}".format(self.__from)]
        if self.__maintainer:
            lines.append("MAINTAINER {}".format(self.__maintainer))
        if len(self.__envs) > 0:
            lines.extend(["ENV {}".format(env) for env in self.__envs])
        if len(self.__runs) > 0:
            lines.extend(["RUN {}".format(cmd) for cmd in self.__runs])
        return "\n".join(lines)

WORKING_DIR = "/target"

class Volume(object):

    def __init__(self, host_folder, alias):
        self.alias = alias
        self.host_folder = host_folder

    def as_dict(self):
        return {self.host_folder: {'bind': self.alias, 'mode': 'rw'}}

    def get_binding(self):
        return {'bind': self.alias, 'mode': 'rw'}

class Volumes(object):

    def __init__(self):
        self.volumes = []

    def add(self, host_folder, alias):
        self.volumes.append(Volume(host_folder, alias))
        return self

    def as_dict(self):
        return {volume.host_folder : volume.get_binding() for volume in self.volumes}

class ContainerOperationOnFolder(object):

    def __init__(self, image, cmd, **container_start_arguments):
        self.image = image
        self.cmd = [cmd] if isinstance(cmd, basestring) else cmd
        self.container_start_arguments = container_start_arguments

    def get_default_container_start_arguments(self):
        return merge_dicts(self.container_start_arguments, {'detach' : False, 'stdin_open' : True, 'tty' :True})

    def calculate_volumes(self, volumes_list):
        volumes = Volumes()
        for volume in volumes_list:
            split = volume.split(':')
            volumes.add(split[0], split[1])
        return {'volumes' : volumes.as_dict()}

    def apply(self, docker_client, volumes, **cmd_arguments):
        container_start_arguments = merge_dicts(self.get_default_container_start_arguments(), self.calculate_volumes(volumes))
        container = None
        try:
            container = docker_client.containers.create(image=self.image, command='bash', **container_start_arguments)
        except ImageNotFound:
            docker_client.images.pull(self.image)
            container = docker_client.containers.create(image=self.image, command='bash', **container_start_arguments)
        container.start()
        output = []
        executed_commands = []
        for cmd in self.cmd:
            cmd_to_execute = cmd.format(**cmd_arguments)
            executed_commands.append(cmd)
            print cmd_to_execute
            output.append(container.exec_run(cmd_to_execute))
        container.stop()
        return '\n'.join(output), executed_commands

class DockerController:

    def __init__(self):
        self.cli = self.create_client()


    def create_client(self):
        if platform.system() == 'Windows':
            certs = os.environ['DOCKER_CERT_PATH']
            tls_config = docker.tls.TLSConfig(  client_cert=(certs + '\\cert.pem', certs + '\\key.pem'), verify=certs + '\\ca.pem')
            return docker.client.DockerClient(base_url=os.environ['DOCKER_HOST'], version="auto", tls=tls_config)
        else:
            return docker.client.DockerClient(base_url='unix://var/run/docker.sock', version="auto")
