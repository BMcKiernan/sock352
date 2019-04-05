# Project 1 Simplified go-back-n

To Run: 

While I'm sure this goes without saying please make sure you run the server2.py before running the client2.py.

Also this implementation is dependent on the -u and -v args being reversed for the client2.py and server2.py as this is the only way they know which udp port to send data to.


Considerations:

This project is as best as it can get without the sliding window restricting how many packets the server2.py can send before needing to wait for the client2.py

Because of this the way I implemented go-back-n was if the client was more than one packet behind the server in acknowledged packets and the timeout occured then it would do go-back-n.  In practice this never occurs because the time it takes to run the program is (on my computer) 1/10th the duration we were instructed to set the timeout too. Therefore go-back-n could never occur. I tried messing with the timeout time to get it work but this introduced concurrency issues.

In conclusion the only way I can think of to get this working properly is to use a sliding window limiting how hard the server can get ahead and also making the server wait until every packet has been acknowledged before exiting.
