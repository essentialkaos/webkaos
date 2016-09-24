#!/usr/bin/env bash

###############################################################################

NORM=0
BOLD=1
UNLN=4
RED=31
GREEN=32
BROWN=33
BLUE=34
MAG=35
CYAN=36
GREY=90

CL_NORM="\e[${NORM}m"
CL_RED="\e[0;${RED};49m"
CL_GREEN="\e[0;${GREEN};49m"
CL_BROWN="\e[0;${BROWN};49m"
CL_BLUE="\e[0;${BLUE};49m"
CL_MAG="\e[0;${MAG};49m"
CL_CYAN="\e[0;${CYAN};49m"
CL_GREY="\e[0;${GREY};49m"
CL_BL_RED="\e[1;${RED};49m"
CL_BL_GREEN="\e[1;${GREEN};49m"
CL_BL_BROWN="\e[1;${BROWN};49m"
CL_BL_BLUE="\e[1;${BLUE};49m"
CL_BL_MAG="\e[1;${MAG};49m"
CL_BL_CYAN="\e[1;${CYAN};49m"
CL_BL_GREY="\e[1;${GREY};49m"

###############################################################################

main() {
  if [[ $# -ne 3 ]] ; then
    echo "Usage: ./patch-check.sh webkaos.patch old-ver-dir new-ver-dir"
    exit 0
  fi

  local patch_file="$1"
  local old_ver_dir="$2"
  local new_ver_dir="$3"

  local sources=$(grep '+++' "$patch_file" | tr "\t" " " | cut -f2 -d" " | cut -f2-99 -d "/")

  show ""

  for source_file in $sources ; do
    local old_ver_hash=$(getHash "$old_ver_dir/$source_file")
    local new_ver_hash=$(getHash "$new_ver_dir/$source_file")

    if [[ "$old_ver_hash" == "$new_ver_hash" ]] ; then
      show " ${CL_GREEN}✔ ${CL_NORM}$source_file"
    else
      local diff_size=$(diff -U 0 "$old_ver_dir/$source_file" "$new_ver_dir/$source_file" | grep -v ^@ | wc -l)
      show " ${CL_RED}✖ ${CL_NORM}$source_file ${CL_GREY}($diff_size lines)${CL_NORM}"
    fi
  done

  show ""
}

getHash() {
  sha256sum "$1" | cut -f1 -d" "
}

show() {
  if [[ -n "$2" ]] ; then
    echo -e "\e[${2}m${1}${CL_NORM}"
  else
    echo -e "$@"
  fi
}

###############################################################################

main $@
