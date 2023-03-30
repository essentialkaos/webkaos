#!/bin/bash

################################################################################

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

################################################################################

# Main func
#
# *: Arguments
#
# Code: No
# Echo: No
main() {
  local spec_ver

  spec_ver=$(getVersionFromSpec)

  if [[ -z "$spec_ver" ]] ; then
    error "Can't find version info in spec file"
    exit 1
  fi

  show "Current webkaos version in spec: $spec_ver\n" $BOLD

  checkDockerfiles "$spec_ver"

  exit $?
}

checkDockerfiles() {
  local spec_ver="$1"
  local df df_name df_ver has_errors

  show "Checking dockerfiles…\n" $GREY

  for df in ".docker"/*.docker ; do
    df_name=$(basename "$df")
    df_ver=$(getVersionFromDockerfile "$df")

    if [[ -z "$df_ver" ]] ; then
      error "  ✖  Can't find version info in $df"
      has_errors=true
      continue
    fi

    if [[ "$df_ver" == "$spec_ver" ]] ; then
      show "  ✔  $df_name" $GREEN
    else
      show "  ✖  $df_name ($df_ver ≠ $spec_ver)" $RED
      has_errors=true
    fi
  done

  if [[ -n "$has_errors" ]] ; then
    show "\nFound problems with versions!" $RED
    return 1
  fi

  show "\nEverything looks fine, excellent!" $BOLD
  return 0
}

# Get webkaos version from dockerfile
#
# 1: Path to ockerfile (String)
#
# Code: No
# Echo: Version (String)
getVersionFromDockerfile() {
  grep 'ARG WEBKAOS_VER' "$1" | head -1 | tr -s ' ' |  cut -f2 -d'='
}

# Get webkaos version from spec file
#
# Code: No
# Echo: Version (String)
getVersionFromSpec() {
  grep 'define nginx_version' webkaos.spec | head -1 | tr -s ' ' |  cut -f3 -d' '
}

# Show message
#
# 1: Message (String)
# 2: Message color (Number) [Optional]
#
# Code: No
# Echo: No
show() {
  if [[ -n "$2" && -z "$no_colors" ]] ; then
    echo -e "\e[${2}m${1}\e[0m"
  else
    echo -e "$*"
  fi
}

# Print error message
#
# 1: Message (String)
# 2: Message color (Number) [Optional]
#
# Code: No
# Echo: No
error() {
  show "$*" $RED 1>&2
}

################################################################################

main "$@"
