import os
import streamlit as st
from git import Repo, GitCommandError
from urllib.parse import quote

def commit_to_git(repo_path, commit_message, file_path, generated_code, token):
    try:
        if not token:
            return False, "GitHub Personal Access Token is required."
        if not repo_path:
            return False, "Git repository path is required."

        # Ensure the token is correctly encoded
        encoded_token = quote(token)
        repo_url = f"https://{encoded_token}:x-oauth-basic@github.com/{repo_path}.git"

        # Initialize or clone repository
        repo_dir = os.path.abspath("./repo")
        if not os.path.exists(repo_dir):
            st.write(f"Cloning repository from {repo_url}...")
            repo = Repo.clone_from(repo_url, repo_dir)
            st.success(f"Repository cloned successfully: {repo_dir}")
        else:
            repo = Repo(repo_dir)
            if repo.is_dirty():
                repo.git.add("--all")
                repo.index.commit("Auto-committing local changes")
            repo.remotes.origin.fetch()

        # Save the generated code to file within the repo
        target_path = os.path.join(repo_dir, file_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        st.write(f"Saving file to: {target_path}")
        with open(target_path, 'w') as f:
            f.write(generated_code)

        # Stage the file and commit changes
        repo_path_relative = os.path.relpath(target_path, repo.working_tree_dir)
        st.write(f"Staging file: {repo_path_relative}")
        repo.git.add(repo_path_relative)

        st.write(f"Committing changes with message: {commit_message}")
        repo.index.commit(commit_message)

        # Set the credential helper to store the token
        repo.git.config('--global', 'credential.helper', 'store')

        # Push changes to the remote repository
        st.write("Pushing changes to the remote repository...")
        repo.git.push("origin", "main")  # Replace 'main' with the actual branch if needed
        os.remove(repo_path_relative)
        return True, "Code successfully committed and pushed to Git!"
        

    except GitCommandError as git_error:
        if 'Authentication failed' in str(git_error):
            return False, "Authentication failed. Check your GitHub Personal Access Token."
        return False, f"Git operation failed: {git_error}"

    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

