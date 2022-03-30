# gorilla-_mind_webscraper

# Selenium

Selenium is an open web-based automation tool which can be used with Python language for testing.

# WebDriver_manager

WebDriverManager automates the browser setup in the Selenium code and is used to import Chrome driver manager. 

# Milestone 2

A scraper class has been built which navigates through the Gorilla mind website by first closing any popups that appear and then it locates the container to where all the products are stored. Through this container it iterates through the child's div tags to get the list of links to each product on that website. 

# Milestone 3 

The scraper then collects all the URL links to each product and iterates through them, one by one. While iterating through it extracts information about each product and then stores the information into a dictionary. A folder is then created for each product dictionary created with the unique ID being the title of each folder. This folder will contain all the product information as well as two images (product image, nutritional information)  

# Milestone 4

The code for the scraper has been refracted and optimised by removing unnecessary nested loops and other time and space complexities. Doc strings were added to each function and unit testing and integration testing was done on every public method present within the code.

# Milestone 5

The raw_folder was uploaded to the s3 bucket by using boto3 with each unique ID being the name of the folder for each set of items on the s3 bucket. All the tabular data obtained was put into a pandas data frame and then uploaded to AWS through an RDS extension on VScode. The tabular data was linked to the images for that product by the UUID assigned to each data entry. The tabular data was stored in and RDS database and the images where uploaded to the s3 bucket on AWS.

# Milestone 6

Further re-scraping was done to ensure that the scraper could work for a long duration of time. further unittests where done to ensure that the scraper worked without complications. Methods for preventing it re-scraping the same data was implemented by using the unique ID for each data entry and methods for preventing it uploading the same images was also done by leveraging the UUID of each image. 

# Milestone 7

The scraper was updated to run in headless mode and then a docker image was made for this new verion of the scraper. Issues with chromedriver on the new M1 chip mac, made it so that gecko driver and Firefox have been used to replace chromedriver and chrome. The image was pushed to docker, then pulled into an EC2 instance. It ran within the EC2 instance without issues. The credentials now enter the scraper through a separate file to build the engine, so it remains private. 

# Milestone 8

Set up Prometheus to monitor the docker container that runs the gorilla_scraper. Grafana is used to measure the metrics of the container.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install selenium.

```zsh
pip install selenium
pip install webdriver_manger
pip install pandas 
```

## Usage

```python
import selenium
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import uuid
import json
import os 
import urllib.request
import boto3
import sqlalchemy
from sqlalchemy import create_engine, false
import tempfile
import shutil
from tqdm import tqdm
import yaml

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)