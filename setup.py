from setuptools import setup, find_packages

setup(
    name="noetide",
    version="0.1.0",
    description="Local-first Personal Context & Growth Engine",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Noetide Project",
    python_requires=">=3.12",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    entry_points={
        "console_scripts": [
            "noetide=noetide_micro.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Scheduling",
    ],
    include_package_data=True,
    package_data={
        "noetide_micro": ["schema.sql"],
    },
)
