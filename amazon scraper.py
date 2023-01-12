from selenium import webdriver
from selenium.webdriver.common.by import By
import mysql.connector
class database_handler:
    def __init__(self):
        self.host=""
        self.username=""
        self.password=""
        self.connection=""
        self.cursor=""
        self.database="amazon_database"
        self.authenticate()
        
    def authenticate(self):
        authentication=False
        print("You need to get connected with database before procceding: ")
        while not authentication:
            self.host=input("Enter the host: ")
            self.username=input("Enter the username: ")
            self.password=input("Enter the password: ")
            try:
                self.connection=mysql.connector.connect(
                host=self.host,
                username=self.username,
                passwd=self.password)
                authentication=True
                self.cursor=self.connection.cursor()
            except:
                print("Authentication Failed. Please try again.")
        print("Successfully Authenticated")
        self.get_database()
    def get_database(self):
        self.cursor.execute("SHOW DATABASES")
        db_found=False
        for db in self.cursor:
            if db[0]==self.database:
                db_found=True
                print("Database exists")
        if not db_found:
            self.cursor.execute("CREATE DATABASE "+self.database)
            print("Database created")
            
        #connecting to database   
        self.connection=mysql.connector.connect(
                host=self.host,
                username=self.username,
                passwd=self.password,
                database=self.database)
        self.cursor=self.connection.cursor()
        print("Successfully connected to the database.")

    def store_data(self,table,data_list):
        table=table.strip().replace("&","").replace("  "," ").replace(" ","_").lower()
        self.cursor.execute("SHOW TABLES")
        table_found=False
        for tbl in self.cursor:
            if tbl[0]== table:
                table_found=True
                print("Table exists.")
        if not table_found:
            self.cursor.execute("CREATE TABLE {} (id int NOT NULL AUTO_INCREMENT, name VARCHAR(255), url VARCHAR(255), price VARCHAR(255), PRIMARY KEY (id))".format(table))
            print("Table successfully created.")
        print("Table successfully selected.")

        #fetching data from the existing table
        self.cursor.execute("SELECT name, url, price FROM "+table)
        table_data=[]
        for data in self.cursor:
            table_data.append(data)

        #writing the data
        c=0
        command="INSERT INTO {} (name, url, price) VALUES (%s, %s, %s)".format(table)
        for data in data_list:
            if data not in table_data:
                self.cursor.execute(command,data)
                c+=1
        print(f'{c} data were stored in the table.')
        self.connection.commit()

        
class amazonscrapper:
    #initiating the object
    def __init__(self):
        self.url=""
        self.list_dict={}
        self.choices_dict={}
        self.selected_item=""
        self.driver=webdriver.Chrome()
        self.driver.maximize_window()
        self.handler=database_handler()
        self.show_help()
        self.get_list()
            

        
    #method to get the url of each categories
    def get_category(self):
        self.url="https://www.amazon.in"
        self.list_dict={'Clothing & Accessories':'https://www.amazon.in/s?bbn=1571271031&rh=n%3A1571271031&dc&qid=1666368004&ref=lp_1953602031_ex_n_1'}
        self.driver.get(self.url)
        _list=self.driver.find_elements(By.CSS_SELECTOR,"a.nav-a  ")
        category_list=['Electronics', 'Books','Home & Kitchen','Computers','Mobiles']
        for element in _list:
            text=element.text
            if text in category_list:
                link=element.get_attribute("href")
                self.list_dict[text]=link
        self.show_choices()

    #method to show choices
    def show_choices(self):
        index=1
        self.choices_dict={}
        for key in self.list_dict:
            self.choices_dict[index]=key
            print(f'{index}. {key}')
            index+=1
        self.get_input()



    #method to get input
    def get_input(self):
        user_in=""
        while user_in=="":
            user_in=input("Enter a command: ").lower().strip()
            try:
                iindex=int(user_in)
                self.selected_item=self.choices_dict[iindex]
                self.url=self.list_dict[self.selected_item]
                print("-"*25+"\n"+self.selected_item+"\n"+"-"*25)
            except:
                if user_in=="stop":
                    self.close_browser()
                elif user_in=="start":
                    self.get_category()
                elif user_in=="help":
                    self.show_help()

    #method to save data
    def save_data(self):
        confirm=""
        while confirm !="y":
            confirm=input("Do you want to store the selected category items? (Y/N): ").lower()
            if confirm=="n": return
        n=int(input("Enter the no of items that you want to store: "))
        self.driver.find_element(By.CSS_SELECTOR,"span.a-size-medium.a-color-link.a-text-bold").click()
        items_info=[]
        item_count=0
        while item_count<n:
            items_list=self.driver.find_elements(By.CSS_SELECTOR,"div.s-card-container.s-overflow-hidden.aok-relative.puis-expand-height.puis-include-content-margin.puis.s-latency-cf-section.s-card-border")
            for item in items_list:
                _item=item.find_element(By.CSS_SELECTOR,"a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal")
                link=_item.get_attribute("href").split("?")[0]
                name=_item.text.replace("("," ").replace(")"," ").replace("  "," ").replace('"'," inch")
                try:
                    price=item.find_element(By.CSS_SELECTOR,"span.a-offscreen").get_attribute("innerHTML")
                except:
                    price="None"
                items_info.append((name,link,price))
                item_count+=1
                if item_count==n:
                    break
            if item_count==n:
              break
            try:
                next_page=self.driver.find_element(By.CSS_SELECTOR,"a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator").get_attribute("href")
                self.driver.get(next_page)
            except:
                break
            
        print(f"{item_count} data collected.")
        self.handler.store_data(self.selected_item,items_info)
              
            
            
                

    #method to close driver
    def close_browser(self):
        self.driver.quit()
        quit()

    #method to show help
    def show_help(self):
        lines=["","Read the help instructions carefully.",
               "This will make you able to use this program.",
               "Enter the number to select list item.",
               "The commands with usages are given below:",
               "\tstart - this command will take you to start",
               "\tstop  - this command will exit the program",
               "\thelp  - this command will print help instructions","",""]
        for line in lines:
            print(line)
        self.get_input()

    #method to get the url of list
    def get_list(self):
        self.driver.get(self.url)
        self.list_dict={}
        _list=self.driver.find_elements(By.CSS_SELECTOR,"ul.a-unordered-list.a-nostyle.a-vertical.a-spacing-medium a.a-color-base.a-link-normal")
        item_count=0
        for element in _list:
            item_count+=1
            text=element.text
            link=element.get_attribute("href")
            child_count=len(element.find_elements(By.TAG_NAME,"span"))
            if child_count==2:
                text+=" [UPPER_LEVEL]"
                item_count-=1
            self.list_dict[text]=link
        if item_count==0:
            self.save_data()
        self.show_choices()
        self.get_list()

    

    
#------------------------------------------------
amazon= amazonscrapper()


