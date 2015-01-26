from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(
    name='fluorine',
    version=version,
    description='The most reactive app.',
    author='Luis Fernandes',
    author_email='luisfmfernandes@gmail.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=("frappe",),
)
