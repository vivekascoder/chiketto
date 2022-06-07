SP=~/smartpy-cli/SmartPy.sh
SHELL := /bin/bash
PYTHONPATH := "./"
export PYTHONPATH

test_factory:
	@echo "> Runnning test for Event Factory."
	$(SP) test ./contracts/EventFactory.py ./output --html

open_log:
	@echo "> Opening log."
	live-server ./output/Test_EventFactory/log.html

deploy_factory:
	@echo "> Compiling Crowdsale Factory."
	$(SP) compile ./contracts/factory.py ./output --html

	@echo "> Deploying on testnet."
	$(SP) originate-contract \
		--code ./output/Factory/step_000_cont_0_contract.tz \
		--storage ./output/Factory/step_000_cont_0_storage.tz \
		--rpc https://ithacanet.smartpy.io
	
	@echo "> Deployed contraevent


test_event:
	@echo "> Running test for the Event contract."
	$(SP) test ./contracts/Event.py ./output --html

open_event:
	@echo "> Opening logs for Event contract"
	open ./output/Test_Event/log.html