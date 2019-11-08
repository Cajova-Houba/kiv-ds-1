#
# This script will simulate the shuffler. It will accept transaction orders
# from sequencer, store them into the queue, shuffle them and send them 
# to the bank servers afterwards.
#
# API offer by sequencer is described in doc/shuffler-api.yml.
#
# I used Bottle (https://falcon.readthedocs.io/en/stable/) framework for the API.
# It can be installed by 
# pip install bottle
#
# Test it using curl:
#  curl -X POST --header "Content-Type: application/json" --data '{"amount":5, "id":1}' localhost:8090/credit 
#

from bottle import Bottle, template, request, HTTPResponse
import random
import requests
import json

# Size of the internal queue for transactions
QUEUE_SIZE = 10


class Shuffler:
	"""
	Implementation of the shuffler server.
	"""
	
	def __init__(self, host, port, debug, bank_servers):
		"""
		Initializes this server with given values.
		"""
		self._host = host
		self._port = port
		self._debug = debug
		self._queue = []
		self._bank_servers = bank_servers
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
		transaction["type"] = "credit"
		print("Credit: " + str(transaction))
		self._add_to_queue(transaction)
		return HTTPResponse(status = 202)
	
	def _debit(self):
		"""
		Handler for /debit API.
		"""
		transaction = request.json
		transaction["type"] = "debit"
		print("Debit: " + str(transaction))
		self._add_to_queue(transaction)
		return HTTPResponse(status = 202)
	
	def _add_to_queue(self, transaction):
		"""
		Adds transaction to the queue and if the queue is full, 
		calls method to send transactions to bank servers.
		"""
		self._queue.append(transaction)
		if len(self._queue) == QUEUE_SIZE:
			self._send_to_bank_servers()
	
	def _send_to_bank_servers(self):
		"""
		Sends the contents of queue to the bank servers.
		The queue is empty after requests are sent.
		"""
		print("Sending transactions to bank servers.")
		
		random.shuffle(self._queue)
		
		for index,bank_server in enumerate(self._bank_servers):
			print("Sending tranactions to server %d: %s" %(index, bank_server))
			for transaction in self._queue:
				operation_api = "/" + transaction["type"]
				headers = {'Content-Type': 'application/json'}
				del transaction["type"]
				response = requests.post(bank_server + operation_api, headers = headers, json = transaction)
				if response.status_code != 200:
					print("Error while sending transaction %d: %d" % (transaction["id"], response.status_code))
		
		self._queue = []
		print("Done.")
		

def load_bank_servers():
	"""
	Loads urls to bank servers from ./bank_servers.json file.
	"""
	input_file = open ('bank_servers.json')
	json_array = json.load(input_file)
	input_file.close()
	return json_array
	
		
def main():
	"""
	Main method of the script, starts the server.
	"""
	bank_servers = load_bank_servers()
	shuffler = Shuffler('0.0.0.0', 8090, True, bank_servers)
	shuffler.start()
		

# Script body
main()

