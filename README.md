# P2P chat tutorial.

    Following tutorial demonstrates how
to implement peer-to-peer chat messaging.
Peers use HolePunching traversal technique
on top python twisted framework.
    To check it out- You need to do following.

###   Install requirements
sudo apt-get install python-dev
sudo pip install twisted

###   On the machine behind Full-Cone NAT:
```bash
#   Using already pre-deployed version
#   of signal server, do the following:
python chat_server.py
```

###   On the several machine behind any kind of NAT:
```bash
python chat_client.py 9999 # port is optional
```

###   Send and receive messages.
