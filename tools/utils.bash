#!/usr/bin/env bash

function exit_on_failure {
    RET_CODE=$?
    ERR_MSG=$1
    if [ $RET_CODE -ne 0 ]; then
        echo $ERR_MSG
        exit 1
    fi
}

function exit_if_empty {
    STRING=${1:-}
    ERR_MSG=${2:-}
    if [ -z "$STRING" ]; then
        echo $ERR_MSG
        exit 1
    fi
}
