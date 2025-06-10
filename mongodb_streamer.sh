#!/bin/bash 

docker exec -it mongo-rs mongosh;
rs.initiate();
collection.watch();
rs.status();