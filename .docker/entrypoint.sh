#!/bin/bash

################################################################################

if [[ -z "$is_test" ]] ; then
  set -e
fi

################################################################################

# Path to configuration file (String)
conf_file="/etc/webkaos/webkaos.conf"

# Path to directory with custom configuration files (String)
conf_dir="/etc/webkaos/conf.d"

################################################################################

cg1_cpuacct="/sys/fs/cgroup/cpu,cpuacct"
cg1_cpuset="/sys/fs/cgroup/cpuset"
cg1_cfs_quota_file="${cg1_cpuacct}/cpu.cfs_quota_us"
cg1_cfs_period_file="${cg1_cpuacct}/cpu.cfs_period_us"
cg1_effective_cpus_file="${cg1_cpuset}/cpuset.effective_cpus"

cg2_cpu_max_file="/sys/fs/cgroup/cpu.max"
cg2_effective_cpus_file="/sys/fs/cgroup/cpuset.cpus.effective"

################################################################################

main() {
  if [[ -n "$WEBKAOS_ENABLE_ENTRYPOINT_LOGS" ]] ; then
    exec 3>&1
  else
    exec 3>/dev/null
  fi

  if [[ -n "$is_test" ]] ; then
    return
  fi

  configureProcNum
  configureBucketSize

  startWebkaos "$@"
}

# Configure number of worker based on cgroups/cgroups limits
#
# Code: No
# Echo: No
configureProcNum() {
  if [[ -n "$WEBKAOS_DISABLE_PROC_TUNE" ]] ; then
    if ! sed -i "s#{{WORKERS}}#auto#" $conf_file &> /dev/null ; then
      error "Can't update configuration file $conf_file"
      doExit 1
      return
    else
      log "Workers number tuning is disabled, configuration property 'worker_processes' set to \"auto\""
    fi
  fi

  local cpu_num cpu_limits

  cpu_num=$(getNumProc)
  cpu_limits=$(getCPULimitsCG1)

  if [[ $cpu_limits == "-1" ]] ; then
    cpu_limits=$(getCPULimitsCG2)

    if [[ $cpu_limits == "-1" ]] ; then
      log "Can't find any limits in cgroups, 'worker_processes' will be set to \"$cpu_num\""
      cpu_limits="$cpu_num"
    else
      if [[ "$cpu_limits" != "$cpu_num" ]] ; then
        log "Limits set by CGroupsV2, 'worker_processes' will be set to \"$cpu_limits\""
      fi
    fi
  else
    if [[ "$cpu_limits" != "$cpu_num" ]] ; then
      log "Limits set by CGroupsV1, 'worker_processes' will be set to \"$cpu_limits\""
    fi
  fi

  cpu_num=$(minCPU "$cpu_num" "$cpu_limits")

  if ! sed -i "s#{{WORKERS}}#${cpu_num}#" $conf_file &> /dev/null ; then
    error "Can't update configuration file $conf_file"
    doExit 1
  else
    log "Configuration property 'worker_processes' set to \"$cpu_limits\""
  fi
}

# Configure hash bucket size
#
# Code: No
# Echo: No
configureBucketSize() {
  if [[ -n "$WEBKAOS_DISABLE_BUCKET_TUNE" ]] ; then
    if ! sed -i "s#{{BUCKET_SIZE}}#${WEBKAOS_HASH_BUCKET_SIZE:-64}#" $conf_file &> /dev/null ; then
      error "Can't update configuration file $conf_file"
      doExit 1
      return
    else
      log "Bucket size tuning is disabled, configuration property 'server_names_hash_bucket_size' set to \"${bucket_size}\""
    fi
  fi

  local bucket_size

  bucket_size=$(getBucketSize)

  if ! sed -i "s#{{BUCKET_SIZE}}#${bucket_size}#" $conf_file &> /dev/null ; then
    error "Can't update configuration file $conf_file"
    doExit 1
    return
  else
    log "Configuration property 'server_names_hash_bucket_size' set to \"${bucket_size}\""
  fi
}

