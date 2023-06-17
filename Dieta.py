import time
import os, re, sys
import sqlite3
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QTableWidgetItem
from PyQt5 import uic


app_path = 'C:\\FoodApp\\'
DB = app_path+'DB.db'
website = 'http://www.goleango.com/%D7%9E%D7%97%D7%A9%D7%91%D7%95%D7%9F%20%D7%A7%D7%9C%D7%95%D7%A8%D7%99%D7%95%D7%AA.php'
product = ' ביצה קשה'

## Disable Notifications and Logs
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--start-maximized")
# chrome_options.add_argument("--headless")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()),
#                                 options=chrome_options)

# Create DB
def create_tables():
    """
    Create the app DB
    """
    db_connect = sqlite3.connect(DB)
    cursor = db_connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS products (
                        name TEXT NOT NULL,
                        calories REAL,
                        protein REAL,
                        carbs REAL,
                        fat REAL,
                        cholesterol REAL,
                        fibers REAL
                    )""")

    cursor.close()
    db_connect.close()

# Insert into DB
def insert_info(product: dict):
    """
    This function insert info to DB
    """
    db_connect = sqlite3.connect(DB)
    cursor = db_connect.cursor()

    cursor.execute("INSERT INTO products VALUES (:name, :calories, :protein, :carbs, :fat, "
                                                    " :cholesterol, :fibers)",
                            {'name': product['name'],
                            'calories': product['calories'],
                            'protein': product['protein'],
                            'carbs': product['carbs'],
                            'fat': product['fat'],
                            'cholesterol': product['cholesterol'],
                            'fibers': product['fibers']
                            })
    db_connect.commit()
    cursor.close()
    db_connect.close()

# Fetch from DB
def fetch_info(product: dict):
    """
    This function fetch info from db table\n        
    to fetch all set product='all'
    """
    db_connect = sqlite3.connect(DB)
    cursor = db_connect.cursor()

    if product['name'] == 'all':
        cursor.execute("SELECT * FROM products")
        result = cursor.fetchall()

    else:
        cursor.execute("SELECT * FROM products WHERE name=:name",
                        {'name': product['name']
                            })
        result = cursor.fetchone()

    cursor.close()
    db_connect.close()

    return result

# Update DB
def update_info(product: dict):
    """
    This function update info in the DB
    """
    db_connect = sqlite3.connect(DB)
    cursor = db_connect.cursor()

    cursor.execute("""UPDATE products SET 
                        calories = :calories,
                        protein = :protein,
                        carbs = :carbs,
                        fat = :fat,
                        cholesterol = :cholesterol,
                        fibers = :fibers
                        WHERE name = :name""",
                            {'name': product['name'],
                            'calories': product['calories'],
                            'protein': product['protein'],
                            'carbs': product['carbs'],
                            'fat': product['fat'],
                            'cholesterol': product['cholesterol'],
                            'fibers': product['fibers']
                            })
    db_connect.commit()
    cursor.close()
    db_connect.close()

# Delete from DB
def delete_info(product: dict):
    """
    This function delete query from DB\n
    to delete all set product='all'
    """
    db_connect = sqlite3.connect(DB)
    cursor = db_connect.cursor()

    if product['name'] == 'all':
        cursor.execute("DELETE FROM products")

    else:
        cursor.execute("""DELETE FROM products WHERE name=:name""",
                               {'name': product['name']
                                })
    db_connect.commit()
    cursor.close()
    db_connect.close()

# Save and Diplay information on the product
def display_info(product: str, product_info: list):
    product_dict = {'name': product,
                    'calories': product_info[0],
                    'protein': product_info[1],
                    'carbs': product_info[2],
                    'fat': product_info[3],
                    'cholesterol': product_info[4],
                    'fibers': product_info[5]
                    }
    insert_info(product=product)
    return product_dict

# Decide which product to choose from dropdown
def decide_on_product(products: list):
    product_selected = False
    while product_selected == False:
        product_name = input('Enter product: ')
        if product_name in products:
            product_selected = True
            return product_name
        else:
            print('Choose product from the list or Add a new product')

# Search for a product
def search(driver, product: str):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'animated-autocomplete-input')))

    except Exception as e:
        print(e)
        quit(driver)
    else:
        search_bar = driver.find_element(by=By.CLASS_NAME, value='animated-autocomplete-input')
        search_bar.send_keys(product)
        try:
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'autocomplete-matched-item')))

            res = driver.find_elements(by=By.CLASS_NAME, value='autocomplete-matched-item')

            if len(res) != 1:
                products = []
                for elem in res:
                    products.append(elem.text)
                product = decide_on_product(products)

        except Exception as e:
            print(e)
            quit(driver)

        else:
            search_bar.send_keys(product)
            time.sleep(0.5)
            search_bar.send_keys(Keys.ENTER)

            run = True
            while(run):
                try:
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//*[@id="calculator_buttons"]/div[1]')))
                    info_btn = driver.find_element(by=By.XPATH, value='//*[@id="calculator_buttons"]/div[1]')
                    info_btn.click()

                except Exception as e:
                    pass

                else:
                    run = False
                    try:
                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.ID, 'nc_main_panel')))
                        table_info = driver.find_element(by=By.ID, value='nc_main_panel')

                        table_text = re.split(r'\n', table_info.text)[-12:]
                        product_info = [' '.join(table_text[i:i+2]) for i in range(0, len(table_text), 2)]
                        display_info(product=product, product_info=product_info)

                    except Exception as e:
                        pass
                        # print(e)
                        # quit(driver)
    return

# Open ChromeDriver
def open_chrome(driver):
    driver.get(website)
    return

def create_folder():
    os.makedirs(name=app_path, exist_ok=True)  # succeeds even if directory exists.

# # Create App folder
# create_folder()

# # Create DB
# create_tables()

# # Open Chrome Webdriver
# open_chrome(driver)

# ## Search the product and display results
# search(driver, product)


def restart():
    MainWindow.singleton = MainWindow()

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.setWindowTitle('Foodie')
        self.setWindowIcon(QtGui.QIcon('icon.png'))

        self.tableWidget.setRowCount(10)
        product_dict = {'name': 'ביצה קשה',
                        'calories': str(176),
                        'protein': str(180),
                        'carbs': str(40),
                        'fat': str(0.5),
                        'cholesterol': str(10),
                        'fibers': str(27)
                        }
        for key in product_dict.keys():
            # name
            self.tableWidget.setItem(0, 0, QTableWidgetItem(product_dict['name']))
            # quantity
            self.tableWidget.setItem(0, 1, QTableWidgetItem(str(100)))
            # calories
            self.tableWidget.setItem(0, 2, QTableWidgetItem(product_dict['calories']))
            # protein
            self.tableWidget.setItem(0, 3, QTableWidgetItem(product_dict['protein']))
            # carbs
            self.tableWidget.setItem(0, 4, QTableWidgetItem(product_dict['carbs']))
            # fat
            self.tableWidget.setItem(0, 5, QTableWidgetItem(product_dict['fat']))
            # cholesterol
            self.tableWidget.setItem(0, 6, QTableWidgetItem(product_dict['cholesterol']))
            # fibers
            self.tableWidget.setItem(0, 7, QTableWidgetItem(product_dict['fibers']))

        self.show()

    def restart(self):
        self.close()
        restart()

    def export_data(self):
        df = pd.DataFrame({
            "tag": tags,
            "author": authors,
            "profile": profiles,
            "comment": comments,
        })

        df.drop_duplicates(subset="comment", keep="first", inplace=True)
        file_name = 'BritneyComments.csv'
        df.to_csv(file_name, encoding='utf-8-sig')
        self.ui.information_lbl.setText(
            f'קובץ התגובות - {file_name.replace(".csv","")} - נוצר בתיקייה')


    def pop(self):
        self.show()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
# window.pop()
sys.exit(app.exec_())
