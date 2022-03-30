import selenium
import time
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
import uuid
import json
import pandas as pd
import os 
import urllib.request
import boto3
import sqlalchemy
from sqlalchemy import create_engine, false
import tempfile
import shutil
from tqdm import tqdm
import yaml




class GorillaMindScraper:
    '''
    This class is a scraper which can be used to browse different websites and collect the deatils of each product on that site. 
    Parameters
    ---------- 
    url: str
        The link we would like to visit.
    Attribute
    --------- 
    driver:
        This is a webdriver object.
    '''
    def __init__(self, url: str = 'https://gorillamind.com/collections/all-products'):
        options = Options()
        options.add_argument('--headless')
        self.driver = Firefox(options=options)
        self.driver.get(url)
        self.key_id = input('Enter your AWS key id: ')
        self.secret_key = input('Enter your AWS secret key: ')
        self.bucket_name = input('Enter your bucket name: ')
        self.region = input('Enter your region: ')
        self.client = boto3.client(
            's3',
            aws_access_key_id=self.key_id,
            aws_secret_access_key=self.secret_key,
            region_name=self.region
        )
    
    def close_popup(self, xpath: str = '//button[@class= "sc-75msgg-0 boAhRx close-button cw-close"]'):
        '''
        This method waits for the popup to appear and then closes it by clicking the button.
        Parameters
        ----------
        xpath: str
            The xpath of the close popup button.   
        '''
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located ((By.XPATH, xpath)))
            self.driver.find_element(By.XPATH , xpath).click()
        except TimeoutException:
            print("No pop up present")

    def find_container(self):
        '''
        This method locates the contianer where all the products are listed. 
        It then iterates through each product link and appends the link to each product into a list.
        Parameters
        ----------
        xpath: str
            The xpath to the container holding each product.
            The xpath to iterate through the container to get each product.
        Returns
        -------
        list
            a list of links to each product. 
        '''
        self.container = self.driver.find_element(By.XPATH, '//div[@class="container collection-matrix"]')
        self.products = self.container.find_elements(By. XPATH, './div')
        prod_list = []
        for items in tqdm(self.products):
            prod_list.append(items.find_element(By.TAG_NAME, 'a').get_attribute('href'))
        return prod_list
    
    def create_store(self, folder):
        '''
        Makes a folder within the raw_data folder.
        '''
        if not os.path.exists(folder):
            os.makedirs(folder)
    
    def data_dump(self, folder_name, data):
        '''
        This method dumps all the collected data for each product into a sperate folder created by it id.
        Paramters
        ---------
        folder_name :str   
        Data:
            Dictionary containing all the infromation about each product.
        '''
        with open(f"raw_data/{folder_name}/{folder_name}data.json", "w") as f:
            json.dump(data, f)   
    
    def product_details(self, Product_list):
        '''
        Iterates through every product and creates a new folder with the product id as the name. It then continues collecting every value for that product and placing it in the data dictionary.
        The infromation in the data dictionary is then dumped for that product and the process repeats. 
        Paramters
        ---------
        Product_list:
            A list containing the link to go to each product.
        Attribute
        --------- 
        driver:
            This is a webdriver object.
        Returns
        -------
        Folder:
            A folder is created for each product with the id as the name of the folder under the folder raw_data.
        Data:
            A dictionary containing all the information about the product is then dumped into the folder with its id as the name.
        Product_image: img 
            An image of the product is taken and stored in the folder correspondding to its id under raw_data.
        screenshot:
            A screenshot of the nutritional information page is taken and stored in the folder corresponding to its id under raw_data. 
        '''
        dataframe_products = pd.DataFrame()
        for products in tqdm(Product_list):
            data = { 
                "id": '',
                "UUID": '',
                "Product_Link": '',
                "Product_Name": '',
                "Price": '', 
                "No_of_servings": '', 
                "Flavours": [], 
                "Size": [], 
                "Nutritional_info": '',
                "No_of_Reviews": '',
                "Product_image": ''
            }
            self.driver.get(products)
            data['id'] = products.split("/")[-1]
            if self._check_item_in_db(data['id']):
                continue
            else: 
                folder_name = data['id']
                self.create_store(f'raw_data/{folder_name}')
                data['UUID'] = str (uuid.uuid4())
                image_name1 = data['UUID']
                data['Product_Link'] = products
                time.sleep(2)
                try:
                    product_name = self.driver.find_element(By.XPATH, '//h1[@class="product_name title"]').text
                    data['Product_Name'] = product_name
                except NoSuchElementException:
                    data['Product_Name'] = None
                try:
                    price = self.driver.find_element(By.XPATH, '//p[@class="modal_price subtitle"]').text
                    data['Price'] = price
                except NoSuchElementException:
                    data['Price'] = None
                try:
                    no_of_servings = self.driver.find_element(By.XPATH, '//span[@class= "variant-size"]').text
                    data['No_of_servings'] = no_of_servings
                except NoSuchElementException:
                    data['No_of_servings'] = None
                try:
                    all_flavours = self.driver.find_element(By.XPATH, '//div[@data-option-index="0"]')
                    flavour_list = all_flavours.find_elements(By.XPATH, './div')
                    flavour_list = [flavour.text for flavour in flavour_list[1:]]
                    data['Flavours'].append(flavour_list)
                except NoSuchElementException:
                    data['Flavours'].append(None)
                try:
                    all_sizes = self.driver.find_element(By.XPATH, '//div[@data-option-index="1"]')
                    size_list = all_sizes.find_elements(By.XPATH, './div')
                    size_list = [size.text for size in size_list[1:]]
                    data['Size'].append(size_list)
                except NoSuchElementException:
                    data['Size'].append(None)
                try:
                    no_of_reviews = self.driver.find_element(By.XPATH, '//a[@class="text-m"]').text
                    data['No_of_Reviews'] = no_of_reviews
                except NoSuchElementException:
                    data['No_of_Reviews'] = None
                try:
                    product_image = self.driver.find_element(By.XPATH, '//img[@class="lazyload--fade-in lazyautosizes lazyloaded"]').get_attribute('src')
                    data['Product_image'] = image_name1
                    urllib.request.urlretrieve(product_image, f"raw_data/{folder_name}/{folder_name}.jpg")
                    self._download_images('jpg', product_image, folder_name)   
                except NoSuchElementException:
                    data['Product_image'] = None
                try:
                    nutritional_informaion = self.driver.find_element(By.XPATH, '//iframe[@title="Nutrition or Supplement Facts Label"]').get_attribute('src')
                    data['Nutritional_info'] = image_name1
                    self.driver.get(nutritional_informaion)
                    self._download_nutritional_info('jpg', folder_name)
                    self.driver.save_screenshot(f"raw_data/{folder_name}/{folder_name}nutritional_info.png")
                    self.driver.back()
                except NoSuchElementException:
                    data['Nutritional_info'] = None
                self.data_dump(folder_name, data)
                time.sleep(2)
                self._upload_json_to_s3(data, self.bucket_name, f'{folder_name}/{folder_name}')
                # self._upload_raw_data('raw_data', self.bucket_name)
                time.sleep(2)
                dataframe_products = dataframe_products.append(data, ignore_index=True) 
        return dataframe_products

    def _download_images(self,  format, product_image, folder_name):
        '''
        Downloads image for the particular product.
        Parameters
        ----------
        Link: str
            Link for the image to be saved in a temp directory.
        Returns
        --------
        

        '''
        with tempfile.TemporaryDirectory() as temp_dir:
            urllib.request.urlretrieve(product_image, f"{temp_dir}/{folder_name}.{format}")
            self.client.upload_file(f'{temp_dir}/{folder_name}.{format}', self.bucket_name, f'{folder_name}/{folder_name}.{format}')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return

    def _download_nutritional_info(self, format, folder_name):
        with tempfile.TemporaryDirectory() as temp_dir:
            self.driver.get_screenshot_as_file(f"{temp_dir}/{folder_name}.{format}")
            self.client.upload_file(f'{temp_dir}/{folder_name}.{format}', self.bucket_name, f'{folder_name}/{folder_name}nutritional_info.{format}')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
   
    def _upload_json_to_s3(self, record_to_upload, bucketname, s3_file_name):
        self.client.put_object(Bucket=self.bucket_name, Key=s3_file_name, Body=json.dumps(record_to_upload))
        return

    def _upload_raw_data(self, path, bucketname):
        for root,dirs,files in os.walk(path):
            for file in files:
                self.client.upload_file(os.path.join(root,file),bucketname,file)
        return True


    def _create_engine(self,  creds: str='scraper/config/RDS_creds.yaml'):
        with open(creds, 'r') as f:
            creds = yaml.safe_load(f)
        DATABASE_TYPE = creds['DATABASE_TYPE']
        DBAPI = creds['DBAPI']
        ENDPOINT = creds['HOST']
        USER = creds['USER']
        PASSWORD = creds['PASSWORD']
        DATABASE = creds['DATABASE']
        PORT = creds['PORT']
        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        return engine 


    def _send_dataframe_to_rds(self, dataframe):
        '''
        The dataframe created from the previous method is then converted to SQL.
        '''
        engine = self._create_engine()
        dataframe.to_sql('Every_item', con=engine, if_exists='append', index=false)
        return      

    def _data_process(self):
        '''
        The dataframe is uploaded to the RDS
        '''
        self._send_dataframe_to_rds(dataframe_products)
        return   

    def _check_item_in_db(self, element_to_check):
        '''
        Checks the list of items in the dataframe so that repeats are not rescraped. 
        '''
        engine = self._create_engine()
        dataframe_products = pd.read_sql('Every_item',engine)
        if element_to_check in dataframe_products['id'].values:
            print("Item in database")
            return True
        else:
            print("Item not in database")
            return False


if __name__ == '__main__':
    bot = GorillaMindScraper()
    bot.close_popup()
    Product_list = bot.find_container()
    dataframe_products = bot.product_details(Product_list)
    bot._data_process()



    