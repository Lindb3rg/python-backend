from setuptools import setup, find_packages

setup(
    name="python-backend-app",
    version="0.0.1",
    description="A simple FastAPI backend handling products and orders",
    packages=find_packages(include=['app', 'app.*']),
    package_data={'': ['db/schema/schema.sql']},
    include_package_data=True,
    
    # Core runtime dependencies
    install_requires=[
        "fastapi>=0.116.0,<1.0",
        "uvicorn>=0.35.0",
        "sqlalchemy>=2.0.0,<3.0", 
        "sqlmodel>=0.0.24",
        "pydantic>=2.11.0,<3.0",
        "python-dotenv>=1.0.0",
    ],
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=8.0",
            "black",
            "flake8",
            "selenium>=4.35.0",
            "httpx>=0.28.0",
        ],
        "monitoring": [
            "sentry-sdk>=2.33.0",
        ]
    },
    
    python_requires=">=3.8",
)