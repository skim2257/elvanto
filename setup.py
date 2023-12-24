from setuptools import setup

with open("requirements.txt", "r", encoding="ascii") as fh:
    reqs = fh.read()

setup(
   name='elvanto',
   version='1.0',
   description='Elvanto API parsing for C3 Projects',
   author='Sejin Kim',
   packages=['elvanto'],  #same as name
   install_requires=reqs, #external packages as dependencies
   python_requires='>=3.10'
)