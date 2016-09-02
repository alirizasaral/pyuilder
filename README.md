# Real Quick Start
Make sure that you have python 2.7 and docker installed. Then just try this:
```
python sample.py
```
Look at the `sample.py` and write your own build scripts.

# pyuilder
As a software developer I want to build my software with code. I want to have all the flexibility and the advantages with my build-process that I know from coding, like versioning, tracking changes, modularization etc. So I started with the idea, how it would look like, if I defined my build-pipe in python. Here is what I came up with:

```python
import pyuilder

if __name__ == '__main__':
	mvn = pyuilder.MVN()
	git = pyuilder.Git()
	nexus = pyuilder.Nexus("<my nexus parameters>")
	pyuilder.ctl.start()

	workspace = pyuilder.WorkspaceManager().createNew()
	workDir = workspace.subfolder("springbootwebapp")
	git.clone("https://github.com/springframeworkguru/springbootwebapp.git").to(workDir)
	package = mvn.package(workDir)
	nexus.upload(package)
```

