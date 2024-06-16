## Prerequisites

### .env File
Ensure the `.env` file contains the following:

```
PIPEDRIVE_API_TOKEN=
MYSQL_ROOT_PASSWORD=password
MYSQL_DATABASE=mydatabase
MYSQL_USER=user
MYSQL_PASSWORD=password
DATABASE_URL=mysql+pymysql://user:password@mysql:3306/mydatabase
```

### Local Deployment
To deploy locally, run the following commands:

```bash
sudo docker-compose down && sudo docker-compose build --no-cache && sudo docker-compose up
```

### API Information
- Kubernetes is used for scaling and managing deployments.
- Terraform is used for provisioning and controlling the infrastructure.
- Gists are treated as activities within the Pipedrive terms.

The app is currently running at http://aa5c77547cadf474288fe4544e86894e-1282359386.eu-central-1.elb.amazonaws.com/docs

#### API Endpoints
- **GET /gists/{username}**: Retrieve new gists for a user from the database and mark them as old.
- **GET /gists/{username}/new**: Sync and retrieve the latest gists for a user from GitHub.
- **GET /users**: Fetch a list of all users.
- **DELETE /gists/delete_random**: Delete a random gist.
- **DELETE /users/{username}**: Delete a user and their associated gists.
- **GET /github/rate_limit**: Get GitHub API rate limit status.

For more details, please refer to the application swagger documentation available at `/docs`.

### AWS and Kubernetes Setup

Before you begin, ensure you have the following prerequisites:

- An AWS account with appropriate permissions.
- Terraform installed on your local machine.
- AWS CLI installed and configured with your AWS credentials.
- Kubectl installed.

#### IAM Roles and Policies
Create the following IAM roles with their respective policies:

- **EKS-WORKER-NODE-ROLE**:
  - **Policies**:
    - AmazonEC2ContainerRegistryReadOnly
    - AmazonEKS_CNI_Policy
    - AmazonEKSWorkerNodePolicy

- **EksClusterRole**:
  - **Policies**:
    - AmazonEKSClusterPolicy

### Docker Image Management

Build and push the Docker image to Amazon ECR:
You do need to make an ecr repo, i called mine pipedrive and made it private.

```bash
aws ecr get-login-password --region eu-central-1 | sudo docker login --username AWS --password-stdin 992382561999.dkr.ecr.eu-central-1.amazonaws.com
sudo docker build -t pipedrive . --no-cache
sudo docker tag pipedrive:latest 992382561999.dkr.ecr.eu-central-1.amazonaws.com/pipedrive:latest
sudo docker push 992382561999.dkr.ecr.eu-central-1.amazonaws.com/pipedrive:latest
```

### Creating Secrets in Kubernetes

Create the necessary secrets in Kubernetes:

```bash
kubectl create secret generic mysql-secret --from-env-file=../.env
kubectl create secret generic mysecret --from-file=.dockerconfigjson=/root/.docker/config.json --type=kubernetes.io/dockerconfigjson
```
If it gives you permission problems, copy the config file to the repo folder for example. (Or any other with sufficient permissions)
### Terraform Deployment
Initialize and apply the Terraform configuration:

```bash
cd terraform
terraform init
terraform apply
```

```
module.eks.aws_eks_node_group.node_group: Still creating...
module.eks.aws_eks_addon.addons["coredns"]: Still creating...
```
NB! In case you feel like the build in aws gets stuck on one part (e.g. 20 min in my case), you can quit and start it again, terraform will pick up where it finished.
### Kubernetes Configuration

1. **Configure kubectl**: Set up `kubectl` to use your EKS cluster:

   ```bash
   aws eks update-kubeconfig --region eu-central-1 --name eks-app
   ```

2. **Deploy MySQL and App**: Wait until the MySQL pod is in the running state, then apply the app manifest:

   ```bash
   kubectl apply -f mysql.yml
   kubectl apply -f app.yml
   ```

3. **Check Deployment Status**: Verify the deployment status:

   ```bash
   kubectl get all
   ```

   Ensure the `app-deployment` has the desired number of replicas and note the external IP address under the `EXTERNAL-IP` column.

4. **Access the App**: Open a web browser and navigate to the external IP address to access the App welcome page.


### Project Choices and Justifications
This application was built using FastAPI due to its modern features, such as automatic interactive API documentation with Swagger and ReDoc, as well as its performance benefits from being built on Starlette and combined with SQLAlchemy for database interactions.

I thought activities in pipedrive fit the role of a gist more than deals.

Implemented endpoints for manual testing (not to be constraint to waiting 3 hours)

Decided to use aws, because i was used to it at work and google cloud didnt let me activate the free tier :(
