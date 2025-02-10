import json
class PipelineStep:
    def __init__(self, name, task, inputs=None,condition=None):
        """
        Initialize a PipelineStep instance.

        :param name: Name or display name of the step (e.g., "Build Docker Image").
        :param task: The task associated with the step (e.g., "Docker@2").
        :param inputs: A dictionary of inputs required for the task (e.g., Dockerfile paths, tags).
        """
        self.name = name  # Step's name (displayName).
        self.task = task  # The task to be executed in the step (e.g., Docker@2).
        self.inputs = inputs if inputs else {}  # Inputs for the task, defaults to an empty dictionary.
        self.condition = condition
    def __repr__(self):
        return f"PipelineStep(Name: {self.name}, Task: {self.task}, Inputs: {self.inputs})"

    def to_raw_code(self):
        """
        Convert the step to raw code (a string) for a specific pipeline format.
        This is a placeholder and can be customized further depending on the pipeline type.
        """
        step_code = f"        - name: {self.name}\n"
        step_code += f"          task: {self.task}\n"

        # If there's a condition, include it in the step code
        if self.condition:
            step_code += f"          condition: {self.condition}\n"

        return step_code


class PipelineJob:
    def __init__(self, name):
        self.name = name
        self.steps = []  # A list to store steps in the job.

    def add_step(self, step):
        """
        Add a step to this job.

        :param step: The PipelineStep instance to be added.
        """
        self.steps.append(step)

    def to_raw_code(self):
        """
        Convert the job to raw code (string format) for a specific pipeline.
        This should be implemented in subclasses.
        """
        job_code = f"      - job: {self.name}\n"
        job_code += f"        steps:\n"
        
        for step in self.steps:
            job_code += step.to_raw_code()  # Calling `to_raw_code()` on the individual step
        
        return job_code


class PipelineStage:
    def __init__(self, name, jobs=None):
        self.name = name
        self.jobs = jobs if jobs else []

    def add_job(self, job):
        """
        Add a job to this stage.

        :param job: The PipelineJob instance to be added.
        """
        self.jobs.append(job)

    def to_raw_code(self):
        """
        Convert the stage to raw code (string format) for a specific pipeline.
        This is a placeholder and can be customized further depending on the pipeline type.
        """
        stage_code = f"  - stage: {self.name}\n"
        stage_code += f"    jobs:\n"
        
        for job in self.jobs:
            stage_code += job.to_raw_code()  # Calling `to_raw_code()` on the individual job
        
        return stage_code


class Pipeline:
    def __init__(self):
        self.stages = []

    def add_stage(self, stage):
        """
        Add a stage to the pipeline.

        :param stage: The PipelineStage instance to be added.
        """
        self.stages.append(stage)

    def add_job_to_stage(self, stage_name, job):
        """
        Add a job to a stage in the pipeline.

        :param stage_name: The name of the stage to add the job to.
        :param job: The PipelineJob instance to be added.
        """
        for stage in self.stages:
            if stage.name == stage_name:
                stage.add_job(job)
                break

    def to_raw_code(self):
        pipeline_code = "trigger: none\n\npr:\n  branches:\n    include:\n      - main\n\njobs:\n"
        
        for stage in self.stages:
            pipeline_code += stage.to_raw_code()  # Calling `to_raw_code()` on the individual stage
        
        return pipeline_code


# Pipeline Format Implementations

class BambooPipeline(Pipeline):
    def __init__(self):
        super().__init__()

    def to_raw_code(self):
        bamboo_yaml = "plan:\n  name: Bamboo CI/CD Pipeline\n  stages:\n"
        for stage in self.stages:
            bamboo_yaml += f"    - {stage.name}:\n"
            bamboo_yaml += "      jobs:\n"
            for job in stage.jobs:
                bamboo_yaml += f"        - {job.name}\n"
                bamboo_yaml += "        steps:\n"
                for step in job.steps:
                    bamboo_yaml += f"          - {step.name}: {step.task}\n"
        return bamboo_yaml


