
drive here drive there drive everywhere

# Deploying with Docker
To deploy the application with the use of Docker, some prerequisites must be made.
- Have Docker installed on the machine. You can install Docker desktop from this link (https://www.docker.com/get-started) 
- Have a Docker account. You can create an account from this link (https://hub.docker.com)
- Have WAMP Server installed on your machine. You can install from this link (https://sourceforge.net/projects/wampserver/)
- Have an SQL client installed such as mySQL workbench. You can also install from this link (https://dev.mysql.com/downloads/workbench/)

<hr>
Step 1: Install the folders and files in this repository to your local drive
<hr>
Step 2: Move the frontend folder inside docker_images to www folder inside wamp64 folder
<hr>
Step 3: Start your WAMP server
<hr>
Step 4: Start your Docker desktop
<hr>
Step 5: Open your WAMP server and log in using root as your username(no password needed unless using MAMP, then password is root) 
<hr>
Step 6: Import the SQL files inside docker_images to create databases in your local machine. Import the following files <br>
- error.sql
- payment.sql
- rental.sql
- user.sql
<hr>
Step 7: Move to the docker_images folder through the terminal <br>

`cd docker_images`
<hr>
Step 8: Build all the services by keying the command to your terminal<br>

`docker compose up -d`
Take note that the services might take a while to setup so be patient!
<hr>
Step 9: open your web browser and type in localhost/frontend
<hr>
Step 10: Run through the scenarios<br>
Scenario 1: Owner lists rental car
- drivewherrrrr
- drivewherrrrr
- drivewherrrrr
<br>
Scenario 2: Renter rents car
- drivewherrrrr
- drivewherrrrr
- drivewherrrrr
<br>
Scenario 3: Renter returns car
- drivewherrrrr
- drivewherrrrr
- drivewherrrrr
<hr>
Step 11: Upon completion of your experience input the following to stop the containers.<br>

`docker compose down`
<br>
Delete the images if necessary
<br>
Turn off your WAMP and docker desktop
<br>
We hope you enjoyed experiencing our DriveWhere project


# Deploying on Kubernetes 
We will be using Minikube to be deployed locally. 
Some prerequities before running this project on Kubernetes:
- Have Docker installed on the machine
- Have some form of SQL client (such as mySQL workbench)
- 20 GB of free space

<hr>
Step 1: Install Minikube
We can install Minikube through this link (https://minikube.sigs.k8s.io/docs/start/) and only follow Step 1 of the documentation
<hr>
Step 2: Start up the cluster
After installation, we can start up the cluster! Let's name our cluster drivewhere and give it two nodes <br>

`minikube start --nodes 2 --profile drivewhere`
Starting minikube will take some time (and also some disk space!)

We can ensure we have 2 nodes (1 master, 1 slave) by typing: <br>
`kubectl get nodes`
<hr>
Step 3: Creating configMap for AMQP
We need to create the configMap for the setup of RabbitMQ, navigate to the kubernetes folder on the command line and enter these two lines 

`kubectl create configmap rabbitmq-config --from-file=rabbitmq.config=rabbitmq.config` <br>
`kubectl create configmap rabbitmq-definitions --from-file=rabbitmq.config=rabbitmq_definitions.json`

We should see a success message such as configmap/rabbitmq-config created
<hr>
Step 4: Creating secrets for API keys and database password

`kubectl create secret generic db-pw --from-literal=password=<yourPassword>` <br>
`kubectl create secret generic gmaps-key --from-literal=APIKEY=<yourAPIKey>` <br>
`kubectl create secret generic stripe-key --from-literal=STRIPE_KEY=<yourStripeAPIKey>` <br>
`kubectl create secret generic gmail-pass --from-literal=GMAIL_APP_PASS=yourGmailPass` <br>

We should see a success message such as secret/db-pw created
<hr>
Step 5: Adding the deployment to the nodes

`kubectl apply -f amqp-deployment.yaml` <br>
`kubectl apply -f db-statefulset.yaml` <br>
`kubectl apply -f email-deployment.yaml`  <br>
`kubectl apply -f error-deployment.yaml`  <br>
`kubectl apply -f master-deployment.yaml`  <br>
`kubectl apply -f payment-deployment.yaml`  <br>
`kubectl apply -f rental-deployment.yaml`  <br>
`kubectl apply -f user-deployment.yaml` <br>

Open the dashboard: <br>
`minikube dashboard -p drivewhere` <br>
If any deployments/pods/statefulsets appear as failed, give it a while as it is taking awhile to mount the PVC!

If everything is successful, you should see this
![Kubernetes Dashboard](/images/k8s_dashboard.png)
<hr>
Step 6: Adding data to the database
We need to portforward the db-service to localhost to add the data!

`kubectl port-forward service/db-service 3306:3306`

- Open up MySQL and click on the localinstance and enter the password 1234
- Copy the sql code from db.sql in the Kubernetes file and run it in the workbench
- If you would like to test the email, add your own email address to the database!

Step 6: Run through the scenarios
blah blah blah
...
If it is successful, you should see two emails
![email sent by drivewhere1@gmail.com](/images/rent_email.png)

When user return the car successfully, you should see two emails
![email sent by drivewhere1@gmail.com](/images/return_email.png)
