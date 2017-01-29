# Real Quick Start
Make sure that you have python 2.7 and docker installed. Then just try this:
```
python sample.py
```
Look at the `sample.py` and write your own build scripts.

# pyuilder
As a software developer I want to code my delivery build & deploy pipeline. I want to have all the flexibility and the advantages with my build-process that I know from coding, like versioning, tracking changes, modularization etc. It should look more or less like this:
```python
# -------------- compile & unit-test ---------------- 
mvn.update_version(application_folder, version)
application_package = mvn.package(application_folder)

# -------------- publish ----------------------------
application_artifact = nexus.upload(repository='saral-web', package=application_package)

# -------------- deploy to stage --------------------
cloud_foundry.deploy(application_artifact, stage)
```

That is what I thought when I started my latest project several weeks ago. I had to set up a process that would take source code as input and would deliver a running service to the users, again. I was doing almost the same thing every time I started a new project. However due to minor differences reuse was very limited and felt more like copy & paste. Most of the powerful tools back then were offering visual pipeline definitions or configurations in a DSLs (XML, JSON or YAML formatted). I missed the toolset I had as a developer, the ability modularise, reuse, audit without sacrificing readability. 

So I decided to create my library. Not a framework with hooks that controls the flow. It had to be a library that I can embed into any code. That would give me much flexibility. I could create a standalone script and let Jenkins call it after checking out the latest version of the source code. Or I could create a standalone web service reacting to the events from GitHub and execute my pipeline. Or I could embed my pipeline definition (which is running code) into a workflow engine. Possibilities were unlimited. The best part was, it should live right next to the source code of my application, in the same repository. Usually, configurations of tools like Jenkins are kept outside. Although you can put them under version control, you have to maintain their version separately from your application. Imagine starting with a monolithic web service. You would build one single application. When you split it up into two microservices, your build pipeline must be adapted accordingly. Your best option is to create a second build job since you still want to build the older versions of your monolithic application. Not with the library approach. Your pipeline definition is just code that lives in the same revision in your repository alongside with the code of your application. You have a new architecture requiring a change in your pipeline, you just refactor your pipeline definition. No need to duplicate anything. When you execute your pipeline for a specific version of your application, you are actually executing the matching version of the pipeline.

The idea was simple. I would wrap bash scripts as Python functions and group them by modules. Very soon I noticed another problem: I had to install build-time dependencies on the machine(s) where I would like to run my scripts. There had to be an easier way. So I decided to group scripts by common dependencies and execute them in Docker containers. Docker images would encapsulate the build dependencies. The build dependencies were thus reduced to solely Docker and Python. Here it was: Pyuilder. Now let's dive into some concepts.

# Concepts
A pipeline is a function that receives source code as input and produces a running service. A pipeline consists of several stages. The goal of every stage is to increase the confidence in the release candidate or to discard it. A stage consists of functions applied to the output of the previous stage. The first function is applied to the source code. For example, the commit stage is applied to the source code of a certain revision, produces binary artifacts and stores them on a binary repository. Acceptance test stage installs those artifacts to the test environment.


