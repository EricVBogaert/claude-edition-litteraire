# setup.py
from setuptools import setup, find_packages

setup(
    name="claude_edition_litteraire",
    version="0.1.0",
    description="Bibliothèque pour l'édition littéraire assistée par Claude",
    author="Eric Van Bogaert et al.",
    author_email="contact@example.com",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.28.0",
        "colorama>=0.4.4",
        "tqdm>=4.64.0",
        "rich>=12.0.0",
    ],
    extras_require={
        "cli": ["click>=8.0.0"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "isort>=5.10.0"]
    },
    entry_points={
        "console_scripts": [
            "claude-lit=claude_edition_litteraire.cli.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)