#
# This script will simulate the bank client. It will generate
# a defined number of CREDIT/DEBIT requests with random amount
# from interval <10000;50000>.
#
# Number of requests to be generated is read from the first parameter. 
# This parameter is optional and default value is 100.
#
from random import randrange
import sys
import requests

# Defualt number of requests to generate.
DEFAULT_REQUEST_COUNT = 100

# Default value for base API url.
DEF_API_URL = 'http://localhost:8080'

class RequestData:
	"""
	Messaging-like class to hold request data.
	"""
	
	def __init__(self, _operation, _amount):
		"""
		Initializes this request data with given OPERATION and amount.
		
		:param string _operation: Either 'CREDIT' or 'DEBIT'.
		:param int _amount: Amount of money for given operaion.
		"""
		self.operation = _operation
		self.amount = _amount

class Client:
	"""
	Class that wraps the client logic.
	"""
	
	def __init__(self, _request_count, _api_url):
		"""
		Initializes this client with number of requests to generate.
			
		:param int _request_count: 	Number of requests to generate.
		:param string _api_url: Base URL to access the sequencer API.
		"""
		self.request_count = _request_count
		self.api_url = _api_url
		
		
	def _generate_request(self):
		"""
		Generates one CREDIT/DEBIT request with random amnout from range <10000;50000>.
		
		:return Request metadata.
		"""
		amount = 10000 + randrange(40001)
		operation = 'CREDIT' if randrange(2) == 0 else 'DEBIT'
		return RequestData(operation, amount)
	
	def _send_request(self, req):
		"""
		Actually sends the request to the server.
		
		:param RequestData req: Object with request data.
		"""
		print("Sending '%s' request for amount of: %d." % (req.operation, req.amount))
		operation_api = '/' + req.operation.lower()
		headers = {'Content-Type': 'application/json'}
		response = requests.post(self.api_url + operation_api, headers = headers, json = {'amount' : req.amount})
		if response.status_code == 202:
			print("Request sent.")
		elif response.status_code == 404:
			print("API for %s operation not found." % req.operation)
		else: 
			print("Unexpected error, response with status %d returned." % response.status_code)
		
	def run(self):
		"""
		Starts the client. This method will exit after generating all the requests.
		"""
		print("Generating %d requests." % self.request_count)
		for req_countetr in range(0, self.request_count):
			req = self._generate_request()
			self._send_request(req)
		
		print("Requets generated and sent.")
			

def read_request_count():
	"""
	Reads the number of requests to be generated from command line
	arguments. If no or invalid argument is found, default value is 
	returned. The count is execpted to be in sys.argv[1].
	
	:return: Number of requests to generate.
	"""
	val = DEFAULT_REQUEST_COUNT
	try:
		val = int(sys.argv[1])
	except(ValueError):
		print("'%s' is not a valid number, using default value for request count." % sys.argv[1])
	
	return val


def read_params():
	"""
	Reads console parameters and returns them in array.
	Expected order:
	request count
	base api url (optional)
	
	:return: Array with ["request_count"] and ["base_api_url"]. None is returned in case of error.
	"""
	arg_count = len(sys.argv)
	
	params = {}
	
	if arg_count == 2:
		params["request_count"] = read_request_count()
		params["base_api_url"] = DEF_API_URL
		return params
	elif arg_count == 3:
		params["request_count"] = read_request_count()
		params["base_api_url"] = sys.argv[2]
		return params
	else:
		print("Wrong number of console arguments (%d), expected 1 or 2." % (len(sys.argv) - 1))
		return None
			
		
def main():
	"""
	Main method of the script.
	"""
	params = read_params()
	if not(params):
		return
	client = Client(params["request_count"], params["base_api_url"])
	client.run()
	
	
# Script body
main()
	