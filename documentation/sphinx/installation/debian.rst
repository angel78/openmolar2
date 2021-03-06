Installation on Debian
======================

:Author: Neil Wallace neil@openmolar.com
   
Debian is my Gnu/linux distribution of choice, and the platform I have used for 
the majority of time whilst developing openmolar2.

Consequently, it should come as no surprise that installation on this platform
is well supported (and hopefully painless!).

I have a repos for debian ::

	STABLE(SQUEEZE)
	deb http://openmolar.com/debian stable main
	deb-src http://openmolar.com/debian stable main
	
	TESTING(WHEEZY)
	deb http://openmolar.com/debian testing main
	deb-src http://openmolar.com/debian testing main
	
	UNSTABLE(SID)
	deb http://openmolar.com/debian unstable main
	deb-src http://openmolar.com/debian unstable main
	 
add the flavour you require to your sources.list. (codename aliases should be supported eg. squeeze, wheezy etc..)

The repo is signed by my key, which is available ::

	http://www.openmolar.com/rowinggolfer.gpg.key
	

Once you have enabled the repo of your choice, get whichever components you require. ::
	
	OPENMOLAR2
	~# apt-get install openmolar-server openmolar-admin openmolar-client
	
	OPENMOLAR1 (deprecated)
	~# apt-get install openmolar-orig

