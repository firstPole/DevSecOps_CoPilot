import streamlit as st
from main import generate_pipeline
import asyncio
from git_utils import commit_to_git
import os
from datetime import datetime
import re

def identify_pipeline_type(generated_code):
    """
    Analyzes the generated code to identify the pipeline type and file extension.

    Args:
        generated_code: The generated pipeline code as a string.

    Returns:
        A tuple containing the pipeline type (e.g., "codepipeline", "gitlab-ci", "jenkinsfile"), 
        file extension (e.g., ".yaml", ".groovy"), and language (e.g., "yaml", "groovy").
    """

    # 1. Basic Keyword Checks (with improved robustness)
    if re.search(r"aws\s+codepipeline", generated_code, re.IGNORECASE): 
        return "codepipeline", ".yaml", "yaml"
    elif "jobs" in generated_code and "stages" in generated_code: 
        if "gitlab-ci" in generated_code: 
            return "gitlab-ci", ".yaml", "yaml" 
        elif "github" in generated_code: 
            return "github-actions", ".yaml", "yaml"
    elif "pipeline" in generated_code and "stages" in generated_code: 
        if "agent" in generated_code: 
            return "jenkinsfile-scripted", "groovy", "groovy" 
        else: 
            return "jenkinsfile-declarative", ".yaml", "yaml" 
    elif "plan" in generated_code and "stages" in generated_code: 
        return "bamboo", ".yaml", "yaml" 
    elif "workflows" in generated_code and "jobs" in generated_code: 
        return "circleci", ".yaml", "yaml" 
    elif "trigger" in generated_code and "pool" in generated_code and "steps" in generated_code: 
        return "azure-pipelines", ".yaml", "yaml" 

    # 2. Structural Analysis (more robust)
    if "apiVersion: apps/v1" in generated_code and "kind: Deployment" in generated_code: 
        # Potential Kubernetes Deployment within a pipeline 
        if "pipeline" in generated_code and "stages" in generated_code: 
            return "codepipeline", ".yaml", "yaml" 

    # 3. Default Case
    return "unknown", ".txt", "text" 

async def generate_pipeline_ui():
    """
    Generates the pipeline based on user input and displays it in the correct format.
    """
    user_prompt = st.text_input(
        "Enter your prompt (e.g., 'Generate an Azure DevOps Pipeline to deploy Microservices application to AKS.'): ",
        key="user_prompt",
        placeholder="Type your pipeline generation request here..."
    )

    if st.button("Generate Pipeline"):
        if not user_prompt:
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Generating pipeline based on industry best practices and your needs...."):
                try:
                    document_path = "devsecops_best_practices.docx"
                    generated_code = await generate_pipeline(user_prompt, document_path)

                    if generated_code:
                        st.success("Pipeline generated successfully!")

                        # Identify pipeline type and file extension
                        pipeline_type, file_extension, language = identify_pipeline_type(generated_code)

                        st.code(generated_code, language=language) 

                        file_name = f"{pipeline_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"

                        # Ensure the "pipelines" directory exists
                        pipelines_dir = "pipelines"
                        os.makedirs(pipelines_dir, exist_ok=True)

                        # Save the generated code to the correct file extension
                        file_path = os.path.join(pipelines_dir, file_name)
                        with open(file_path, "w") as file:
                            file.write(generated_code)

                        # Store generated code and file path in session state for "Commit to Git"
                        st.session_state.generated_code = generated_code
                        st.session_state.generated_file_path = file_path
                        st.session_state.show_commit_ui = True

                    else:
                        st.warning("No code was generated. Please review your prompt and try again.")

                except Exception as e:
                    st.error(f"An error occurred: {e}")

    # Commit to Git section, visible after code generation
    if st.session_state.get("show_commit_ui", False):
        st.markdown("### Commit Generated Code to Git")

        if 'repo_path' not in st.session_state:
            st.session_state.repo_path = ""

        st.info("To commit your changes, enter your GitHub repository path (e.g., 'username/repo') and Personal Access Token.")
        st.warning("If you have enabled 2FA on GitHub, please use a Personal Access Token (PAT) instead of your password.")

        repo_path = st.text_input("Enter Git Repository Path: (username/repository_name)", value=st.session_state.repo_path)
        token = st.text_input("Enter your GitHub Personal Access Token:", type="password")

        if st.button("Commit"):
            if repo_path and token:
                commit_message = "Generated pipeline code"
                file_path = st.session_state.generated_file_path

                # Ensure the file exists before attempting to commit
                if not os.path.isfile(file_path):
                    st.error(f"The file {file_path} does not exist. Please generate the pipeline first.")
                else:
                    success, message = commit_to_git(repo_path, commit_message, file_path, st.session_state.generated_code, token)

                    if success:
                        st.success(message)
                        st.session_state.show_commit_ui = False
                       
                            # Clean up the file after successful commit
                            # os.remove(file_path)
                            # st.success(f"Cleaned up the generated file: {file_path}")
                        

                    else:
                        st.error(message)
            else:
                st.warning("Please provide both the Git repository path and your GitHub Personal Access Token.")

if __name__ == "__main__":
    st.set_page_config(page_title="Pipeline Generator")
    st.title("Dev(Sec)Ops Co-Pilot")
    st.sidebar.title("About")
    st.sidebar.text("DevSecOps Co-pilot to help and assist in generating CI/CD Pipelines according to best practice and industry standards")

    asyncio.run(generate_pipeline_ui())

