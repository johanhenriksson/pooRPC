import oorpc

client = oorpc.Client("127.0.0.1", 12345)
client.connect()

# create two client proxies since we know the capabilities
usr_a = client.GetProxy('User', raw_input('User 1:'))
usr_b = client.GetProxy('User', raw_input('User 2:'))

# modify objects through client proxies
usr_a.GetName()
usr_a.SetName("nytt namn")
usr_a.GetName()
usr_b.GetName()
