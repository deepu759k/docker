import boto3
import mysql.connector
import json
import logging
import time

from config import ENVIRON, SECRETMANAGERKEY
class Utils:
    # static class containing helpful functions 
    
    @staticmethod
    def connect_to_db():
        '''
        returns both database connections in a tuple --> shopify, template
        '''

        client = boto3.client('secretsmanager','us-east-1')
        response = client.get_secret_value(SecretId=f'shopify-{ENVIRON}')
        print("environ-----", ENVIRON)

        database_secrets = json.loads(response['SecretString'])
        print("environ-----", ENVIRON)
        shopify = mysql.connector.connect(
                    host= database_secrets[SECRETMANAGERKEY]['dbServer'], # asldkfj@aws
                    user= database_secrets[SECRETMANAGERKEY]['username'], # secretuser
                    password= database_secrets[SECRETMANAGERKEY]['password'], # secretuserpass
                    database= database_secrets[SECRETMANAGERKEY]['dbName']  # shopify
                )
        
        template = mysql.connector.connect(
                    host= database_secrets[SECRETMANAGERKEY]['dbServer'], # asldkfj@aws
                    user= database_secrets[SECRETMANAGERKEY]["username"], # secretuser
                    password= database_secrets[SECRETMANAGERKEY]["password"], # secretuserpass
                    database= database_secrets[SECRETMANAGERKEY]["dbNametemplate"] #template_metadata
                )

        return shopify, template



    @staticmethod
    def dataframe_to_MySQL(dataframe, index_cols, table_name_string, connection, logs = True, batch_size = 1000): 
        # Given a dataframe, table name (string), and a database connection,
        # puts the dataframe into the table
        # 
        # NOTE: MUST have the exact same format as the table in MySQL
        #       - Same column names, etc
        #

        
        columns = list(dataframe.columns)

        values = list(dataframe.itertuples(index=False))

        non_index = columns.copy()

        [non_index.remove(i) for i in index_cols]
        mycursor = connection.cursor()
        
        
        lines = 1
        update_vals = []
        total = len(values)
        Utils.printProgressBar(0, total, prefix = "Updating " + table_name_string, suffix = 'Complete', length = 50)
        for value in values:
            update_vals.append(list(value))
            if lines % batch_size == 0:
                
                sql_update = Utils.batch_update(columns, update_vals, non_index, table_name_string)
                mycursor.execute(sql_update)
                connection.commit()
                mycursor.close() 
                mycursor = connection.cursor() 
                update_vals = []
                Utils.printProgressBar(lines/batch_size, total/batch_size, prefix = "Updating " + table_name_string, \
                    suffix = 'Complete', length = 50)

            lines = lines + 1

            if lines >= total:
                sql_update = Utils.batch_update(columns, update_vals, non_index, table_name_string)
                mycursor.execute(sql_update)
                connection.commit()
                mycursor.close() 
                mycursor = connection.cursor() 
                update_vals = []
                Utils.printProgressBar(lines/batch_size, total/batch_size, prefix = "Updating " + table_name_string, \
                    suffix = 'Complete', length = 50)


        # Utils.printProgressBar(total/batch_size, total/batch_size, prefix = "Updating " + table_name_string, \
        #             suffix = 'Complete', length = 50)   
        
            
        logging.info(table_name_string + " update complete!")

            


    @staticmethod
    def execute_sql(path_to_sql_file, connection):
        # executes and commits a text SQL file given a connection and path to the file
        # 
        # NOTE: 

        mycursor = connection.cursor()
        create_table = ''.join(open(path_to_sql_file, 'r').read().splitlines())

        statements = [x+';' for x in create_table.split(';')][:-1]
        # [print(i) for i in statements]
        # mycursor.close() 
        # mycursor = mydb.cursor() 

        for statement in statements:
            # execute the create table statement
        
            mycursor.execute(statement)
            connection.commit()
            mycursor.close() 
            mycursor = connection.cursor() 

        logging.info("Completed " + path_to_sql_file)
    
    @staticmethod
    def batch_update(names : list, values : list, non_index : list, table_name_string : str):
        '''
        takes three lists: one with column names, one with lists of values, 
        the name of the table to commit

        constructs sql update query

        INSERT into `table` (id, fruit)
        VALUES (1, 'apple'), (2, 'orange'), (3, 'peach')
        ON DUPLICATE KEY UPDATE fruit = VALUES(fruit);
        '''

        statement = "INSERT INTO " + table_name_string + " (`"
        
        statement = statement + "`, `".join(names) + "`) VALUES "

        for row in values:
            statement = statement + "(\"" + "\", \"".join([str(x) for x in row]) + "\"), "

        statement = statement[:-2] + " ON DUPLICATE KEY UPDATE "

        for col in non_index:
            if col != "created_time":

                statement = statement + col + " = values(" + col + "), "

        # print( statement[:-2] + ";")
        # raise ValueError('stop')
        return statement[:-2] + ";"


    @staticmethod
    def row_to_mysql(names : list, values : list, non_index : list, table_name_string : str):
        '''
        takes three lists: one with column names, one with values, 
        the name of the table to commit

        constructs sql update query in this format:
        
        '''


        together = dict(zip(names, values))

        statement = "INSERT INTO " + table_name_string + " (`"
        
        statement = statement + "`, `".join(names) + "`) VALUES (\"" + "\", \"".join([str(x) for x in values]) + "\")"

        statement = statement + " ON DUPLICATE KEY UPDATE "

        for col in non_index:
            statement = statement + col + " = \"" + str(together[col]) + "\", "

        return statement[:-2] + ";"


    # Print iterations progress
    # @SOURCE https://stackoverflow.com/questions/3173320/text-progress-bar-in-terminal-with-block-characters
    @staticmethod
    def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        try:
            percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
            filledLength = int(length * iteration // total)
            bar = fill * filledLength + '-' * (length - filledLength)
            print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
            # Print New Line on Complete
            if iteration == total: 
                print()
        except:
            pass


# print(Utils.row_to_mysql(['col1', 'col2', 'col3'], [1, 'a', 3], ['col2', 'col3'], 'test_table'))
