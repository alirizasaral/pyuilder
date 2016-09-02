import controller

workspace = controller.WorkspaceManager().createNew()

if __name__ == '__main__':
	mvn = controller.MVN()
	git = controller.Git()
	controller.ctl.start()
	
	workDir = workspace.subfolder("springbootwebapp")
	git.clone("https://github.com/springframeworkguru/springbootwebapp.git").to(workDir)
	mvn.package(workDir)
	#mvn.package(workDir)