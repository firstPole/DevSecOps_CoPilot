from conversion import *
from pipelinetypes import *
import re
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
import streamlit as st
import json
def clean_and_format_yaml(code):
    """Cleans and formats YAML code while preserving indentation."""

    # Remove Markdown-style delimiters
    code = code.replace("```yaml", "").replace("```", "")

    # Strip unnecessary leading and trailing whitespace from the entire code
    code = code.strip()

    # Split into lines and preserve indentation
    lines = [line.rstrip() for line in code.splitlines()]

    # Remove empty lines
    lines = [line for line in lines if line]

    # Ensure YAML starts with '---' (for YAML parsers that require it)
    if lines and not lines[0].startswith("---"):
        lines.insert(0, "---")

    # Join cleaned lines with proper indentation
    return "\n".join(lines)




def parse_yaml_code(code, handler_name):
    """Parses YAML code and maps it to the appropriate handler."""
    if not code.strip():
        return {"error": "Empty YAML code provided."}

    try:
        cleaned_code = clean_and_format_yaml(code)
        ruamel_yaml = YAML(typ='safe')
        ci_config = ruamel_yaml.load(cleaned_code)
        return handler_name(ci_config)
    except YAMLError as e:
        error_details = re.search(r"line (\d+), column (\d+)", str(e))
        error_message = f"YAML parsing error on line {error_details.group(1)}, column {error_details.group(2)}" if error_details else f"YAML parsing error: {e}"
        return {"error": error_message}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}


def clean_jenkins_script(script):
    """Remove comments, explanations, and unnecessary placeholders from Jenkins Groovy scripts."""
    # Remove single-line comments (e.g., // comment)
    script = re.sub(r'//.*$', '', script, flags=re.MULTILINE)

    # Remove multi-line comments (e.g., /* comment */)
    script = re.sub(r'/\*.*?\*/', '', script, flags=re.DOTALL)

    # Remove unnecessary placeholders like AWS GetAtt or Sub
    script = re.sub(r'AWS-GetAtt-Placeholder', '', script)
    script = re.sub(r'AWS-Sub-Placeholder', '', script)

    # Optional: Remove debug or unnecessary print statements (e.g., println, echo)
    script = re.sub(r'println\s*\(.*?\)', '', script)
    script = re.sub(r'echo\s*\(.*?\)', '', script)

    # Remove extra spaces or newlines created after cleaning
    script = re.sub(r'\n+', '\n', script).strip()

    return script


def extract_yaml_code(text):
    """Extracts YAML code enclosed in ```yaml delimiters and preserves indentation."""
    match = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    if match:
        yaml_content = match.group(1)
        # Split into lines and preserve original indentation
        lines = yaml_content.splitlines()
        return "\n".join(lines)  # Return lines with correct indentation preserved
    return ""



class PipelineParser:
    def __init__(self, pipeline_code, pipeline_type):
        self.pipeline_code = pipeline_code
        self.pipeline_type = pipeline_type

    def parse_pipeline_code(self):
        pipeline_class_map = {
            "azure-pipelines": convert_azure_devops_to_pipeline,
            "github-actions": convert_github_actions_to_pipeline,
            "gitlab-ci": convert_gitlab_ci_to_pipeline,
            "jenkinsfile-scripted": convert_jenkins_scripted_to_pipeline,
            "jenkinsfile-declarative": convert_jenkins_declarative_to_pipeline,
            "codepipeline": convert_aws_codepipeline_to_pipeline
        }

        # Check if the pipeline_code is a string
        if isinstance(self.pipeline_code, str):
            if self.pipeline_type in ["jenkinsfile-scripted", "jenkinsfile-declarative"]:
                # Groovy-based Jenkins pipelines (clean and parse the script)
                print("Processing Jenkins pipeline...")
                cleaned_script = clean_jenkins_script(self.pipeline_code)
                convert_func = pipeline_class_map.get(self.pipeline_type)
                if not convert_func:
                    raise ValueError(f"Unsupported pipeline type for conversion: {self.pipeline_type}")
                pipeline = convert_func(cleaned_script)
            elif self.pipeline_type in ["azure-pipelines", "github-actions", "gitlab-ci"]:
                # YAML-based pipelines (parse with YAML)
                print("Processing non-Jenkins (YAML/JSON) pipeline...")
                print(f"Pipeline type: {self.pipeline_type}")
                yaml_code = extract_yaml_code(self.pipeline_code)
                print(f"Extracted YAML: {yaml_code}")

                if not yaml_code.startswith("---"):
                    yaml_code = "---\n" + yaml_code

                try:
                    print("===========================yaml_code: \n", yaml_code)
                    cleaned_code = clean_and_format_yaml(yaml_code)
                    print(f"Cleaned YAML: {cleaned_code}")  # Print cleaned YAML
                    ruamel_yaml = YAML(typ='safe')
                    ci_config = ruamel_yaml.load(cleaned_code)
                except YAMLError as e:
                    error_details = re.search(r"line (\d+), column (\d+)", str(e))
                    print(f"YAML parsing error on line {error_details.group(1)}, column {error_details.group(2)}" if error_details else f"YAML parsing error: {e}")
                    return None
                
                # Convert the parsed YAML to the respective pipeline
                convert_func = pipeline_class_map.get(self.pipeline_type)
                if not convert_func:
                    raise ValueError(f"Unsupported pipeline type for conversion: {self.pipeline_type}")
                pipeline = convert_func(ci_config)
            elif self.pipeline_type == "codepipeline":
                print("Processing AWS CodePipeline...")

                try:
                    # Detect JSON or YAML format
                    pipeline_config = None
                    if self.pipeline_code.strip().startswith("{"):
                        pipeline_config = json.loads(self.pipeline_code)
                    else:
                        yaml_code = extract_yaml_code(self.pipeline_code)
                        cleaned_code = clean_and_format_yaml(yaml_code)
                        ruamel_yaml = YAML(typ='safe')
                        pipeline_config = ruamel_yaml.load(cleaned_code)

                    if not pipeline_config:
                        raise ValueError("Invalid AWS CodePipeline configuration.")

                    print(f"Extracted AWS CodePipeline config: {pipeline_config}")

                    # Convert parsed AWS CodePipeline to internal format
                    convert_func = pipeline_class_map.get(self.pipeline_type)
                    if not convert_func:
                        raise ValueError(f"Unsupported pipeline type: {self.pipeline_type}")

                    return convert_func(pipeline_config)

                except (YAMLError, json.JSONDecodeError) as e:
                    print(f"Parsing error: {e}")
                    return None

            else:
                raise ValueError(f"Unsupported pipeline type: {self.pipeline_type}")
        else:
            raise ValueError("pipeline_code should be a string.")

        return pipeline

