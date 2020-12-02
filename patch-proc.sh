#!/usr/bin/env bash

###############################################################################

NORM=0
BOLD=1
UNLN=4
RED=31
GREEN=32
YELLOW=33
BLUE=34
MAG=35
CYAN=36
GREY=37
DARK=90

CL_NORM="\e[${NORM}m"
CL_BOLD="\e[${BOLD}m"
CL_UNLN="\e[${UNLN}m"
CL_RED="\e[${RED}m"
CL_GREEN="\e[${GREEN}m"
CL_YELLOW="\e[${YELLOW}m"
CL_BLUE="\e[${BLUE}m"
CL_MAG="\e[${MAG}m"
CL_CYAN="\e[${CYAN}m"
CL_GREY="\e[${GREY}m"
CL_DARK="\e[${DARK}m"

###############################################################################

main() {
  if [[ $# -ne 4 ]] ; then
    usage
    exit 0
  fi

  check "$@"

  local choice

  show "Copy unchanged files? (y/N):" $BOLD
  read -p "> " choice

  if [[ "$choice" == "Y" || "$choice" == "y" ]] ; then
    copy "$@"
  fi
}

check() {
  checkArgs "$@"

  local patch_file data_dir old_ver new_ver old_ver_dir new_ver_dir
  local sources old_ver_hash new_ver_hash diff_size

  patch_file="$1"
  data_dir="$2"
  old_ver="$3"
  new_ver="$4"
  
  old_ver_dir="${data_dir}/nginx-${old_ver}-orig"
  new_ver_dir="${data_dir}/nginx-${new_ver}-orig"

  if [[ ! -e "$old_ver_dir" ]] ; then
    show "Directory $old_ver_dir doesn't exist" $RED
    exit 1
  fi

  if [[ ! -e "$new_ver_dir" ]] ; then
    show "Directory $new_ver_dir doesn't exist" $RED
    exit 1
  fi

  sources=$(grep '+++' "$patch_file" | tr "\t" " " | cut -f2 -d" " | cut -f2-99 -d "/")

  show ""

  for source_file in $sources ; do
    old_ver_hash=$(getHash "$old_ver_dir/$source_file")
    new_ver_hash=$(getHash "$new_ver_dir/$source_file")

    if [[ "$old_ver_hash" == "$new_ver_hash" ]] ; then
      show " ${CL_GREEN}✔  ${CL_NORM}$source_file"
    else
      diff_size=$(getDiffSize "$old_ver_dir/$source_file" "$new_ver_dir/$source_file")
      show " ${CL_RED}✖  ${CL_NORM}${CL_BOLD}$source_file ${CL_DARK}(± $diff_size lines)${CL_NORM}"
      showDiff "$old_ver_dir/$source_file" "$new_ver_dir/$source_file"
    fi
  done

  show ""
}

copy() {
  checkArgs "$@"
  
  local patch_file data_dir old_ver new_ver
  local old_ver_dir new_ver_dir old_ver_pt_dir new_ver_pt_dir
  local sources old_ver_hash new_ver_hash

  patch_file="$1"
  data_dir="$2"
  old_ver="$3"
  new_ver="$4"
  
  old_ver_dir="${data_dir}/nginx-${old_ver}-orig"
  new_ver_dir="${data_dir}/nginx-${new_ver}-orig"
  old_ver_pt_dir="${data_dir}/nginx-${old_ver}"
  new_ver_pt_dir="${data_dir}/nginx-${new_ver}"

  sources=$(grep '+++' "$patch_file" | tr "\t" " " | cut -f2 -d" " | cut -f2-99 -d "/")

  show ""

  for source_file in $sources ; do
    old_ver_hash=$(getHash "$old_ver_dir/$source_file")
    new_ver_hash=$(getHash "$new_ver_dir/$source_file")

    if [[ "$old_ver_hash" == "$new_ver_hash" ]] ; then
      show " $data_dir/${CL_BOLD}{$old_ver → $new_ver}${CL_NORM}/$source_file"
      cp "$old_ver_pt_dir/$source_file" "$new_ver_pt_dir/$source_file"
    fi
  done

  show ""
}

getDiffSize() {
  local file1="$1"
  local file2="$2"

  local diff_size=$(diff -U 0 "$file1" "$file2" | wc -l)

  diff_size=$(( diff_size - 3 ))

  echo "$diff_size"
}

showDiff() {
  local file1="$1"
  local file2="$2"

  show "$CL_GREY"
  diff -U 0 "$file1" "$file2" | sed -n 3,9999p | sed 's/^/   /g' | sed 's/@@ //g' | sed 's/ @@//g'
  show "$CL_NORM"
}

checkArgs() {
  local patch_file data_dir old_ver new_ver
  local old_ver_dir new_ver_dir old_ver_pt_dir new_ver_pt_dir

  patch_file="$1"
  data_dir="$2"
  old_ver="$3"
  new_ver="$4"

  if ! head -1 "$patch_file" | grep -q -o 'diff -urN' ; then
    error "File $patch_file is not a patch file"
    exit 1
  fi

  if [[ $(echo "$old_ver" | tr -d '[:digit:].') != "" ]] ; then
    error "$old_ver is not a valid Nginx version"
    exit 1
  fi

  if [[ $(echo "$new_ver" | tr -d '[:digit:].') != "" ]] ; then
    error "$new_ver is not a valid Nginx version"
    exit 1
  fi

  old_ver_dir="${data_dir}/nginx-${old_ver}-orig"
  new_ver_dir="${data_dir}/nginx-${new_ver}-orig"
  old_ver_pt_dir="${data_dir}/nginx-${old_ver}"
  new_ver_pt_dir="${data_dir}/nginx-${new_ver}"

  if [[ ! -e "$data_dir" ]] ; then
    error "Directory $data_dir doesn't exist"
    exit 1
  fi

  if [[ ! -e "$old_ver_dir" ]] ; then
    error "Directory $old_ver_dir doesn't exist"
    exit 1
  fi

  if [[ ! -e "$new_ver_dir" ]] ; then
    error "Directory $new_ver_dir doesn't exist"
    exit 1
  fi

  if [[ ! -e "$old_ver_pt_dir" ]] ; then
    error "Directory $old_ver_pt_dir doesn't exist"
    exit 1
  fi

  if [[ ! -e "$new_ver_pt_dir" ]] ; then
    error "Directory $new_ver_pt_dir doesn't exist"
    exit 1
  fi
}

getHash() {
  sha256sum "$1" | cut -f1 -d" "
}

show() {
  if [[ -n "$2" ]] ; then
    echo -e "\e[${2}m${1}\e[0m"
  else
    echo -e "$*"
  fi
}

error() {
  show "$*" $RED 1>&2
}

usage() {
  show ""
  show "${CL_BOLD}Usage:${CL_NORM} ./patch-proc.sh patch data-dir prev-ver new-ver"
  show ""
  show "Examples" $BOLD
  show ""
  show "  ./patch-proc.sh SOURCES/webkaos.patch /some/dir 1.17.5 1.17.6"
  show "  Check diff and copy unchanged files" $DARK
  show ""
}

###############################################################################

main "$@"
