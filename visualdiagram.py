from diagrams import Diagram, Cluster
from diagrams.onprem.compute import Server
from diagrams.onprem.ci import Jenkins
from diagrams.onprem.vcs import Github
from diagrams.aws.devtools import Codepipeline, Codebuild, Codedeploy

from diagrams.azure.devops import Devops
from io import BytesIO
import streamlit as st
from datetime import datetime
import os
from pipelinetypes import *
import utils
from contextlib import suppress
from diagrams.custom import Custom

def generate_diagram_from_pipeline(pipeline, pipeline_type_class):
    """
    Generate a CI/CD pipeline diagram with enhanced styling and layout.
    """
    if not utils.validate_pipeline_type(pipeline, pipeline_type_class):
        return None

    try:
        parsed_stages = pipeline.stages
        if not parsed_stages:
            st.error("No stages found in the pipeline.")
            return None

        filename = f"pipeline_diagram_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        with Diagram(
            f"CI/CD Pipeline ({pipeline_type_class.__name__})",
            filename=filename,
            show=False,
            graph_attr={'rankdir': 'LR', 'nodesep': '1.2', 'bgcolor': '#F8F8F8', 'splines': 'spline'},
        ) as diag:
            source = Github("Source Code")

            if isinstance(pipeline, JenkinsPipeline):
                handle_jenkins_pipeline(source, parsed_stages)
            elif isinstance(pipeline, GitLabPipeline):
                handle_gitlab_pipeline(source, parsed_stages)
            elif isinstance(pipeline, AzureDevOpsPipeline):
                handle_azure_devops_pipeline(source, parsed_stages)
            elif isinstance(pipeline, GitHubActionsPipeline):
                handle_github_actions_pipeline(source, parsed_stages)
            elif isinstance(pipeline, AWSPipeline):
                handle_aws_codepipeline(source, parsed_stages)
            else:
                st.error("Unsupported pipeline type.")
                return None

        output_file = f"{filename}.png"
        with open(output_file, "rb") as f:
            diagram_stream = BytesIO(f.read())
        os.remove(output_file)
        return diagram_stream

    except Exception as e:
        st.error(f"Error: {e}")
        return None


def handle_jenkins_pipeline(source, stages):
    """ Enhanced layout for Jenkins pipelines. """
    with Cluster("Jenkins CI/CD Pipeline"):
        jenkins_master = Jenkins("Jenkins Master")
        source >> jenkins_master
        previous_stage_node = jenkins_master

        for stage in stages:
            with Cluster(stage.name, graph_attr={'style': 'filled', 'fillcolor': '#D6EAF8'}):
                stage_node = Server(stage.name)
                previous_stage_node >> stage_node
                previous_stage_node = stage_node


def handle_gitlab_pipeline(source, stages):
    """ Improved GitLab pipeline visualization. """
    with Cluster("GitLab CI/CD Pipeline"):
        previous_node = source
        for stage in stages:
            with Cluster(stage.name, graph_attr={'style': 'filled', 'fillcolor': '#FCF3CF'}):
                stage_node = Server(stage.name)
                previous_node >> stage_node
                previous_node = stage_node


def handle_azure_devops_pipeline(source, stages):
    """ Optimized Azure DevOps pipeline representation. """
    azure_devops = Devops("Azure DevOps")
    source >> azure_devops
    previous_stage_node = azure_devops

    for stage in stages:
        with Cluster(stage.name, graph_attr={'style': 'filled', 'fillcolor': '#F5B7B1'}):
            stage_node = Server(stage.name)
            previous_stage_node >> stage_node
            previous_stage_node = stage_node


def handle_github_actions_pipeline(source, stages):
    """ Styled GitHub Actions pipeline visualization. """
    github_actions = Github("GitHub Actions")
    source >> github_actions
    previous_stage_node = github_actions

    for stage in stages:
        with Cluster(stage.name, graph_attr={'style': 'filled', 'fillcolor': '#AED6F1'}):
            stage_node = Server(stage.name)
            previous_stage_node >> stage_node
            previous_stage_node = stage_node

def handle_aws_codepipeline(source, stages):
    """ AWS CodePipeline visualization. """
    with Cluster("AWS CodePipeline", graph_attr={'style': 'filled', 'fillcolor': '#ABEBC6'}):
            # Define the source stage
            aws_pipeline = Codepipeline("CodePipeline")
            source >> aws_pipeline
            previous_stage_node = aws_pipeline

            # Iterate over the stages and visualize each one with user-specified services
            for stage in stages:
                with Cluster(stage['name'], graph_attr={'style': 'filled', 'fillcolor': '#D5F5E3'}):
                    # Use the actual service passed in the stage dictionary
                    stage_node = stage['service'](stage['name'])
                    
                    # Connect the stages
                    previous_stage_node >> stage_node
                    previous_stage_node = stage_node






