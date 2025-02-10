import os
import streamlit as st
from git import Repo, GitCommandError
from urllib.parse import quote
import requests


def commit_to_git(repo_path, commit_message, file_path, generated_code, 
                 github_token=None, username=None, password=None, 
                 client_id=None, client_secret=None, redirect_uri=None):
    

    try:
        if not repo_path:
            return False, "Git repository path is required."

        # Determine the repository URL based on authentication method
        if github_token:
            encoded_token = quote(github_token)
            repo_url = f"https://{encoded_token}@github.com/{repo_path}.git" 
        elif username and password:
            auth = (username, password)
            repo_url = f"https://{username}@{username}.github.io/{repo_path}.git"
        elif client_id and client_secret and redirect_uri:
            # For OAuth, you'll use the repository URL without authentication details
            repo_url = f"https://github.com/{repo_path}.git" 
        else:
            return False, "Either GitHub Token, username/password, or Client ID/Secret and Redirect URI are required."

        # Print where the file is being pushed
        st.write(f"Repository URL: {repo_url}")

        # Initialize or clone repository
        repo_dir = os.path.abspath("./repo")
        if not os.path.exists(repo_dir):
            st.write(f"Cloning repository from {repo_url}...")
            repo = Repo.clone_from(repo_url, repo_dir)
            st.success(f"Repository cloned successfully: {repo_dir}")
        else:
            repo = Repo(repo_dir) 

        # Save the generated code to file within the repo
        target_path = os.path.join(repo_dir, file_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        st.write(f"Saving file to: {target_path}")
        with open(target_path, 'w') as f:
            f.write(generated_code)

        # Print file being pushed to
        st.write(f"File being pushed to: {target_path}")

        # Stage the file and commit changes
        repo_path_relative = os.path.relpath(target_path, repo.working_tree_dir) 
        st.write(f"Staging file: {repo_path_relative}")
        repo.git.add(repo_path_relative)

        st.write(f"Committing changes with message: {commit_message}")
        repo.index.commit(commit_message)

        # Push changes to the remote repository
        st.write("Pushing changes to the remote repository...")
        repo.git.push("origin", "main") 
        # Handle authentication and push (code for pushing would be here)

        os.remove(repo_path_relative)
        return True, "Code successfully committed and pushed to Git!"

    except GitCommandError as git_error:
        if 'Authentication failed' in str(git_error):
            return False, "Authentication failed. Check your credentials."
        return False, f"Git operation failed: {git_error}"

    except Exception as e:
        return False, f"An unexpected error occurred: {e}"
