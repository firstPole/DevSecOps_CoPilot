from pipelinetypes import *
import streamlit as st

def convert_azure_devops_to_pipeline(parsed_data):
    print(f"Parsed Azure DevOps data: {parsed_data}")
    if isinstance(parsed_data, AzureDevOpsPipeline):
        return parsed_data  # If already an AzureDevOpsPipeline, return it directly.

    pipeline = AzureDevOpsPipeline()  # Create an AzureDevOpsPipeline instance

    # Preserve the order of stages
    for stage in parsed_data.get("stages", []):
        stage_name = stage.get("stage", "Unnamed Stage")  # Correctly get the stage name
        pipeline.add_stage(PipelineStage(stage_name))

        # Add jobs to each stage
        for job in stage.get("jobs", []):
            job_name = job.get("displayName", "Unnamed Job")
            job_obj = PipelineJob(job_name)

            # Process steps in each job
            for step in job.get("steps", []):
                step_name = step.get("displayName", "Unnamed Step")
                step_obj = PipelineStep(step_name, step.get("task", "Unknown Task"), step.get("inputs", {}))
                job_obj.add_step(step_obj)

            pipeline.add_job_to_stage(stage_name, job_obj)

    return pipeline


def convert_github_actions_to_pipeline(parsed_data):
    if isinstance(parsed_data, GitHubActionsPipeline):
        return parsed_data  # If already a GitHubActionsPipeline, return it directly.

    pipeline = GitHubActionsPipeline()  # Create a GitHubActionsPipeline instance

    jobs = parsed_data.get("jobs", [])
    # Preserve the order of jobs
    for job in jobs:
        job_name = job.get("name", "Unnamed Job")
        pipeline.add_stage(PipelineStage(job_name))

        # Add jobs to each stage
        job_obj = PipelineJob(job_name)
        pipeline.add_job_to_stage(job_name, job_obj)

    return pipeline

def convert_gitlab_ci_to_pipeline(parsed_data):
    if isinstance(parsed_data, GitLabPipeline):
        return parsed_data  # If already a GitLabCIPipeline, return it directly.

    pipeline = GitLabPipeline()  # Create a GitLabCIPipeline instance

    stages = parsed_data.get("stages", [])
    # Preserve the order of stages
    for stage in stages:
        pipeline.add_stage(PipelineStage(stage))

        # Add jobs to each stage
        stage_obj = PipelineStage(stage)
        pipeline.add_job_to_stage(stage, PipelineJob(f"{stage}_job"))

    return pipeline

def convert_jenkins_scripted_to_pipeline(parsed_data):
    st.write(parsed_data)
    if isinstance(parsed_data, JenkinsPipeline):
        return parsed_data  # If already a JenkinsPipeline, return it directly.

    if isinstance(parsed_data, str):
        stages = extract_stages_from_script(parsed_data)
        if not stages:
            raise ValueError("No stages found in the provided Jenkins scripted pipeline script.")

        pipeline = JenkinsPipeline()  # Create a JenkinsPipeline instance

        # Iterate over stages in the order they appear, not as a set (to preserve order)
        for stage in stages:  
            pipeline.add_stage(PipelineStage(stage))
            job_obj = PipelineJob(f"{stage}_job")
            pipeline.add_job_to_stage(stage, job_obj)
    else:
        raise ValueError("Expected raw Groovy script for Jenkins scripted pipeline.")

    return pipeline

def convert_jenkins_declarative_to_pipeline(parsed_data):
    if isinstance(parsed_data, JenkinsPipeline):
        return parsed_data  # If already a JenkinsPipeline, return it directly.

    pipeline = JenkinsPipeline()  # Create a JenkinsPipeline instance

    if isinstance(parsed_data, dict):
        pipeline_structure = parsed_data.get("pipeline", {})
        if not pipeline_structure:
            raise ValueError("Missing 'pipeline' key in the Jenkins declarative pipeline data.")

        stages = pipeline_structure.get("stages", [])
        if not stages:
            raise ValueError("No stages defined in the Jenkins declarative pipeline data.")

        # Preserve the order of stages
        for stage in stages:
            stage_name = stage.get("name")
            if not stage_name:
                raise ValueError("A stage is missing the 'name' field in the Jenkins declarative pipeline.")
            pipeline.add_stage(PipelineStage(stage_name))
            job_obj = PipelineJob(f"{stage_name}_job")
            pipeline.add_job_to_stage(stage_name, job_obj)
    else:
        raise ValueError("Expected a dictionary format for Jenkins declarative pipeline.")

    return pipeline

