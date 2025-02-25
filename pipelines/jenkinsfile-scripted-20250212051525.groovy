Here's a Jenkins CI/CD pipeline configuration for a Java application, incorporating various security stages like Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), image scanning, and Kubernetes security scanning. This pipeline is designed for deployment to Azure Kubernetes Service (AKS). 

The pipeline uses Jenkins declarative syntax for clarity and maintainability.

### Jenkinsfile

```groovy
pipeline {
    agent any

    environment {
        // Define environment variables here
        DOCKER_IMAGE_NAME = 'your-docker-image-name' // Placeholder for Docker image name
        DOCKER_IMAGE_TAG = 'latest' // Placeholder for Docker image tag
        AKS_CLUSTER_NAME = 'your-aks-cluster-name' // Placeholder for AKS cluster name
        RESOURCE_GROUP = 'your-resource-group' // Placeholder for Azure resource group
        SAST_TOOL = 'your-sast-tool' // Placeholder for SAST tool configuration
        DAST_TOOL = 'your-dast-tool' // Placeholder for DAST tool configuration
        IMAGE_SCAN_TOOL = 'your-image-scan-tool' // Placeholder for image scanning tool
        K8S_SECURITY_SCAN_TOOL = 'your-k8s-security-scan-tool' // Placeholder for K8s security scanning tool
    }

    stages {
        stage('Build') {
            steps {
                script {
                    echo "Building the Java application..."
                    // Add commands to build your Java application (e.g., Maven, Gradle)
                    sh 'mvn clean package'
                }
            }
        }

        stage('SAST') {
            steps {
                script {
                    echo "Running SAST..."
                    // Add commands to run SAST tool
                    sh "${SAST_TOOL} --source-path=./src"
                }
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    echo "Running unit tests..."
                    // Add commands to run unit tests
                    sh 'mvn test'
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    echo "Building Docker image..."
                    // Build Docker image
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG} ."
                }
            }
        }

        stage('Image Scan') {
            steps {
                script {
                    echo "Scanning Docker image..."
                    // Add commands to scan Docker image
                    sh "${IMAGE_SCAN_TOOL} ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                script {
                    echo "Deploying to AKS..."
                    // Add commands to deploy to AKS
                    sh "az aks get-credentials --resource-group ${RESOURCE_GROUP} --name ${AKS_CLUSTER_NAME}"
                    sh "kubectl apply -f k8s/deployment.yaml"
                }
            }
        }

        stage('DAST') {
            steps {
                script {
                    echo "Running DAST..."
                    // Add commands to run DAST tool
                    sh "${DAST_TOOL} --target-url=http://your-app-url"
                }
            }
        }

        stage('K8s Security Scan') {
            steps {
                script {
                    echo "Running Kubernetes security scan..."
                    // Add commands to run Kubernetes security scan
                    sh "${K8S_SECURITY_SCAN_TOOL} k8s/deployment.yaml"
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    echo "Cleaning up..."
                    // Add cleanup commands if necessary
                    sh "docker rmi ${DOCKER_IMAGE_NAME}:${DOCKER_IMAGE_TAG}"
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline finished!"
            // Add additional notifications or cleanup tasks
        }
    }
}
```

### Placeholders and Variables

1. `your-docker-image-name`: Replace with the name of the Docker image to be built.
2. `latest`: Replace with the desired tag for the Docker image.
3. `your-aks-cluster-name`: Replace with the name of your Azure Kubernetes Service cluster.
4. `your-resource-group`: Replace with the name of your Azure resource group where the AKS cluster is located.
5. `your-sast-tool`: Replace with the command or path to your chosen SAST tool (e.g., SonarQube, Checkmarx).
6. `your-dast-tool`: Replace with the command or path to your chosen DAST tool (e.g., OWASP ZAP, Burp Suite).
7. `your-image-scan-tool`: Replace with the command or path to your chosen image scanning tool (e.g., Trivy, Clair).
8. `your-k8s-security-scan-tool`: Replace with the command or path to your chosen Kubernetes security scanning tool (e.g., kube-hunter, kube-score).
9. `your-app-url`: Replace with the URL of your deployed application for DAST testing.
10. `k8s/deployment.yaml`: Replace with the path to your Kubernetes deployment configuration file.

### Security Considerations
- Ensure sensitive information (like credentials) is stored in Jenkins credentials store and accessed securely.
- Use secure protocols for all communications.
- Regularly update your security tools and dependencies.
- Implement access controls and monitor for security vulnerabilities in your CI/CD pipeline. 

### Performance Considerations
- Use caching strategies for Docker layers to speed up image builds.
- Optimize your SAST and DAST tools to only scan the necessary components, reducing overhead.
- Ensure that the tests run in parallel when applicable to reduce pipeline execution time.

This pipeline structure is modular, making it easy to integrate or replace security tools as needed.