class AWSPipeline(Pipeline):
    def __init__(self):
        super().__init__()

    def to_raw_code(self):
        if not self.stages:
            raise ValueError("No stages found in the pipeline.")

        aws_code_pipeline_json = {
            "version": "1.0",
            "stages": []
        }

        for stage in self.stages:
            stage_dict = {
                "name": stage.name,
                "actions": []
            }

            for job in stage.jobs:
                for step in job.steps:
                    action = {
                        "name": step.name,
                        "actionTypeId": {
                            "category": "Build",  # Modify as per actual AWS CodePipeline stage type
                            "owner": "AWS",
                            "provider": step.task,
                            "version": "1"
                        },
                        "configuration": step.inputs if step.inputs else {},
                        "outputArtifacts": [],
                        "inputArtifacts": [],
                        "runOrder": 1  # AWS CodePipeline requires a run order
                    }
                    stage_dict["actions"].append(action)

            if not stage_dict["actions"]:
                raise ValueError(f"No actions found in stage: {stage.name}")

            aws_code_pipeline_json["stages"].append(stage_dict)

        return json.dumps(aws_code_pipeline_json, indent=2)


class CircleCIPipeline(Pipeline):
    def __init__(self):
        super().__init__()

    def to_raw_code(self):
        circleci_yaml = "version: 2.1\nworkflows:\n  version: 2\n  jobs:\n"
        for stage in self.stages:
            circleci_yaml += f"    {stage.name}:\n"
            circleci_yaml += f"      docker:\n"
            for job in stage.jobs:
                circleci_yaml += f"        - image: {job.name}\n"
                for step in job.steps:
                    circleci_yaml += f"        - name: {step.name}\n"
                    circleci_yaml += f"          run: {step.task}\n"
        return circleci_yaml


class JenkinsPipeline(Pipeline):
    def __init__(self):
        super().__init__()

    def to_raw_code(self):
        jenkinsfile = "pipeline {\n"
        for stage in self.stages:
            jenkinsfile += f"    stage('{stage.name}') {{\n"
            for job in stage.jobs:
                jenkinsfile += f"        {job.name}()\n"
                for step in job.steps:
                    jenkinsfile += f"        script: {step.name} - {step.task}\n"
            jenkinsfile += "    }\n"
        jenkinsfile += "}"
        return jenkinsfile


class GitLabPipeline(Pipeline):
    def __init__(self):
        super().__init__()

    def to_raw_code(self):
        gitlab_yaml = "stages:\n"
        for stage in self.stages:
            gitlab_yaml += f"  - {stage.name}\n"
        for stage in self.stages:
            gitlab_yaml += f"\n{stage.name}:\n"
            for job in stage.jobs:
                gitlab_yaml += f"  script: {job.name}\n"
                for step in job.steps:
                    gitlab_yaml += f"    - {step.name}: {step.task}\n"
        return gitlab_yaml


class AzureDevOpsPipeline(Pipeline):
    def __init__(self):
        super().__init__()

    def to_raw_code(self):
        azure_yaml = "trigger:\n  branches:\n    include:\n      - main\n\njobs:\n"
        for stage in self.stages:
            azure_yaml += f"  - job: {stage.name}\n"
            azure_yaml += f"    steps:\n"
            for job in stage.jobs:
                azure_yaml += f"      - script: {job.name}\n"
                for step in job.steps:
                    azure_yaml += f"        - name: {step.name}\n"
                    azure_yaml += f"          script: {step.task}\n"
        return azure_yaml


class GitHubActionsPipeline(Pipeline):
    def __init__(self):
        super().__init__()

    def to_raw_code(self):
        github_yaml = "name: CI/CD\non: [push]\n\njobs:\n"
        for stage in self.stages:
            github_yaml += f"  {stage.name}:\n"
            github_yaml += f"    runs-on: ubuntu-latest\n"
            github_yaml += f"    steps:\n"
            for job in stage.jobs:
                for step in job.steps:
                    github_yaml += f"      - name: {step.name}\n"
                    github_yaml += f"        run: {step.task}\n"
        return github_yaml
