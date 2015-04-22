import json
import socket
import thread
import time
import random
import string

BUFF_SIZE = 1024

class Target:
    def send(self, message):
        packed = json.dumps(message, sort_keys=False)
        self.socket.send(packed)

    def recv(self):
        msg = self.socket.recv(BUFF_SIZE)
        print self.__class__.__name__, "<", msg # debug print
        if not msg:
            return False
        return json.loads(msg)

class Client(Target):
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.caps = { }
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect((self.hostname, self.port))

    def call(self, obj_type, cap, method, args):
        self.send({
            "obj": obj_type,
            "cap": cap,
            "method": method,
            "args": args
        })
        return self.recv()

    def GetProxy(self, obj_type, cap):
        return ClientProxy(self, obj_type, cap)

class Server(Target):
    def __init__(self, port):
        self.port = port
        self.caps = { }
        self.proxies = { }
        self.running = False
        self.listen_sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    """ Runs server on a new thread """
    def thread(self):
        thread.start_new_thread(self.run, ())

    """ Run server on the current thread """
    def run(self):
        self.listen_sck.bind(('127.0.0.1', self.port))
        self.listen_sck.listen(1)
        self.running = True
        while self.running:
            sck, addr = self.listen_sck.accept()
            self.socket = sck
            while self.running:
                reply = self.recv()
                if not reply: break # Break on disconnect

                proxy = self.FindProxy(reply['obj'], reply['cap'])
                if proxy != None:
                    proxy.call(reply['method'], reply['args'])
                else:
                    self.send({ 'error': True, 'message': 'No such capability ' + reply['cap'] })
            print 'Connection lost'

    """ Stop server """
    def stop(self):
        self.running = False

    def GetCapabilityString(self):
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))

    """ Finds and returns an existing Server Proxy object with a given type & capability string """
    def FindProxy(self, obj_type, cap):
        if not obj_type in self.caps:
            self.send({ 'error': True, 'message': 'No capabilities for type ' + obj_type })
            return
        caps = self.caps[obj_type]
        if not cap in caps:
            self.send({ 'error': True, 'message': 'No such capability ' + cap + ' for ' + obj_type })
            return
        return caps[cap]

    def GetProxy(self, instance):
        obj_type = instance.__class__.__name__

        # If its a client proxy just return it
        if obj_type == 'ClientProxy':
            return instance

        if not obj_type in self.proxies:
            self.proxies[obj_type] = { }
            self.caps[obj_type] = { }
        proxies = self.proxies[obj_type]
        caps = self.caps[obj_type]

        if not instance in caps:
            proxy = ServerProxy(self, instance, self.GetCapabilityString())
            proxies[instance] = proxy
            caps[proxy.cap] = proxy
            return proxy
        else:
            # this never seems to happen
            print 'Returning instance proxy'
            return proxies[instance]

class ClientProxy:
    def __init__(self, client, obj_type, cap):
        self.client   = client
        self.obj_type = obj_type
        self.cap      = cap
    def __getattr__(self, name):
        def proxy(*args):
            return self.client.call(self.obj_type, self.cap, name, args)
        return proxy

class ServerProxy:
    def __init__(self, server, target, cap):
        self.server = server
        self.target = target
        self.cap    = cap
    def call(self, name, *args):
        method = getattr(self.target, name)
        self.server.send(method(*args[0]))
