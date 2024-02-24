from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def parse_requirements(filename):
    with open(filename) as f:
        lines = f.read().splitlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith("#")]

setup(
    name='SimpleBotClient',
    version='1.0',
    author='Eric Pan',
    author_email='hello@jointhebread.army',
    description='A lightweight bare minimum API wrapper for Discord\'s v10 API made in Python3.',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/crumb-bots/discord-bot-client',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
