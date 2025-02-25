import streamlit as st
import os
from datetime import datetime
import asyncio
from git_utils import commit_to_git
from visualdiagram import generate_diagram_from_pipeline
from pipeline_patterns import PIPELINE_TYPE_PATTERNS
import re
from conversion import * 
from pipelineparser import PipelineParser, parse_yaml_code  # Import functions from pipelineparser
from main import generate_pipeline
from pipelinetypes import *
import utils



def identify_pipeline_type(generated_code):
    for pipeline_type, pattern in PIPELINE_TYPE_PATTERNS.items():
        if all(keyword.lower() in generated_code.lower() for keyword in pattern["keywords"]):
            return pipeline_type, pattern["file_extension"], pattern["language"]
    return "unknown", ".txt", "text"

def initialize_session_state():
    session_defaults = {
        "generated_code": None,
        "generated_file_path": None,
        "show_commit_ui": False,
        "repo_path": "",
    }
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

async def generate_pipeline_ui():
    initialize_session_state()

    user_prompt = st.text_input(
        "Enter your prompt (e.g., 'Generate an Azure DevOps Pipeline to deploy Microservices application to AKS.'): ",
        key="user_prompt",
        placeholder="Type your pipeline generation request here..."
    )

    
    provider_flag = "Azure"

    if st.button("Generate Pipeline"):
        if not user_prompt:
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Generating pipeline based on industry best practices and your needs...."):
                try:
                    document_path = "best_practices"
                    generated_code = await generate_pipeline(user_prompt, document_path, provider_flag)

                    if generated_code:
                        st.success("Pipeline generated successfully!")
                        pipeline_type, file_extension, language = identify_pipeline_type(generated_code)
                        
                        st.code(generated_code, language=language)

                        file_name = f"{pipeline_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
                        pipelines_dir = "pipelines"
                        os.makedirs(pipelines_dir, exist_ok=True)
                        file_path = os.path.join(pipelines_dir, file_name)
                        with open(file_path, "w") as file:
                            file.write(generated_code)

                        st.session_state.generated_code = generated_code
                        st.session_state.generated_file_path = file_path
                        st.session_state.show_commit_ui = True

                        st.download_button(
                            label="Download Pipeline",
                            data=generated_code,
                            file_name=file_name,
                            mime="text/plain"
                        )
                        
                        

                        try:
                            # Initialize PipelineParser and generate diagram
                            pipeline_parser = PipelineParser(pipeline_code=generated_code, pipeline_type=pipeline_type)
                            parsed_data = pipeline_parser.parse_pipeline_code()
                            st.write(f"Parsed Data Type: {type(parsed_data)}")
                            st.write(f"Parsed stream Type: {type(pipeline_type)}")

                            # Ensure parsed_data is a valid Pipeline object with stages and jobs
                            if isinstance(parsed_data, Pipeline):  # Only proceed if it's a subclass of Pipeline
                                pipeline_type = pipeline_type.lower().strip()  # Ensure consistent lowercase input
                                pipeline_type_class = {
                                    "jenkinsfile-scripted": JenkinsPipeline,
                                    "jenkinsfile-declarative": JenkinsPipeline,
                                    "azure-pipelines": AzureDevOpsPipeline,
                                    "gitlab-ci": GitLabPipeline,
                                    "github-actions": GitHubActionsPipeline,
                                    "codepipeline": AWSPipeline,
                                }.get(pipeline_type)

                                print(f"Pipeline Type Class: {pipeline_type_class}")

                                if pipeline_type_class is None:
                                    st.error(f"Unsupported or invalid pipeline type: {pipeline_type}. Please check your input.")
                                else:
                                    # Validate the pipeline type using the helper function
                                    if utils.validate_pipeline_type(parsed_data, pipeline_type_class):
                                        # Pass the appropriate subclass to generate_diagram
                                        try:
                                            diagram = generate_diagram_from_pipeline(parsed_data, pipeline_type_class)
                                            if diagram:
                                                st.image(diagram, caption=f"{pipeline_type.title()} Pipeline Visualization")
                                            else:
                                                st.error("Failed to generate pipeline diagram. Please check the pipeline data.")
                                        except Exception as e:
                                            st.error(f"An error occurred while generating the diagram: {str(e)}")
                            else:
                                st.error("Parsed data is not a valid pipeline object.")
                                                            

                        except Exception as e:
                            st.error(f"An error occurred while generating the diagram: {e}")
                    else:
                        st.warning("No code was generated. Please review your prompt and try again.")
                except Exception as e:
                    st.error(f"An error occurred during pipeline generation: {e}")

    if st.session_state.get("show_commit_ui", False):
        render_commit_ui()

def render_commit_ui():
    st.markdown("### Commit Generated Code to Git")

    auth_method = st.selectbox("Select Authentication Method:", ("Personal Access Token (PAT)", "OAuth App"))

    if auth_method == "Personal Access Token (PAT)":
        repo_path = st.text_input("Enter Git Repository Path: (username/repository_name)", value=st.session_state.repo_path)
        token = st.text_input("Enter your GitHub Personal Access Token:", type="password")

    elif auth_method == "OAuth App":
        repo_path = st.text_input("Enter Git Repository Path: (username/repository_name)", value=st.session_state.repo_path)

        client_id = os.environ.get("GITHUB_CLIENT_ID", "")
        client_secret = os.environ.get("GITHUB_CLIENT_SECRET", "")
        redirect_uri = os.environ.get("GITHUB_REDIRECT_URI", "")

        if not client_id or not client_secret or not redirect_uri:
            st.warning("OAuth App credentials are missing or incomplete.")
            return

        auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=repo&redirect_uri={redirect_uri}"

        if st.button("Authorize with GitHub"):
            st.experimental_rerun()

    if st.button("Commit"):
        file_path = st.session_state.generated_file_path
        if not os.path.isfile(file_path):
            st.error(f"The file {file_path} does not exist. Please generate the pipeline first.")
        else:
            try:
                commit_message = "Generated pipeline code"
                success, message = commit_to_git(
                    repo_path, commit_message, file_path,
                    st.session_state.generated_code,
                    github_token=token if auth_method == "Personal Access Token (PAT)" else None
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)
            except Exception as e:
                st.error(f"An error occurred during Git commit: {e}")

if __name__ == "__main__":
    st.set_page_config(page_title="Pipeline Generator",  layout="wide")
    st.markdown(
    """
    <style>
    .streamlit-expander .streamlit-code-container pre { /* Target code container within expander */
        white-space: pre-wrap !important; /* Enable text wrapping */
        overflow-x: auto; /* Allow horizontal scrolling if wrapping creates very long lines*/
        max-width: 100%; /* Ensure it takes full container width */
    }
    .streamlit-code-container pre { /* Target code container */
        white-space: pre-wrap !important; /* Enable text wrapping */
        overflow-x: auto; /* Allow horizontal scrolling if wrapping creates very long lines*/
        max-width: 100%; /* Ensure it takes full container width */
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    st.title("Dev(Sec)Ops Co-Pilot")
    st.sidebar.title("About")
    st.sidebar.text("DevSecOps Co-pilot to assist in generating CI/CD Pipelines as per industry standards.")
    asyncio.run(generate_pipeline_ui())
