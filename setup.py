from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='adwatch',
    version='1.0.0',
    url='https://github.com/cramja/craigslist',
    description="A webapp for watching classified ads",
    long_description = long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'beautifulsoup4',
        'humanize',
        'humanize-Flask'
    ],
    classifiers=["Framework :: Flask",
                 "Programming Language :: Python :: 3.6",
                 "Topic :: Internet :: WWW/HTTP :: Dynamic Content"],
)