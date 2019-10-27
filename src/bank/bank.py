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

class Bank:
	"""
	Implementation of the bank server.
	"""
	
	def __init__(self, host, port, debug):
		"""
		Initializes this server with given values.
		"""
		self._host = host
		self._port = port
		self._debug = debug
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
		# todo call DB
		return HTTPResponse(status = 200)
	
	def _debit(self):
		"""
		Handler for /debit API.
		"""
		transaction = request.json
		print("Debit: " + str(transaction))
		# todo call DB
		return HTTPResponse(status = 200)
	
		
		
def main():
	"""
	Main method of the script, starts the server.
	"""
	bank = Bank('0.0.0.0', 8100, True)
	bank.start()
		

# Script body
main()

