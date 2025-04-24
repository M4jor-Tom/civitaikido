#!/bin/bash

export ROLE=$1
export PROFILE=DEV
if [[ $ROLE == "" ]]; then
    export ROLE=injector_extractor
fi
if [[ $PROFILE != "" ]] && [[ $ROLE != "" ]]; then
  cd app
  python main.py
  exit 0
else
  echo "Error:"
  if [[ $ROLE == "" ]]; then
      echo "> ROLE is unset"
  fi
  exit 1
fi
