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
#  curl -X POST --header "Content-Type: application/json" --data '{"amount":5}' localhost:8090/credit 
#

from bottle import Bottle, template, request, HTTPResponse

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
	
	def __init__(self, counter, host, port, debug):
		"""
		Initializes this server with given values.
		"""
		self._counter = counter
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
		new_body = request.json
		new_body['id'] = self._counter.get_next_id()
		print(new_body)
		# todo call shuffler API
		return HTTPResponse(status = 202)
	
	def _debit(self):
		"""
		Handler for /debit API.
		"""
		print(request.json)
		new_body = request.json
		new_body['id'] = self._counter.get_next_id()
		print(new_body)
		return HTTPResponse(status = 202)
	
		
		
def main():
	"""
	Main method of the script, starts the server.
	"""
	counter = Counter()
	sequencer = Sequencer(counter, '0.0.0.0', 8090, True)
	sequencer.start()
		

# Script body
main()

