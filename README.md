# Deploying with Docker
## Prerequisites
To deploy the application with the use of Docker, some prerequisites must be made.
- Windows machine (_this will still work with other OSes such as macOS and linux with caveats such as different default login credentials for MySQL, etc. but the setup guide will be catered to Windows users_)
- Have Docker installed on the machine. You can install Docker desktop from this link (https://www.docker.com/get-started) 
- Have a Docker account. You can create an account from this link (https://hub.docker.com)
- Have WAMP Server installed on your machine. You can install from this link (https://sourceforge.net/projects/wampserver/)
- Have an SQL client installed such as mySQL workbench. You can also install from this link (https://dev.mysql.com/downloads/workbench/)

## Setup
1. Install the folders and files in this repository to your local drive

1. Move the "frontend" folder inside the "docker_images" directory to the "www" folder inside "wamp64" folder of your local drive

1. Start your WAMP server

1. Start your Docker desktop

1. Open your WAMP server and log in using root as your username (_no password needed unless using MAMP, then password is root_) 

1. Import the SQL files inside docker_images to create databases in your local machine. Import the following files
    - error.sql
    - payment.sql
    - rental.sql
    - user.sql
        - Note for user.sql, you will need to use your own "stripeId" values from test "Connect" accounts from your Stripe account if you wish to see the payment process on your Stripe account.

1. Ensure you have created an account 'is213'@'%' with no password in MySQL and it is granted all privileges for all tables in the databases created in the previous step. You may do this in client that can use MySQL (e.g phpMyAdmin). (_If you wish to use a different account name/password, ensure that you change the dbURL values in the `.env` file below accordingly_)

1. Move to the docker_images folder through the terminal

    `cd docker_images`

1. Add an `.env` file inside which will be used by `compose.yaml` during docker compose. Here are the default values in an `.env` file that this setup will use for this project (_You may change these values yourself but make sure you follow the same settings in the next steps. Note that certain values with the <> still need to be changed as they are secrets/API keys that you will need to obtain for yourself_):

    ```
    USER_dbURL=mysql+mysqlconnector://is213@host.docker.internal:3306/user
    RENTAL_dbURL=mysql+mysqlconnector://is213@host.docker.internal:3306/rental
    PAYMENT_dbURL=mysql+mysqlconnector://is213@host.docker.internal:3306/payment
    ERROR_dbURL=mysql+mysqlconnector://is213@host.docker.internal:3306/error
    ERROR_QUEUE=Error
    EMAIL_QUEUE=Email
    RABBIT_HOST=rabbitmq
    RABBIT_PORT=5672
    RABBIT_WEB_PORT=15672
    FRONTEND_HOST=host.docker.internal
    MASTER_HOST=master
    MASTER_PORT=5100
    USER_HOST=user
    USER_PORT=5001
    RENTAL_HOST=rental
    RENTAL_PORT=5002
    EMAIL_HOST=email
    EMAIL_PORT=5003
    PAYMENT_HOST=payment
    PAYMENT_PORT=5004
    ERROR_HOST=error
    ERROR_PORT=5005
    STRIPE_KEY=<your_stripe_key>
    GMAPS_KEY=<your_googlemaps_api_key>
    GMAIL_APP_PASS=<your_google_app_pass>
    ```
    More information on the secrets/API keys you need:
    - STRIPE_KEY: Taken from your Stripe account, make sure it is a test key as this project uses the test version.
    - GMAPS_KEY: Obtained from the Google cloud console using your Google account.
    - GMAIL_APP_PASS: Obtained from App Passwords in your Google account.

1. Build all the services by keying the command to your terminal

    `docker compose up -d`

    Take note that the services might take a while to setup so be patient!

1. Open your web browser and go to http://localhost/frontend

1. Run through the scenarios

1. Upon completion of your experience input the following to stop the containers.

    `docker compose down`

    - Delete the images if necessary
    - Turn off your WAMP and docker desktop
    - We hope you enjoyed experiencing our DriveWhere project


# Deploying on Kubernetes 
## Prerequisites
We will be using Minikube to be deployed locally. 
Some prerequities before running this project on Kubernetes:
- Have Docker installed on the machine
- Have some form of SQL client (such as mySQL workbench)
- 20 GB of free space

## Setup
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
`kubectl create configmap rabbitmq-definitions --from-file=rabbitmq_definitions.json=rabbitmq_definitions.json`

We should see a success message such as configmap/rabbitmq-config created
<hr>
Step 4: Creating secrets for API keys and database password

`kubectl create secret generic db-pw --from-literal=password=<yourPassword>` <br>
`kubectl create secret generic gmaps-key --from-literal=APIKEY=<yourAPIKey>` <br>
`kubectl create secret generic stripe-key --from-literal=STRIPE_KEY=<yourStripeAPIKey>` <br>
`kubectl create secret generic gmail-pass --from-literal=GMAIL_APP_PASS=<yourGmailPass>` <br>

We should see a success message such as secret/db-pw created
<hr>
Step 5: Adding the deployment to the nodes

`kubectl apply -f amqp-deployment.yaml` <br>
`kubectl apply -f db-statefulset.yaml` <br>
`kubectl apply -f email-deployment.yaml`  <br>
`kubectl apply -f error-deployment.yaml`  <br>
`kubectl apply -f master-deployment.yaml`  <br>
`kubectl apply -f frontend-deployment.yaml`  <br>
`kubectl apply -f payment-deployment.yaml`  <br>
`kubectl apply -f rental-deployment.yaml`  <br>
`kubectl apply -f user-deployment.yaml` <br>

Open the dashboard: <br>
`minikube dashboard -p drivewhere` <br>
If any deployments/pods/statefulsets appear as failed, give it a while as it is taking awhile to mount the PVC!

If everything is successful, you should see this
![Kubernetes Dashboard](/images/k8s_dashboard.png)
<hr>
Step 6: Adding data to the database <br>
We need to portforward the db-service to localhost to add the data!

`kubectl port-forward service/db-service 3306:3306`

- Open MySQL Workbench or your MySQL client and click on the localinstance and enter the password 1234
- Copy the sql code from db.sql in the Kubernetes file and run it in the workbench
- If you would like to test the email, add your own email address to the database!
<hr>

Step 7: Port forward the services

Find the frontend pod <br>
`kubectl get pods` <br>
Select the frontend-deployment <br>
![image](https://github.com/tannowenn/drivewhere/assets/142380212/5342303c-5f78-4742-904a-adeb6eb55b3f)


Now we port-forward the services <br>
`kubectl port-forward <name of frontend-pod> 8080:80` <br>
`kubectl port-forward service/master-service 5100:5100` <br>
`kubectl port-forward service/rental-service 5002:5002` <br>

<hr>

Step 8: Run through the scenarios <br>
**Scenario 1: Owner creates listing** <br>
**Scenario 2: User rents a car** <br> 
If it is successful, you should see two emails <br>
![email sent by drivewhere1@gmail.com](/images/rent_email.png)
<br>
**Scenario 3: User returns the car and Owner releases payment** <br>
When user return the car successfully, you should see two emails
![email sent by drivewhere1@gmail.com](/images/return_email.png)
