# WEBSITE CI/CD PIPELINE

This is a sample project created to test automated CI/CD pipeline.

### Used Tools:
* Docker
* Jenkins (Running inside Docker)
* Github

### High level Workflow:
1. **Install Docker Desktop**   
   Ensure Docker is installed and running on your system.

2. **Build the Custom Jenkins Image**  
   Use the base Jenkins image and include your corporate root CA certificate.

   `docker build -t <image-name> .`

3. **Run Jenkins in a Conatiner**   
    Start he Jenkins container with port mapping:

    `Docker run --name <containername> -p 8080:8080 <imagename>`

4. **Create the web server project**    
    In Ubuntu, create and update the required files to run the web server such as
        * Application code (python code)
        * Dockerfile(to run the website)
        * Jenkinsfile (to define the pipeline)
        * Other files such as scripts needed to run the pipeline

5. **Push to Github for version control**   
    * Initialize git in local and push the code to feature/main branch.
    * If pushed to feature branch, open a merge request.
    * If merge conflict arises then go to the conflict and manually resolve the conflict and merge it.

6. **Setup Jenkins Pipeline**   
    * In Jenkins, create a new pipeline job.
    * Setup Jenkins pipeline to connect with the git repo.
    * Setup triggers to run jenkins job by using 'polling SCM'.

### Note:   

* Since, we are using Jenkins inside a docker container, Jenkins will not be able to use the host Docker Daemon to create a container if the job requires it.
* So, we will create a docker container using `jenkins/inbound-agent:latest` image which will talk with the host Docker Daemon to create containers.
