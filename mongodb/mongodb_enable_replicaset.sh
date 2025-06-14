#!/bin/bash 

mongosh <<EOF
rs.initiate();
rs.status();
EOF