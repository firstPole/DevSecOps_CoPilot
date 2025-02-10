# pipeline_patterns.py

PIPELINE_TYPE_PATTERNS = {
    "azure-pipelines": {
        "keywords": ["trigger", "stages", "pool", "jobs"],
        "file_extension": ".yaml",
        "language": "yaml"
    },
    "gitlab-ci": {
        "keywords": ["stages", "jobs", "gitlab"],
        "file_extension": ".yaml",
        "language": "yaml"
    },
    "github-actions": {
        "keywords": ["jobs", "runs-on", "steps"],
        "file_extension": ".yaml",
        "language": "yaml"
    },
    "jenkinsfile-scripted": {
        "keywords": ["pipeline", "agent", "stages"],
        "file_extension": ".groovy",
        "language": "groovy"
    },
    "jenkinsfile-declarative": {
        "keywords": ["pipeline", "stages", "agent"],
        "file_extension": ".groovy",
        "language": "groovy"
    },
    "bamboo": {
        "keywords": ["plan", "stages"],
        "file_extension": ".yaml",
        "language": "yaml"
    },
    "circleci": {
        "keywords": ["workflows", "jobs"],
        "file_extension": ".yaml",
        "language": "yaml"
    },
    "codepipeline": {
        "keywords": ["aws", "codepipeline"],
        "file_extension": ".yaml",
        "language": "yaml"
    }
}
