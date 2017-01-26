from dockerlayer import ContainerOperationOnFolder
import os

class Nexus:

    def __init__(self, client, endpoint, username, password, proxy=None):
        self.client = client
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.upload_operation = ContainerOperationOnFolder('tutum/curl:latest', 'curl -v -F r={r} -F hasPom=false -F e={e} -F g={g} -F a={a} -F v={v} -F p={p} -F file=@{file}  -u {username}:{password} {endpoint}/service/local/artifact/maven/content', environment=proxy if proxy else {})
        self.download_operation = ContainerOperationOnFolder('tutum/curl:latest', 'curl -o {o} {endpoint}/service/local/artifact/maven/content?g={g}&a={a}&v={v}&r={r}', environment=proxy if proxy else {})

    def split_file(self, file):
        return os.path.basename(file), os.path.dirname(file)


    def upload(self, repository, package):
        filename, filepath = self.split_file(package['binary_path'])
        output, cmd = self.upload_operation.apply(self.client, volumes=['{}:/target'.format(filepath)], r=repository, e=package['type'], g=package['groupId'], a=package['artifactId'], v=package['version'], p=package['type'], file='/target/{}'.format(filename), username=self.username, password=self.password, endpoint=self.endpoint)
        print cmd
        print output
        return output

    def download(self, workdir, repository, package, app_filename='app.jar'):
        if not workdir.endswith('/'):
            workdir = workdir + '/'
        output, cmd = self.download_operation.apply(self.client, volumes=['{}:/target'.format(workdir)], o='/target/{}'.format(app_filename), r=repository, g=package['groupId'], a=package['artifactId'], v=package['version'], endpoint=self.endpoint)
        print cmd
        print output
        return workdir + app_filename