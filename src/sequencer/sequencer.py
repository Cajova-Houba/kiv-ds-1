#
# This script will simulate the sequencer. It will accept transaction orders
# from client and mark each order with an unique identifier. Transaction order
# with unique ID is then sent to shuffler.
#
# API offer by sequencer is described in doc/sequencer-api.yml.
#
# I used Bottle (https://falcon.readthedocs.io/en/stable/) framework for the API.
# It can be installed by 
# pip install bottle
#
# Test it using curl:
#  curl -X POST --header "Content-Type: application/json" --data '{"amount":5}' localhost:8080/credit 
#

from bottle import Bottle, template, request, HTTPResponse
import requests
import json
import sys
import logging

class Counter:
	"""
	Class to be used as ID generator.
	"""
	
	def __init__(self):
		"""
		Initializes internal ID to value 0.
		"""
		self._id = 0
		
	def get_next_id(self):
		"""
		Returns the current ID and increments the internal ID value.
		
		:return: Next id.
		"""
		curId = self._id
		self._id = self._id + 1
		return curId

class Sequencer:
	"""
	Implementation of the sequencer server.
	"""
	
	def __init__(self, counter, host, port, debug, shuffler_url):
		"""
		Initializes this server with given values.
		"""
		self._counter = counter
		self._host = host
		self._port = port
		self._debug = debug
		self._shuffler_url = shuffler_url
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
		new_body = request.json
		new_body['id'] = self._counter.get_next_id()
		logging.info("Credit: %s" % str(new_body))
		self._send_to_shuffler("credit", new_body)
		return HTTPResponse(status = 202)
	
	def _debit(self):
		"""
		Handler for /debit API.
		"""
		new_body = request.json
		new_body['id'] = self._counter.get_next_id()
		logging.info("Debit: %s" % str(new_body))
		self._send_to_shuffler("debit", new_body)
		return HTTPResponse(status = 202)
	
	def _send_to_shuffler(self, operation, transaction):
		"""
		Sends transaction with id to shuffler.
		"""
		operation_api = "/" + str(operation)
		headers = {'Content-Type': 'application/json'}
		response = requests.post(self._shuffler_url + operation_api, headers = headers, data = json.dumps(transaction))
		if response.status_code != 202:
			logging.warning("Error while sending transaction %d: %d" % (transaction["id"], response.status_code))

def read_params():
	arg_count = len(sys.argv)
	
	params = {}
	
	if arg_count == 2:
		params["base_api_url"] = sys.argv[1]
		return params
	else:
		logging.warning("Wrong number of console arguments (%d), expected 1." % (len(sys.argv) - 1))
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
	logging.info("Starting sequencer")
	
	params = read_params()
	if params is None:
		return
	counter = Counter()
	sequencer = Sequencer(counter, '0.0.0.0', 8100, True, params["base_api_url"])
	sequencer.start()
		

# Script body
main()

