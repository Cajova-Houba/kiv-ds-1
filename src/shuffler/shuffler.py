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
import sys
import logging

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
		logging.info("Credit: " + str(transaction))
		self._add_to_queue("credit", transaction)
		return HTTPResponse(status = 202)
	
	def _debit(self):
		"""
		Handler for /debit API.
		"""
		transaction = request.json
		logging.info("Debit: " + str(transaction))
		self._add_to_queue("debit", transaction)
		return HTTPResponse(status = 202)
	
	def _add_to_queue(self, type, transaction):
		"""
		Adds transaction to the queue and if the queue is full, 
		calls method to send transactions to bank servers.
		"""
		self._queue.append([type, transaction])
		if len(self._queue) == QUEUE_SIZE:
			self._send_to_bank_servers()
	
	def _send_to_bank_servers(self):
		"""
		Sends the contents of queue to the bank servers.
		The queue is empty after requests are sent.
		"""
		logging.info("Sending transactions to bank servers.")
		
		random.shuffle(self._queue)
		
		for transaction in self._queue:
			for index,bank_server in enumerate(self._bank_servers):
				logging.info("Sending tranaction %d to server %d: %s" %(transaction[1]["id"], index, bank_server))
				try:
					operation_api = "/" + transaction[0]
					headers = {'Content-Type': 'application/json'}
					response = requests.post(bank_server + operation_api, headers = headers, data = json.dumps(transaction[1]))
					if response.status_code != 200:
						logging.warning("Error while sending transaction %d: %d" % (transaction[1]["id"], response.status_code))
				except:
					logging.warning("Error while sending transaction %d" % transaction[1]["id"])
		
		self._queue = []
		logging.info("Done.")
		

def load_bank_servers(filename):
	"""
	Loads urls to bank servers from ./bank_servers.json file.
	"""
	input_file = open (filename, 'r')
	json_array = json.load(input_file)
	input_file.close()
	return json_array


def read_params():
	"""
	Reads console parameters and returns them in array.
	Expected order:
	path to file with bank servers configuration
	
	:return: Array with ["request_count"] and ["base_api_url"]. None is returned in case of error.
	"""
	arg_count = len(sys.argv)
	
	params = {}
	
	if arg_count == 2:
		params["bank_servers_conf"] = sys.argv[1]
		return params
	else:
		logging.error("Wrong number of console arguments (%d), expected 1." % (len(sys.argv) - 1))
		return None	
		
def main():
	"""
	Main method of the script, starts the server.
	"""
	logging.basicConfig(filename='log.txt',
                            filemode='a',
                            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.DEBUG)
	
	logging.info("Starting shuffler")
	params = read_params()
	if params is None:
		return 
	bank_servers = load_bank_servers(params["bank_servers_conf"])
	shuffler = Shuffler('0.0.0.0', 8100, True, bank_servers)
	shuffler.start()
		

# Script body
main()