# from diagrams import Diagram, Cluster, Node
# from diagrams.onprem.compute import Server
# from diagrams.onprem.ci import Jenkins
# from diagrams.onprem.vcs import Github
# from diagrams.aws.devtools import Codepipeline, Codebuild, Codedeploy
# from diagrams.azure.devops import Devops
# from io import BytesIO
# import streamlit as st
# from datetime import datetime
# import os
# from pipelinetypes import Pipeline, JenkinsPipeline, GitLabPipeline, AzureDevOpsPipeline, GitHubActionsPipeline
# import utils
# from contextlib import suppress
# from diagrams.custom import Custom

# def generate_diagram_from_pipeline(pipeline, pipeline_type_class):
#     """
#     Generate a CI/CD pipeline diagram based on the pipeline object and display it in Streamlit.
#     Args:
#         pipeline (Pipeline): A custom Pipeline object containing stages, jobs, and pipeline type information.
#         pipeline_type_class (type): The subclass of Pipeline for type-specific handling.
#     Returns:
#         BytesIO: A stream of the rendered pipeline diagram.
#     """
#     if not utils.validate_pipeline_type(pipeline, pipeline_type_class):
#         return None

#     try:
#         parsed_stages = pipeline.stages
#         if not parsed_stages:
#             st.error("No stages found in the pipeline.")
#             return None

#         filename = f"pipeline_diagram_{datetime.now().strftime('%Y%m%d%H%M%S')}"
#         print("Pipeline Structure:")
#         print(f"Pipeline Type: {type(pipeline).__name__}")
#         print("Stages:")
#         for stage in pipeline.stages:
#             print(f"  Stage: {stage.name}")

#         with Diagram(
#             f"CI/CD Pipeline ({pipeline_type_class.__name__})",
#             filename=filename,
#             show=False,
#             graph_attr={'rankdir': 'LR', 'nodesep': '1.5', 'bgcolor': 'lightgrey', 'splines': 'true'},
#         ) as diag:
#             source = Github("Source Code")

#             # Add the source node and connect pipeline-specific stages
#             if isinstance(pipeline, JenkinsPipeline):
#                 handle_jenkins_pipeline(source, parsed_stages)
#             elif isinstance(pipeline, GitLabPipeline):
#                 handle_gitlab_pipeline(source, parsed_stages)
#             elif isinstance(pipeline, AzureDevOpsPipeline):
#                 handle_azure_devops_pipeline(source, parsed_stages)
#             elif isinstance(pipeline, GitHubActionsPipeline):
#                 handle_github_actions_pipeline(source, parsed_stages)
#             else:
#                 st.error("Unsupported pipeline type.")
#                 return None

#         output_file = f"{filename}.png"
#         with open(output_file, "rb") as f:
#             diagram_stream = BytesIO(f.read())
        
#         os.remove(output_file)
#         return diagram_stream

#     except AttributeError as e:
#         st.error(f"An AttributeError occurred: {e}")
#         return None
#     except Exception as e:
#         st.error(f"An unexpected error occurred: {e}")
#         return None

# def handle_jenkins_pipeline(source, stages):
#     """
#     Handle diagram generation for Jenkins pipelines.

#     Args:
#         source: Source node (e.g., Github).
#         stages: Parsed stages of the pipeline.
#     """
#     jenkins_master = Jenkins("Jenkins Master", style="filled", fillcolor="lightblue")
#     source >> jenkins_master
#     previous_stage_node = jenkins_master
#     for stage in stages:
#         if not hasattr(stage, "name"):
#             st.warning(f"Skipping invalid or undefined stage: {stage}")
#             continue

#         with Cluster(stage.name):
#             stage_node = Node(stage.name, style="rounded", fillcolor="lightgreen", fontcolor="black")
#             previous_stage_node >> stage_node
#             previous_stage_node = stage_node

# def handle_gitlab_pipeline(source, stages):
#     """
#     Handle diagram generation for GitLab pipelines.

#     Args:
#         source: Source node (e.g., Github).
#         stages: Parsed stages of the pipeline.
#     """
#     previous_node = source
#     for stage in stages:
#         if not hasattr(stage, "name"):
#             st.warning(f"Skipping invalid or undefined stage: {stage}")
#             continue

#         stage_node = Node(stage.name, style="rounded", fillcolor="lightyellow", fontcolor="black")
#         previous_node >> stage_node
#         previous_node = stage_node

# def handle_azure_devops_pipeline(source, stages):
#     """
#     Handle diagram generation for Azure DevOps pipelines.

#     Args:
#         source: Source node (e.g., Github).
#         stages: Parsed stages of the pipeline.
#     """
#     azure_devops = Devops("Azure DevOps", style="filled", fillcolor="lightcoral")
#     source >> azure_devops
#     previous_stage_node = azure_devops
#     for stage in stages:
#         if not hasattr(stage, "name"):
#             st.warning(f"Skipping invalid or undefined stage: {stage}")
#             continue

