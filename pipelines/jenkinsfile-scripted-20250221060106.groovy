Certainly! Below is a Jenkins Pipeline script for a secure CI/CD process for a Java application to be deployed on Azure Kubernetes Service (AKS). The pipeline includes stages for Static Application Security Testing (SAST), Dynamic Application Security Testing (DAST), image scanning, and Kubernetes security scanning.

### Jenkins Pipeline Script

```groovy
pipeline {
    agent any

    environment {
        // Define environment variables here
        DOCKER_IMAGE = 'your-docker-image-name'  // Placeholder for Docker image name
        DOCKER_REGISTRY = 'your-docker-registry'  // Placeholder for Docker registry
        K8S_NAMESPACE = 'your-k8s-namespace'      // Placeholder for Kubernetes namespace
        AKS_CLUSTER = 'your-aks-cluster-name'     // Placeholder for AKS cluster name
        SAST_TOOL = 'your-sast-tool'               // Placeholder for SAST tool
        DAST_TOOL = 'your-dast-tool'               // Placeholder for DAST tool
        IMAGE_SCAN_TOOL = 'your-image-scan-tool'  // Placeholder for image scan tool
        K8S_SCAN_TOOL = 'your-k8s-scan-tool'      // Placeholder for Kubernetes scan tool
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout source code from the repository
                git 'https://github.com/your-repo/your-java-app.git'
            }
        }

        stage('Build') {
            steps {
                // Build the Java application using Maven
                sh 'mvn clean install'
            }
        }

        stage('SAST') {
            steps {
                // Run Static Application Security Testing
                sh "${SAST_TOOL} --source ."
            }
        }

        stage('Unit Tests') {
            steps {
                // Run unit tests
                sh 'mvn test'
            }
        }

        stage('Image Build') {
            steps {
                // Build Docker image
                sh "docker build -t ${DOCKER_IMAGE} ."
            }
        }

        stage('Image Scan') {
            steps {
                // Scan Docker image for vulnerabilities
                sh "${IMAGE_SCAN_TOOL} scan ${DOCKER_IMAGE}"
            }
        }

        stage('DAST') {
            steps {
                // Run Dynamic Application Security Testing
                sh "${DAST_TOOL} --target http://your-app-url"
            }
        }

        stage('K8s Security Scan') {
            steps {
                // Scan Kubernetes manifests for security issues
                sh "${K8S_SCAN_TOOL} scan k8s-manifest.yaml"
            }
        }

        stage('Deploy to AKS') {
            steps {
                // Deploy to AKS
                sh "kubectl apply -f k8s-manifest.yaml --namespace=${K8S_NAMESPACE}"
            }
        }

        stage('Post-Deployment Tests') {
            steps {
                // Run post-deployment tests
                sh 'curl -f http://your-app-url/health'
            }
        }
    }

    post {
        always {
            // Clean up workspace
            cleanWs()
        }
        success {
            // Notify on success
            echo 'Deployment Successful!'
        }
        failure {
            // Notify on failure
            echo 'Deployment Failed!'
        }
    }
}
```

### Placeholders, Variables, and Descriptions

| Placeholder/Variable        | Value/Description                        |
|-----------------------------|-----------------------------------------|
| `your-docker-image-name`    | Name of the Docker image to be built.  |
| `your-docker-registry`      | Docker registry URL (e.g., Docker Hub, Azure Container Registry). |
| `your-k8s-namespace`        | Kubernetes namespace where the app will be deployed. |
| `your-aks-cluster-name`     | Name of the Azure Kubernetes Service cluster. |
| `your-sast-tool`            | Command or script to run the SAST tool. |
| `your-dast-tool`            | Command or script to run the DAST tool. |
| `your-image-scan-tool`      | Command or script to perform image scanning. |
| `your-k8s-scan-tool`        | Command or script to scan Kubernetes manifests for security issues. |
| `your-repo/your-java-app.git`| Git repository URL of the Java application. |
| `http://your-app-url`       | URL endpoint of the deployed application for DAST and health checks. |
| `k8s-manifest.yaml`         | Kubernetes manifest file for deployment. |

### Security and Performance Considerations
- Ensure that sensitive information such as Docker registry credentials and any API keys are stored securely in Jenkins credentials and retrieved at runtime.
- Avoid hardcoding sensitive information in the pipeline script.
- Use efficient base images and multi-stage builds in Docker to reduce image size and improve performance.
- Consider parallelizing stages where possible to speed up the pipeline execution.
- Regularly update the tools used for SAST, DAST, and scanning to ensure you are protected against the latest vulnerabilities.

This modular Jenkins pipeline provides a comprehensive approach to CI/CD while integrating security checks at various stages, ensuring both security and quality in the deployed application.