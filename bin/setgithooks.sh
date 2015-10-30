#!/bin/bash

# Get absolute script dir
# Source: http://stackoverflow.com/questions/59895/can-a-bash-script-tell-what-directory-its-stored-in
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

# get parent dir
DIR=$(dirname ${DIR})

for f in $(ls ${DIR}/git-hooks); do
    rm -rf ${DIR}/.git/hooks/${f}
    ln -s ${DIR}/git-hooks/${f} ${DIR}/.git/hooks/${f}
done
