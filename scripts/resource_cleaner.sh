#!/bin/bash
#
# This is a custom script for QGIS-Development to give a development solution to the annoying resources_rc bug.
#
# Copyright (c) 2020 Julian Psotta <julianpsotta@gmail.com>
usage() {
  set +x
  cat 1>&2 <<HERE

This is a custom script for QGIS-Development to give a development solution to the annoying resources_rc bug.
It runs recursively until manually quit.
The goals is to check all files in a given directory that end on '*.ui' and replace the following content:

 <resources>
  <include location="..."/>
 </resources>

with:

 <resources/>

USAGE:
    ./resource_cleaner.sh -p /path/to/development/folder

OPTIONS (Clean *.ui files from wrong Resource tag):

    #  # Set the Greenlight db settings
  -p <FOLDER_PATH> Provide the postgres URL

  -v <version>     Gives the current script version

EXAMPLES:
  /bin/bash  resource_cleaner.sh -p /path/to/folder/

SUPPORT:
    Community: https://github.com/MichaelsJP/ohsome-qgis-plugin

HERE
}

START_DIRECTORY=$PWD
SCRIPT_NAME="UI-Cleanup"
VERSION_TAG=0.1

################################################################################
# Initialize SAY function                                                      #
################################################################################

say() {
  echo -e "\e[44m""$SCRIPT_NAME:\e[49m $1" >&2
}

################################################################################
# Initialize TRAP functions                                                 #
################################################################################

# trap ctrl-c and call ctrl_c()
trap ctrl_c INT

function ctrl_c() {
  say "Trapped CTRL-C"
  err "Script was manually canceled"
}

################################################################################
# Initialize LOGGING functions                                                 #
################################################################################

err() {
  echo -e "\e[101m""ERROR:\e[49m ""$1" >&2
  exit 1
}

dependency_found() {
  echo -e "\e[44m""Dependency check:\e[49m\e[32m found \e[39m $1"
}

dependency_not_found() {
  echo -e "\e[44m""Dependency check:\e[49m\e[31m not found\e[39m $1"
  cleanup
  exit 1
}

################################################################################
# Initialize helper functions                                                  #
################################################################################

get_absolute_path() {
  # Return the absolut path of a file or folder relative to its start
  # $1 file or folder name
  cd "$1" || err "Can't return absolute path for $1"
  echo "$PWD"
}

CheckSed() {
  if type -p sed >/dev/null; then
    dependency_found "sed"
  else
    dependency_not_found "sed"
  fi
}

check_mandatory_argument() {
  # If $2 is set it is used as a value for $1. Else $3 is used as a default value.
  # If neither $2 nor $3 is set, an error is thrown.
  # $1 Name of the variable
  # $2 Value of the variable
  # $3 Optional default value
  if [ -z "${2}" ]; then
    if [ -n "${3}" ]; then
      say "Setting default $1=$3"
      export "${1}"="${3}"
    else
      err "$1 needs to be set."
    fi
  else
    say "Setting custom $1=$2"
  fi
}

CheckNonRoot() {
  if [ $(id -u) == 0 ]; then
    err "Don't run this script as root"
  fi
}

CheckSystem() {
  if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
    err "This script only runs in linux and Mac OS systems"
  fi
}

################################################################################
# Initialize main functions                                                  #
################################################################################

testing_loop() {
  # Runs the Resource cleanup on all *.ui files in the Path provided
  # $1 folder path
  say "Started *.ui cleanup routing for folder $1"
  inotifywait -qm "$1" |
    while read -r path_to_file _ file; do
      if [[ "$file" =~ .*ui$ ]]; then # Does the file end with .ui?
        sed -i ':a;N;$!ba; s|<resources>.*<\/resources>|<resources\/>|g' "$path_to_file$file"
      fi
    done
}

################################################################################
################################################################################
# Main program                                                                 #
################################################################################
################################################################################
main() {
  export DEBIAN_FRONTEND=noninteractive

  CheckSystem
  CheckNonRoot

  while builtin getopts "hvp:" opt "${@}"; do
    case $opt in
    h)
      usage
      exit 0
      ;;
    v)
      say "Current script version: ${VERSION_TAG}"
      exit 0
      ;;
    p)
      FOLDER_PATH=$OPTARG
      if [ -z "$FOLDER_PATH" ]; then
        err "You must provide a valid folder."
      fi
      ;;
    :)
      err "Missing option argument for -$OPTARG"
      ;;
    \?)
      err "Invalid option: -$OPTARG" >&2
      usage
      ;;
    esac
  done

  # Check mandatory
  check_mandatory_argument "FOLDER_PATH" "$FOLDER_PATH"
  testing_loop "$FOLDER_PATH"
}
# Must be the last statement
main "$@" || exit 1
