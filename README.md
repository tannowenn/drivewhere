# drivewhere
drive here drive there drive everywhere


<!-- Deploying on Kubernetes -->
We will be using Minikube to be deployed locally. 
Some prerequities before running this project on Kubernetes:
- Have Docker installed on the machine
- Have some form of SQL client (such as mySQL workbench)
- 20 GB of free space


Step 1: Install Minikube
We can install Minikube through this link (https://minikube.sigs.k8s.io/docs/start/) and only follow Step 1 of the documentation

Step 2: Start up the cluster
After installation, we can start up the cluster! Let's name our cluster drivewhere and give it two nodes
`minikube start --nodes 2 --profile drivewhere`
Starting minikube will take some time (and also some disk space!)

We can ensure we have 2 nodes (1 master, 1 slave) by typing:
`kubectl get nodes`

Step 3: Creating configMap for AMQP
We need to create the configMap for the setup of RabbitMQ, navigate to the kubernetes folder on the command line and enter these two lines 
`kubectl create configmap rabbitmq-config --from-file=rabbitmq.config=rabbitmq.config`
`kubectl create configmap rabbitmq-definitions --from-file=rabbitmq.config=rabbitmq_definitions.json`

We should see a success message such as configmap/rabbitmq-config created

Step 4: Creating secrets for API keys and database password
`kubectl create secret generic db-pw --from-literal=password=1234`
`kubectl create secret generic gmaps-key --from-literal=APIKEY=AIzaSyBkH3BTvWeG9UzLMNhSJsm95KxNNDpi0yE`
`kubectl create secret generic stripe-key --from-literal=STRIPE_KEY=sk_test_51OuU6ERwhPaLZQ7Jc38nX5rpjYnhJbtspXQ5EMvskpjbnsDTotjrA1GciZZKFUyPBWwZnO0IGlVsdqmFWlX4Rgba000ObBunlu`
`kubectl create secret generic gmail-pass --from-literal=GMAIL_APP_PASS=vzsoycpwksezvrey`

We should see a success message such as secret/db-pw created

Step 5: Adding the deployment to the nodes
`kubectl apply -f amqp-deployment.yaml`
`kubectl apply -f db-statefulset.yaml`
`kubectl apply -f email-deployment.yaml` 
`kubectl apply -f error-deployment.yaml` 
`kubectl apply -f master-deployment.yaml` 
`kubectl apply -f payment-deployment.yaml` 
`kubectl apply -f rental-deployment.yaml` 
`kubectl apply -f user-deployment.yaml` 

Open the dashboard
`minikube dashboard -p drivewhere`
If any deployments/pods/statefulsets appear as failed, give it a while as it is taking awhile to mount the PVC!

If everything is successful, you should see this
![Kubernetes Dashboard](image.png)

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
![email sent by drivewhere1@gmail.com](image-1.png)

When user return the car successfully, you should see two emails
![email sent by drivewhere1@gmail.com](image-2.png)