""" below varibles helps to change variable all through the code"""

## Utils
ENVIRON = 'dev' # 'dev' for staging # 'qa' for qa
SECRETMANAGERKEY = 'rds_analytics' # 'rds_analytics' for staging # 'rds' for qa

## Generates Products
# give list of shops ['21','22'] or 'all' TO GET ALL
# shopid = ['21','22']

# SHOPID = 'all' # default 'all'
BLACKLIST_SHOP = [] #  [11,12] -- > must be integer
SHOPID = [851]

GET_DATA = True
SQLPUSH = True
CHECK_NEWTEMPALTES = False

# used in Generate_products.py
## 0 -> no feedbackdata, 1->includes feedbackdata 
FEEDBACKDATA = 1  # default 1
COLOR_PERCENT = .4  # default .4
PRODUCT_LIMIT = 50

## used in Attr_match.py
COMPULSARY_ATTRIBUTES = True
COM_ATTRIBUTES = {'color','gender'}
## Not to set prod_update_flag=1 all feedback products 
## for minutes  use like 5 minute, 15 minute etc, for hours use 1 hour, 2 hour ets
FEEDBACK_INTERVAL = '2 hour'
BYPASS = False
COLOR_SIMILARITY = False
THRESHOLD_SCORE = 51
TOTAL_PRODUCT_COUNT = 6
## used in checkpoint.py


## Attr_match
fabric_var = True
category_var = True
BEGIN_NUM = '1' # must be string number '2','3','4'

## S3 Credentials
S3_BUCKET = 'shopify-airbyte-templete-csv'
S3_ENV = 'shopify-dev'



