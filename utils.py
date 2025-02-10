# utils.py

import streamlit as st

def validate_pipeline_type(pipeline, pipeline_type_class):
    """
    Validate if the pipeline object is an instance of the expected pipeline type.

    Args:
        pipeline: The pipeline object to check.
        pipeline_type_class: The expected pipeline class.

    Returns:
        bool: True if the pipeline object matches the expected type, False otherwise.
    """
    if not isinstance(pipeline, pipeline_type_class):
        st.error(f"The provided pipeline object does not match the expected type. "
                 f"Expected: {pipeline_type_class}, Got: {type(pipeline)}")
        return False
    return True
