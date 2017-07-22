import docker
import logging

logger = logging.getLogger("pyuilder")
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

class ContainerFunction:

    def __init__(self,  command, container):
        self.command = command
        self.container = container

    def __call__(self, *args):
        cmd = self.command + " " + " ".join(args)
        return self.container.execute(cmd)

class Container:

    def __init__(self, image, **kwargs):
        self.image = image
        self.kwargs = kwargs

    def __enter__(self):
        self.__start()
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __getattr__(self, name):
        return ContainerFunction(name, self)

    def __start(self):
        docker.from_env().images.pull(self.image)

    def execute(self, cmd):
        logger.info("Executing command: {}".format(cmd))
        container = docker.from_env().containers.run(self.image, cmd, detach=True, **self.kwargs)
        for line in container.logs(stream=True):
            logger.info(line.strip())
