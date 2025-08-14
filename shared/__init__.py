# shared/infrastructure/database.py
from peewee import MySQLDatabase

DB_CONFIG = {
    'database': 'coupon_microservice',
    'user': 'root',
    'password': 'gitano200J@@J@@',  # tu clave
    'host': 'localhost',
    'port': 3306
}
db = MySQLDatabase(**DB_CONFIG)