# Start webkaos daemon
#
# Code: No
# Echo: No
startWebkaos() {
  exec "$@"
}

################################################################################

# Get CPU limits from cgroups
#
# Code: No
# Echo: Number of CPU's limited by cgroups (Number)
getCPULimitsCG1() {
  if [[ ! -d "$cg1_cpuacct" || ! -d "$cg1_cpuset" ]] ; then
    echo -1
    return
  fi

  local cpu_quota cpu_cpuset

  cpu_quota=$(getCPULimitsCG1Cpuacct)
  cpu_cpuset=$(getCPULimitsCG1Cpuset)

  if [[ "$cpu_quota" == "-1" && "$cpu_cpuset" == "-1" ]] ; then
    echo -1
    return
  fi

  minCPU "$cpu_quota" "$cpu_cpuset"
}

# Get CPU limits from cgroups CFS quotas
#
# Code: No
# Echo: Number of CPU's limited by CFS quotas (Number)
getCPULimitsCG1Cpuacct() {
  local cpuacct_num cfs_quota cfs_period

  if [[ ! -f "$cg1_cfs_quota_file" || ! -f "$cg1_cfs_period_file" ]] ; then
    echo -1
    return 
  fi

  cfs_quota=$(cat "$cg1_cfs_quota_file")
  cfs_period=$(cat "$cg1_cfs_period_file")

  if [[ -z "$cfs_quota" || "$cfs_quota" == "-1" ]] ; then
    echo -1
    return
  fi

  if [[ -z "$cfs_period" || "$cfs_period" == "0" ]] ; then
    echo -1
    return
  fi

  cpuacct_num=$(( (cfs_quota + cfs_period - 1) / cfs_period ))

  echo "$cpuacct_num"
}

# Get CPU limits from cgroups assigned CPU's
#
# Code: No
# Echo: Number of CPU's limited by assigned CPU's (Number)
getCPULimitsCG1Cpuset() {
  local effective_cpus

  if [[ ! -f "$cg1_effective_cpus_file" ]] ; then
    echo -1
    return
  fi

  effective_cpus=$(tr ',' ' ' < "$cg1_effective_cpus_file")

  # shellcheck disable=SC2086
  calculateCPUSets $effective_cpus
}

# Get CPU limits from cgroups v2
#
# Code: No
# Echo: Number of CPU's limited by cgroups2 (Number)
getCPULimitsCG2() {
  if [[ ! -f "$cg2_cpu_max_file" || ! -f "$cg2_effective_cpus_file" ]] ; then
    echo -1
    return
  fi

  local cpu_quota cpu_cpuset

  cpu_quota=$(getCPULimitsCG2CpuMax)
  cpu_cpuset=$(getCPULimitsCG2Cpuset)

  if [[ "$cpu_quota" == "-1" && "$cpu_cpuset" == "-1" ]] ; then
    echo -1
    return
  fi

  minCPU "$cpu_quota" "$cpu_cpuset"
}

# Get CPU limits from cgroups v2 cpu.max quotas
#
# Code: No
# Echo: Number of CPU's limited by cpu.max quotas (Number)
getCPULimitsCG2CpuMax() {
  local cpuacct_num cfs_quota cfs_period

  if [[ ! -f "$cg2_cpu_max_file" ]] ; then
    echo -1
    return
  fi

  cfs_quota=$(cut -f1 -d' ' < "$cg2_cpu_max_file")
  cfs_period=$(cut -f2 -d' ' < "$cg2_cpu_max_file")

  if [[ -z "$cfs_quota" || "$cfs_quota" == "max" ]] ; then
    echo -1
    return
  fi

  if [[ -z "$cfs_period" || "$cfs_period" == "0" ]] ; then
    echo -1
    return
  fi

  cpuacct_num=$(( (cfs_quota + cfs_period - 1) / cfs_period ))

  echo "$cpuacct_num"
}