def convert_bamboo_to_pipeline(parsed_data):
    if isinstance(parsed_data, BambooPipeline):
        return parsed_data  # If already a BambooPipeline, return it directly.

    pipeline = BambooPipeline()  # Create a BambooPipeline instance

    # Preserve the order of stages
    for stage in parsed_data.get("stages", []):
        stage_name = stage if isinstance(stage, str) else stage.get("name", "Unnamed Stage")
        pipeline.add_stage(PipelineStage(stage_name))

        # Add jobs to each stage
        for job in stage.get("jobs", []):
            job_name = job.get("displayName", "Unnamed Job")
            job_obj = PipelineJob(job_name)
            pipeline.add_job_to_stage(stage_name, job_obj)

    return pipeline

def convert_aws_codepipeline_to_pipeline(parsed_data):
    if isinstance(parsed_data, AWSPipeline):
        return parsed_data  # If already an AWSPipeline, return it directly.

    pipeline = AWSPipeline()  # Create an AWSPipeline instance

    stages = parsed_data.get("stages", [])
    # Preserve the order of stages
    for stage in stages:
        stage_name = stage if isinstance(stage, str) else stage.get("name", "Unnamed Stage")
        pipeline.add_stage(PipelineStage(stage_name))

        # For AWS CodeBuild, CodeDeploy, we can add corresponding jobs
        for job in stage.get("jobs", []):
            job_name = job.get("name", "Unnamed Job")
            job_obj = PipelineJob(job_name)
            pipeline.add_job_to_stage(stage_name, job_obj)

            # Add steps for each job (This part was missing in your original code)
            for step in job.get("steps", []):
                step_name = step.get("name", "Unnamed Step")
                step_task = step.get("task", "Unknown Task")
                step_inputs = step.get("inputs", {})
                step_obj = PipelineStep(name=step_name, task=step_task, inputs=step_inputs)
                job_obj.add_step(step_obj)  # Adding the step to the job

    return pipeline


def convert_circleci_to_pipeline(parsed_data):
    if isinstance(parsed_data, CircleCIPipeline):
        return parsed_data  # If already a CircleCIPipeline, return it directly.

    pipeline = CircleCIPipeline()  # Create a CircleCIPipeline instance

    jobs = parsed_data.get("jobs", [])
    # Preserve the order of jobs
    for job in jobs:
        job_name = job.get("name", "Unnamed Job")
        pipeline.add_stage(PipelineStage(job_name))

        # Add jobs to each stage
        job_obj = PipelineJob(job_name)
        pipeline.add_job_to_stage(job_name, job_obj)

    return pipeline



# def convert_aws_to_pipeline(parsed_data):
#     pipeline = AWSPipeline()  # Create an AWSPipeline instance

#     stages = parsed_data.get("stages", [])
#     for stage in stages:
#         stage_name = stage if isinstance(stage, str) else stage.get("name", "Unnamed Stage")
#         pipeline.add_stage(PipelineStage(stage_name))
        
#         # For AWS CodeBuild, CodeDeploy, we can add corresponding jobs
#         job_obj = PipelineJob(f"{stage_name}_job")
#         pipeline.add_job_to_stage(stage_name, job_obj)

#     return pipeline


def extract_stages_from_script(script):
    """
    A placeholder function to parse the Groovy script and extract stage names.
    This function uses regex to identify `stage('...')` or `stage("...")`.
    """
    import re
    stage_pattern = r"stage\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"  # Regex to match stage names
    stages = re.findall(stage_pattern, script)

    if not stages:
        print("No stages found. Check if the script follows the expected format.")
    
    return stages
