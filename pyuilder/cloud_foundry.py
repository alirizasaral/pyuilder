from dockerlayer import ContainerOperationOnFolder
import os.path

IMAGE = 'lwieske/cloudfoundrycli:latest'

class CloudFoundry(object): 

    def __init__(self, docker_client, endpoint, username, password, organization):
        self.docker_client = docker_client
        self.endpoint = endpoint
        self.username = username
        self.password = password
        self.organization = organization

        self.deploy_operation = ContainerOperationOnFolder(IMAGE, self.get_cmd_steps())

    def get_cmd_steps(self):
        return [
                'cf login -a {endpoint} -u {username} -p {password} -o {organization} --skip-ssl-validation'.format(endpoint=self.endpoint, username=self.username, password=self.password, organization=self.organization) + ' -s {space}',
                'cf push {app_name} -p {app_path} -f {manifest}'
                ]

    def get_volumes(self, app, manifest):
        appdir = os.path.dirname(app)
        manifestdir = os.path.dirname(manifest)
        appdir_alias = '/app'
        manifestdir_alias = '/manifest'
        volumes = ['{}:{}'.format(appdir, appdir_alias), 
                   '{}:{}'.format(manifestdir, manifestdir_alias)]
        return volumes, '{}/{}'.format(appdir_alias, os.path.basename(app)), '{}/{}'.format(manifestdir_alias, os.path.basename(manifest))

    def deploy(self, app_name, app, manifest, space):
        print app
        volumes, app_in_container, manifest_in_container = self.get_volumes(app, manifest)
        print volumes
        output, cmd = self.deploy_operation.apply(self.docker_client, volumes, app_name=app_name, space=space, app_path=app_in_container, manifest=manifest_in_container)
        print cmd
        print output
        return output