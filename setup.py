from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="configgen",
    version="1.0.0",
    author="ConfigGen Contributors",
    author_email="configgen@example.com",
    description="Dynamic configuration file generator with templates, validation, and multi-format support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moggan1337/ConfigGen",
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pyyaml>=6.0",
        "jinja2>=3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
        ],
        "toml": [
            "tomli>=2.0",
            "tomli-w>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "configgen=configgen.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
