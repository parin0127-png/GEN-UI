from setuptools import setup, find_packages

setup(
    name="genui-ai",
    version="1.0.2",
    author="Parin",
    author_email="parin122007@gmail.com",
    description="AI-powered UI generator that creates production-grade HTML/CSS/JS from a single prompt",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/parin0127-png/GEN-UI",
    packages=find_packages(),
    install_requires=[
        "openai",
        "requests",
        "python-dotenv",
        "rich",
        "beautifulsoup4",
        "ddgs",
    ],
    entry_points={
        "console_scripts": [
            "genui=genui.UI:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)

