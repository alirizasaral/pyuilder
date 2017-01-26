from dockerlayer import ContainerOperationOnFolder
import utils
import re
import configparser

IMAGE = 'alirizasaral/maven-with-proxy:3'

class Maven(object):

    def __init__(self, client, cache=None, skip_tests=False, proxy=None):
        self.client = client
        self.cache = cache
        package_cmd = 'mvn --batch-mode -f {path} package'
        if skip_tests: package_cmd += ' -Dmaven.test.skip=true'
        self.package_operation = ContainerOperationOnFolder(IMAGE, package_cmd, environment=proxy if proxy else {})
        self.version_update_operation = ContainerOperationOnFolder(IMAGE, 'mvn --batch-mode -f {path} versions:set -DnewVersion={version}', environment=proxy if proxy else {})

    def get_volumes(self, workdir):
        workdir_alias = '/src'
        volumes = ['{}:{}'.format(workdir, workdir_alias)]
        if self.cache:
            volumes.append('{}:/root/.m2'.format(self.cache))
        return volumes, workdir_alias

    def update_version(self, workdir, version):
        volumes, workdir_alias = self.get_volumes(workdir)
        output, cmd = self.version_update_operation.apply(self.client, volumes, path=workdir_alias, version=version)
        print cmd
        print output
        return output

    def convert_containerpath_to_hostpath(self, path_on_container, workdir, workdir_alias):
        return path_on_container.replace(workdir_alias, workdir)

    def package(self, workdir):
        volumes, workdir_alias = self.get_volumes(workdir)
        output, cmd = self.package_operation.apply(self.client, volumes, path=workdir_alias)
        print cmd
        print output
        package = self.extract_data_from_output(output)
        package['binary_path'] = self.convert_containerpath_to_hostpath(package['binary_path'], workdir, workdir_alias)
        pom = utils.parse_properties(utils.platform_specific_path('{}/target/maven-archiver/pom.properties'.format(workdir)))
        return utils.merge_dicts(package, pom)

    def extract_data_from_output(self, output):
        package = None
        first = True
        for line in output.split('\n'):
            m = re.search('Building ([/.*\S.*/]+) ([/.*\S.*/]+)', line)
            if m != None and len(m.groups()) == 2:
                if first:
                    first = False
                else:
                    package = {}
                    package['type'] = m.group(1).replace(':', '')
                    package['binary_path'] = m.group(2)
        if not package:
            raise ValueError('Package could not be extracted from Maven-Output: \n' + output)
        return package

    def __str__(self):
        return "Maven"
