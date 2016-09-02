import pyuilder

workspace = pyuilder.WorkspaceManager().createNew()

if __name__ == '__main__':
	mvn = pyuilder.MVN()
	git = pyuilder.Git()
	pyuilder.ctl.start()
	
	workDir = workspace.subfolder("springbootwebapp")
	git.clone("https://github.com/geowarin/springboot-jersey.git").to(workDir)
	mvn.package(workDir)
	#mvn.package(workDir)