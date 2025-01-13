Creating a secure Jenkins CI/CD pipeline for a Java application to be deployed on Azure Kubernetes Service (AKS) involves several stages, including static application security testing (SAST), dynamic application security testing (DAST), image scanning, Kubernetes security scanning, and monitoring. Below is a sample Jenkins pipeline configuration that incorporates these stages, along with best practices for security, maintainability, scalability, and disaster recovery.

### Jenkinsfile Example

```groovy
pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "myapp:${env.BUILD_ID}"
        AZURE_CREDENTIALS = credentials('azure-credentials')
        K8S_CLUSTER_NAME = "my-aks-cluster"
        K8S_NAMESPACE = "default"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git 'https://github.com/my-org/my-java-app.git'
            }
        }

        stage('Build') {
            steps {
                script {
                    // Build the Java application
                    sh './gradlew build'
                }
            }
        }

        stage('SAST - Static Code Analysis') {
            steps {
                script {
                    // Run SAST tool (e.g., SonarQube)
                    sh 'sonar-scanner -Dsonar.projectKey=my-java-app -Dsonar.host.url=http://sonarqube-server'
                }
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    // Run unit tests
                    sh './gradlew test'
                }
            }
        }

        stage('Image Build and Scan') {
            steps {
                script {
                    // Build Docker image
                    sh 'docker build -t $DOCKER_IMAGE .'
                    
                    // Scan Docker image for vulnerabilities
                    sh 'trivy image --exit-code 1 --severity HIGH,CRITICAL $DOCKER_IMAGE'
                }
            }
        }

        stage('DAST - Dynamic Testing') {
            steps {
                script {
                    // Run DAST tool (e.g., OWASP ZAP)
                    sh 'zap.sh -cmd -quickurl http://myapp-url -quickout zap_report.html'
                }
            }
        }

        stage('Kubernetes Security Scan') {
            steps {
                script {
                    // Scan Kubernetes manifests for security issues (e.g., kube-score)
                    sh 'kube-score score k8s/deployment.yaml'
                }
            }
        }

        stage('Deploy to AKS') {
            steps {
                script {
                    // Configure Azure CLI
                    sh 'az login --service-principal -u $AZURE_CREDENTIALS_USERNAME -p $AZURE_CREDENTIALS_PASSWORD --tenant <TENANT_ID>'
                    sh 'az aks get-credentials --resource-group <RESOURCE_GROUP> --name $K8S_CLUSTER_NAME'
                    
                    // Deploy to AKS
                    sh "kubectl apply -f k8s/deployment.yaml -n $K8S_NAMESPACE"
                    sh "kubectl apply -f k8s/service.yaml -n $K8S_NAMESPACE"
                }
            }
        }

        stage('Monitor and Rollback') {
            steps {
                script {
                    // Implement monitoring and self-healing checks
                    sh 'kubectl get pods -n $K8S_NAMESPACE'
                    
                    // Optional: Add logic for rollback if necessary
                    // sh "kubectl rollout undo deployment/myapp -n $K8S_NAMESPACE"
                }
            }
        }
    }

    post {
        always {
            // Archive artifacts and reports
            archiveArtifacts artifacts: 'zap_report.html', fingerprint: true
            junit 'build/test-results/**/*.xml'
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed.'
        }
    }
}
```

### Key Components Explained

1. **SAST**: Static Application Security Testing is performed using tools like SonarQube, which scans the codebase for vulnerabilities and code quality issues.

2. **Unit Tests**: Running unit tests ensures that the application logic is functioning correctly.

3. **Image Build and Scan**: The Docker image is built and scanned using tools like Trivy to identify vulnerabilities.

4. **DAST**: Dynamic Application Security Testing is performed using tools like OWASP ZAP, which tests the running application for vulnerabilities.

5. **Kubernetes Security Scan**: Tools like kube-score can be used to scan Kubernetes manifests for security best practices.

6. **Deployment**: The application is deployed to the AKS cluster using `kubectl`.

7. **Monitoring and Rollback**: Basic monitoring checks are performed, and there is an option for rolling back the deployment if issues are detected.

### Security Considerations

- **Secrets Management**: Use Jenkins credentials to manage sensitive information securely.
- **Access Control**: Ensure that only authorized personnel can trigger the pipeline.
- **Regular Updates**: Keep the tools and dependencies up to date to mitigate vulnerabilities.

### Monitoring and Service Mesh

- **Monitoring**: Integrate Azure Monitor or Prometheus for monitoring and alerting.
- **Service Mesh**: Consider using Istio or Linkerd for managing service-to-service communication and observability in Kubernetes.

### Disaster Recovery and Self-Healing

- **Automated Backups**: Implement a backup strategy for critical data and configurations.
- **Self-Healing**: Kubernetes inherently provides self-healing features; ensure that liveness and readiness probes are configured correctly.

This pipeline is an example and can be customized further based on specific project needs and organizational policies.