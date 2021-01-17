import setuptools

with open("README.md", "r", encoding="UTF-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gf", 
    version="0.0.1",
    author="Be5yond",
    author_email="beyond147896@126.com",
    description="git-flow branch management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Be5yond/gf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=["gitpython", "typer", "prompt_toolkit"],
    python_requires='>=3.6',
    entry_points = {
        'console_scripts': ['gf = gf.main:app']
    }
)