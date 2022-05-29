Clone it all.

cd into Patent_Search_DC and follow instructions

cd into broker from root
run python main.py to start up the main broker server

cd into resource from root
run python main.py to start up a resource, it automatically connects to broker if it is running on localhost:8000
otherwise on console you can enter the brokers IP

open 127.0.0.1:80000/docs to be able to search/run queries from our API interface.

the query is accepted by a brokers worker which then sends the command to all connected resources to get relevant results.

Results are collected back at broker and merged into single response then sent to Client as search Query response.