# Get CPU limits from cgroups v2 assigned CPU's
#
# Code: No
# Echo: Number of CPU's limited by assigned CPU's (Number)
getCPULimitsCG2Cpuset() {
  local effective_cpus

  if [[ ! -f "$cg2_effective_cpus_file" ]] ; then
    echo -1
    return
  fi

  effective_cpus=$(tr ',' ' ' < "$cg2_effective_cpus_file")

  # shellcheck disable=SC2086
  calculateCPUSets $effective_cpus
}

# Calculate number of CPU's defined in cpuset
#
# *: cpuset values
#
# Code: No
# Echo: Number of CPU's from cpuset (Number)
calculateCPUSets() {
  local cpuset_val cpuset_num cpu_count

  cpuset_num=0

  for cpuset_val in "$@" ; do
    if [[ "$cpuset_val" =~ [0-9]+\-[0-9]+ ]] ; then
      # shellcheck disable=SC2086
      cpu_count=$(seq "${cpuset_val%-*}" "${cpuset_val#*-}" | wc -l)
      cpuset_num=$(( cpuset_num + cpu_count ))
    else
      (( cpuset_num++ ))
    fi
  done

  echo "$cpuset_num"
}

# Get hash bucket size based on virtual hosts names
#
# Code: No
# Echo: Hash bucket size (Number)
getBucketSize() {
  if [[ $(find "$conf_dir" -maxdepth 1 -name '*.conf' | wc -l) == "0" ]] ; then
    echo "${WEBKAOS_HASH_BUCKET_SIZE:-64}"
    return
  fi

  local vhost
  local size=64

  while read -r vhost ; do

    if [[ ${#vhost} -gt 238 && size -lt 512 ]] ; then
      size=512
    elif [[ ${#vhost} -gt 110 && size -lt 256 ]] ; then
      size=256
    elif [[ ${#vhost} -gt 46 && size -lt 128 ]] ; then
      size=128
    fi

  done < <(grep -h 'server_name' "$conf_dir"/*.conf | tr -s ' ' | sed 's/^ \+server_name \+//' | tr -d ';' | tr ' ' '\n' | sort -u)

  echo "$size"
}

# Get the number of processors which are currently online (i.e., available)
#
# Code: No
# Echo: Number of online CPU's (Number)
getNumProc() {
  getconf _NPROCESSORS_ONLN
}

# Get the smallest number from given two
#
# 1: First number (Number)
# 2: Second number (Number)
#
# Code: No
# Echo: Smallest number (Number)
minCPU() {
  local result

  if [[ "$1" != "-1" && "$2" == "-1" ]] ; then
    result="$1"
  elif [[ "$1" == "-1" && "$2" != "-1" ]] ; then
    result="$2"
  elif [[ "$1" -lt "$2" ]] ; then
    result="$1"
  else
    result="$2"
  fi

  # Minimal number of CPU is 1
  if [[ "$result" -le 0 ]] ; then
    echo 1
  else
    echo "$result"
  fi
}

################################################################################

# Print error message
#
# 1: Error message (String)
#
# Code: No
# Echo: No
error() {
  if [[ -z "$is_test" ]] ; then
    echo "$(date +'%Y/%m/%d %H:%M:%S') (entrypoint) [ERROR] $*" >&2
  else
    # shellcheck disable=SC2034
    error_message="(entrypoint) [ERROR] $*"
  fi
}

# Print message to log
#
# 1: Message (String)
#
# Code: No
# Echo: No
log() {
  if [[ -z "$is_test" ]] ; then
    echo "$(date +'%Y/%m/%d %H:%M:%S') (entrypoint) $*" >&3
  fi
}

# Exit with given exit code
#
# 1: Exit code (Number)
#
# Code: No
# Echo: No
doExit() {
  if [[ -z "$is_test" ]] ; then
    exit "${1:-0}"
  fi
}

################################################################################

main "$@"
