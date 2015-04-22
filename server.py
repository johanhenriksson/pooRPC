import oorpc
import User

# create some regular objects
usr1 = User.User()
usr2 = User.User()
usr1.SetName("johan")
usr2.SetName("annan")

# start a server and create two proxies to local objects
server = oorpc.Server(12345)
usp1 = server.GetProxy(usr1)
usp2 = server.GetProxy(usr2)

print 'User 1:', usp1.cap
print 'User 2:', usp2.cap

server.run()
