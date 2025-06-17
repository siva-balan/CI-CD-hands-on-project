# WEBSITE

This is a sample project created to test automated CI/CD pipeline.

### Used Tools:
* Docker
* Jenkins (Run Inside Docker)
* Gitlab 

### High level overview of the process followed:
* Install Docker desktop.
* Build jenkins image using basic jenkins image and update the CA cert file.
* Run Jenkins image and install the required plugins.
* In Ubuntu, create the required files such as
    * Application code (HTML code)
    * Dockerfile(to run the website)
    * Jenkinsfile (to define the pipeline)
    * other files such as scripts needed to run the pipeline
* Initalize git in local and push the code to feature branch/main branch.
* If pushed to feature branch, open a merge request, and merge it if no conflicts.
* Setup Jenkins pipeline to connect with the git repo and setup triggers to run jenkins job by polling SCM according to the required timeframe.

