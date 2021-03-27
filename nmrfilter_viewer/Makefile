build:
	docker build -t pylipids_lmscc .

bash:
	docker run -it -p 5030:5030 --rm -v $(shell pwd):/home/pylipids --name pylipids_lmscc pylipids_lmscc bash

interactive:
	docker run -it -p 5030:5030 --rm -v $(shell pwd):/home/pylipids --name pylipids_lmscc pylipids_lmscc sh /home/pylipids/run_server.sh

server:
	docker run -itd -p 5030:5030 --rm -v $(shell pwd):/home/pylipids --name pylipids_lmscc pylipids_lmscc sh /home/pylipids/run_server.sh
