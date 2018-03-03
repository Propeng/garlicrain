from faucet.faucet_settings import faucet_settings
import jsonrpclib

session = None

def get_session():
	global session
	if session == None:
		session = RPCClient()
	return session

class RPCClient:
	def __init__(self):
		self.conn = jsonrpclib.Server(faucet_settings['rpc_url'])
	
	def __getattr__(self, name):
		return self.conn.__getattr__(name)