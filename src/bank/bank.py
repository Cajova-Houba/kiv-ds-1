#
# This script will simulate the bank server. It will accept transaction orders
# from the shuffler, sort them by their id and execute them. There will be a couple
# of instances of this server running at the same time and each of them will use its'
# own DB.
#
# API offered by bank is described in doc/bank-api.yml.
#
# I used Bottle (https://falcon.readthedocs.io/en/stable/) framework for the API.
# It can be installed by 
# pip install bottle
#
# Test it using curl:
#  curl -X POST --header "Content-Type: application/json" --data '{"amount":5, "id":1}' localhost:8100/credit 
#

from bottle import Bottle, template, request, HTTPResponse
import mysql.connector

class DbConnector:
	"""
	Implementation of DB connector.
	"""
	
	def __init__(self, host = 'localhost', user = 'root', password = 'r00t', schema = 'bank_server', account_id = 1):
		self._host = host
		self._user = user
		self._password = password
		self._schema = schema
		self._account_id = account_id
		self._connection = self._get_connection()
	
	def _get_connection(self):
		return mysql.connector.connect(
			host=self._host,
			user=self._user,
			passwd=self._password,
			database=self._schema
		)
	
	def _perform_update_query(self, query, amount):
		"""
		Executes and commits the update query.
		"""
		db = self._connection
		cursor = db.cursor()
		cursor.execute(query, (amount, self._account_id))
		db.commit()
		cursor.close()
	
	def close_connection(self):
		self._connection.close()
	
	def credit_money(self, amount):
		"""
		Credits given amount of money to the account.
		"""
		print("crediting %d" % amount)
		self._perform_update_query(
			"update account set balance = balance + %s where id = %s;",
			amount
		)
		
	def debit_money(self, amount):
		"""
		Debits given amount of money from the account.
		"""
		print("debiting %d" % amount)
		self._perform_update_query(
			"update account set balance = balance - %s where id = %s;",
			amount
		)
		

class Bank:
	"""
	Implementation of the bank server.
	"""
	
	def __init__(self, host, port, debug, db_connector):
		"""
		Initializes this server with given values.
		"""
		self._host = host
		self._port = port
		self._debug = debug
		self._db_connector = db_connector
		self._app = Bottle()
		self._route()
	
	def start(self):
		"""
		Starts the server.
		"""
		self._app.run(host=self._host, port=self._port, debug = self._debug)
	
	def _route(self):
		"""
		Sets up routes to endpoints.
		"""
		self._app.route('/credit', method="POST", callback=self._credit)
		self._app.route('/debit', method="POST", callback=self._debit)		
		
	def _credit(self):
		"""
		Handler for /credit API.
		"""
		transaction = request.json
		print("Credit: " + str(transaction))
		self._db_connector.credit_money(transaction["amount"])
		return HTTPResponse(status = 200)
	
	def _debit(self):
		"""
		Handler for /debit API.
		"""
		transaction = request.json
		print("Debit: " + str(transaction))
		self._db_connector.debit_money(transaction["amount"])
		return HTTPResponse(status = 200)
	
		
		
def main():
	"""
	Main method of the script, starts the server.
	"""
	db_connector = DbConnector()
	bank = Bank('0.0.0.0', 8100, True, db_connector)
	bank.start()
	db_connector.close_connection()
		

# Script body
main()