#         with Cluster(stage.name):
#             stage_node = Node(stage.name, style="rounded", fillcolor="lightblue", fontcolor="black")
#             previous_stage_node >> stage_node
#             previous_stage_node = stage_node

# def handle_github_actions_pipeline(source, stages):
#     """
#     Handle diagram generation for GitHub Actions pipelines.

#     Args:
#         source: Source node (e.g., Github).
#         stages: Parsed stages of the pipeline.
#     """
#     github_actions = Github("GitHub Actions")
#     source >> github_actions
#     previous_stage_node = github_actions
#     for stage in stages:
#         if not hasattr(stage, "name"):
#             st.warning(f"Skipping invalid or undefined stage: {stage}")
#             continue

#         with Cluster(stage.name):
#             stage_node = Node(stage.name)
#             previous_stage_node >> stage_node
#             previous_stage_node = stage_node
#             # Commented out the code for jobs
#             # for job in getattr(stage, "jobs", []):
#             #     if not hasattr(job, "name"):
#             #         st.warning(f"Skipping invalid or undefined job: {job}")
#             #         continue
#             #     job_node = Node(job.name)
#             #     stage_node >> job_node






# import plotly.graph_objects as go
# import networkx as nx
# from datetime import datetime
# import streamlit as st
# from io import BytesIO
# import os

# def generate_diagram_from_pipeline(pipeline, pipeline_type_class):
#     """
#     Generate a CI/CD pipeline diagram based on the pipeline object and display it in Streamlit.
#     Args:
#         pipeline: A custom pipeline object containing stages, jobs, and pipeline type information.
#         pipeline_type_class: The subclass of Pipeline for type-specific handling.
#     Returns:
#         BytesIO: A stream of the rendered pipeline diagram.
#     """
#     try:
#         # Validate pipeline data
#         if not hasattr(pipeline, "stages") or not pipeline.stages:
#             st.error("No stages found in the pipeline.")
#             return None

#         # Initialize directed graph
#         G = nx.DiGraph()

#         # Add source node
#         source_node = "Source Code"
#         G.add_node(source_node)

#         # Add pipeline stages as nodes and connect them
#         previous_node = source_node
#         for stage in pipeline.stages:
#             if not hasattr(stage, "name"):
#                 st.warning(f"Skipping invalid or undefined stage: {stage}")
#                 continue

#             G.add_node(stage.name)
#             G.add_edge(previous_node, stage.name)
#             previous_node = stage.name

#         # Compute positions using a layout algorithm
#         pos = nx.spring_layout(G, seed=42)  # Assign positions to nodes
#         for node, position in pos.items():
#             G.nodes[node]["pos"] = position

#         # Extract edge positions for Plotly
#         edge_x = []
#         edge_y = []
#         for edge in G.edges():
#             x0, y0 = G.nodes[edge[0]]["pos"]
#             x1, y1 = G.nodes[edge[1]]["pos"]
#             edge_x.extend([x0, x1, None])
#             edge_y.extend([y0, y1, None])

#         # Extract node positions and labels for Plotly
#         node_x = [pos[node][0] for node in G.nodes()]
#         node_y = [pos[node][1] for node in G.nodes()]
#         node_labels = list(G.nodes())

#         # Create Plotly figure
#         fig = go.Figure()

#         # Add edges
#         fig.add_trace(go.Scatter(
#             x=edge_x,
#             y=edge_y,
#             line=dict(width=2, color="gray"),
#             mode="lines",
#             hoverinfo="none"
#         ))

#         # Add nodes
#         fig.add_trace(go.Scatter(
#             x=node_x,
#             y=node_y,
#             mode="markers+text",
#             text=node_labels,
#             textposition="top center",
#             marker=dict(
#                 size=20,
#                 color="skyblue",
#                 line=dict(width=2, color="darkblue")
#             ),
#             hoverinfo="text"
#         ))

#         # Update layout
#         fig.update_layout(
#             title=f"CI/CD Pipeline Diagram ({pipeline_type_class.__name__})",
#             title_x=0.5,
#             showlegend=False,
#             plot_bgcolor="white",
#             xaxis=dict(showgrid=False, zeroline=False),
#             yaxis=dict(showgrid=False, zeroline=False)
#         )

#         # Save figure as image and return as stream
#         output_file = f"pipeline_diagram_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
#         fig.write_image(output_file)

#         with open(output_file, "rb") as f:
#             diagram_stream = BytesIO(f.read())

#         os.remove(output_file)
#         return diagram_stream

#     except KeyError as e:
#         st.error(f"KeyError occurred: {e}. Please check your pipeline data.")
#         return None
#     except Exception as e:
#         st.error(f"An unexpected error occurred: {e}")
#         return None






