from setuptools import setup, find_packages

requires = ["termcolor"]

setup(name="easylist",
      version="0.0.1",
      description="",
      classifiers=[
        "Programming Language :: Python",
        ],
      packages = find_packages(),
      #author='James Shuttleworth',
      license="GPLv2",
      install_requires = requires,
)

