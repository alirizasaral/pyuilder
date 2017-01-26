import unittest
from pyuilder.maven import Maven
from pyuilder.nexus import Nexus
from pyuilder.cloud_foundry import CloudFoundry
from pyuilder.utils import *
from pyuilder.dockerlayer import DockerController, DockerFileBuilder, Volume, Volumes, ContainerOperationOnFolder

class DockerFileBuilderTest(unittest.TestCase):

    def test_build_dockerfile(self):
        builder = DockerFileBuilder()
        builder.inherits("ubuntu") \
               .maintainer("Ali Riza Saral <aliriza.saral@gmail.com>") \
               .env("http_proxy", "http://localproxy:8080") \
               .env("https_proxy", "http://localproxy:8080") \
               .run("apt-get update")
        actual = builder.build()
        expected = ("FROM ubuntu\n"
                    "MAINTAINER Ali Riza Saral <aliriza.saral@gmail.com>\n"
                    "ENV http_proxy=http://localproxy:8080\n"
                    "ENV https_proxy=http://localproxy:8080\n"
                    "RUN apt-get update")
        self.assertEqual(expected, actual)

class VolumesTest(unittest.TestCase):

    def test_volume_as_dict(self):
        self.assertEqual({'/src': {'bind': '/home/user1', 'mode': 'rw'}}, Volume("/src", '/home/user1').as_dict())
    
    def test_volumes_as_dict(self):
        self.assertEqual({'/src': {'bind': '/home/user1', 'mode': 'rw'},
                          '/tmp': {'bind': '/tmp/pyuilder', 'mode': 'rw'}
                         }, Volumes().add("/src", '/home/user1')
                                     .add("/tmp", "/tmp/pyuilder").as_dict())

    def test_volumes_as_dict_overriding(self):
        self.assertEqual({'/src': {'bind': '/home/user2', 'mode': 'rw'},
                          '/tmp': {'bind': '/tmp/pyuilder', 'mode': 'rw'}
                         }, Volumes().add("/src", '/home/user1')
                                     .add("/tmp", "/tmp/pyuilder")
                                     .add("/src", '/home/user2').as_dict())
"""
class UtilsTest(unittest.TestCase):

    def test_get_proxy_parameters_from_env(self):
        self.assertEqual({'PROXY_HOST': 'smtpproxy2.allianz-ceema.com',
                          'PROXY_PORT': '80',
                          'PROXY_PROTOCOL': "http",
                          'NO_PROXY': '127.0.0.1,localhost'}, get_proxy_parameters_from_env())

class ContainersTest(unittest.TestCase):

    def test_run_multiple_commands(self):
      dockerClient = DockerController().cli
      dockerClient.containers.run('ubuntu', ['echo', 'hello2'], detach=False, stdin_open=True, tty=True)


class MiscTest(unittest.TestCase):

    def test_container_with_multiple_operations(self):
        controller = DockerController()
        #op = ContainerOperationOnFolder('maven:3.3.9-jdk-8-alpine', ['ls -al', 'echo {message}'])
        op = ContainerOperationOnFolder('alirizasaral/maven-with-proxy:3', ['mvn --version', 'echo {message}'])
        output, cmd = op.apply(controller.cli, ['/c/Users/pyuilder/m2:/tmp'], message="helloworld")
        print output
        self.assertTrue(True)
"""
if __name__ == '__main__':
    unittest.main()