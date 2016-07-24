# P2P chat tutorial.

  Following tutorial demonstrates how
to implement peer-to-peer chat messaging.
Peers use HolePunching traversal technique
on top python twisted framework.
  To check it out- You need to do following.

###   Install requirements
```bash
sudo apt-get install python-dev
sudo easy_install pip
sudo pip install twisted
git clone https://github.com/yanlobkarev/p2p.git
cd p2p
```

###   On the machine behind Full-Cone NAT:
```bash
#   Using already pre-deployed version
#   of signal server, do the following
python chat_server.py
```

###   On the several machines behind any kind of NAT:
```bash
python chat_client.py 9999 # port is optional
```

###   Send and receive messages.
![](https://raw.githubusercontent.com/yanlobkarev/p2p/master/chat.png "chat between work & home computers")

###   Optionally You can deploy signal server by yourself:
```bash
python signal_server.py & # runs on 8888 port
```
And don't forget to adjust `common.py`:
```python
SIGNAL_SERVER_IP = 'XXX.XXX.XXX.XXX'  #   There should be IP your signal server
SIGNAL_SERVER_PORT = 8888
```


