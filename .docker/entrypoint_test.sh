#!/usr/bin/env bash
# shellcheck disable=SC2028,SC2034,SC2181

########################################################################################

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

CL_NORM="\e[0m"
CL_BOLD="\e[0;${BOLD};49m"
CL_UNLN="\e[0;${UNLN};49m"
CL_RED="\e[0;${RED};49m"
CL_GREEN="\e[0;${GREEN};49m"
CL_YELLOW="\e[0;${YELLOW};49m"
CL_BLUE="\e[0;${BLUE};49m"
CL_MAG="\e[0;${MAG};49m"
CL_CYAN="\e[0;${CYAN};49m"
CL_GREY="\e[0;${GREY};49m"
CL_DARK="\e[0;${DARK};49m"
CL_BL_RED="\e[1;${RED};49m"
CL_BL_GREEN="\e[1;${GREEN};49m"
CL_BL_YELLOW="\e[1;${YELLOW};49m"
CL_BL_BLUE="\e[1;${BLUE};49m"
CL_BL_MAG="\e[1;${MAG};49m"
CL_BL_CYAN="\e[1;${CYAN};49m"
CL_BL_GREY="\e[1;${GREY};49m"

########################################################################################

TMP_PREFIX="/tmp/webkaos-entrypoint-tests"

########################################################################################

is_test=true
verbose=""
error_message=""

########################################################################################

unit.start() {
  if [[ $1 == "-V" || "$1" == "--verbose" ]] ; then
    verbose=true
  fi

  unit.prepare
  
  unit.run "getBucketSizeNoConfigs"
  unit.run "getBucketSize64"
  unit.run "getBucketSize128"
  unit.run "getBucketSize256"
  unit.run "getBucketSize512"

  unit.run "configureBucketSizeDefault"
  unit.run "configureBucketSizeNoConfigs"
  unit.run "configureBucketSizeDisableTuning"
  unit.run "configureBucketSizeIncreased"
  unit.run "configureBucketSizeSedError"

  unit.run "getCPULimitsCG1CpuacctNoLimit"
  unit.run "getCPULimitsCG1CpuacctSmall"
  unit.run "getCPULimitsCG1CpuacctNormal"

  unit.run "getCPULimitsCG1CpusetNoLimit"
  unit.run "getCPULimitsCG1CpusetCustom"

  unit.run "getCPULimitsCG2CpuMaxNoLimit"
  unit.run "getCPULimitsCG2CpuMaxSmall"
  unit.run "getCPULimitsCG2CpuMaxNormal"

  unit.run "getCPULimitsCG2CpusetNoLimit"
  unit.run "getCPULimitsCG2CpusetCustom"

  unit.run "getCPULimitsCG1Cpuacct"
  unit.run "getCPULimitsCG1Cpuset"

  unit.run "getCPULimitsCG2CpuMax"
  unit.run "getCPULimitsCG2Cpuset"

  unit.run "configureProcNumNoCG"
  unit.run "configureProcNumDisableTuning"
  unit.run "configureProcNumSedError"

  unit.run "configureProcNumCG1NoLimits"
  unit.run "configureProcNumCG1Custom"

  unit.run "configureProcNumCG2NoLimits"
  unit.run "configureProcNumCG2Custom"

  unit.run "minCPUVariations"

  unit.run "templatesDefault"
  unit.run "templatesDefaultWithDir"
  unit.run "templatesDisabled"
  unit.run "templatesNoTemplates"
  unit.run "templatesEmptyTemplate"
  
  unit.teardown
}

unit.prepare() {
  unit.show "Starting tests…\n" $BOLD
}

unit.run() {
  # Clear error message before every test
  error_message=""

  if [[ -z "$verbose" ]] ; then
    "test.$*" &> /dev/null

    if [[ $? -ne 0 ]] ; then
      unit.show "  [ ${CL_RED}FAIL${CL_NORM} ] $*"
      unit.teardown 1
    else
      unit.show "  [  ${CL_GREEN}OK${CL_NORM}  ] $*"
    fi
  else
    unit.show "  $*"
    "test.$*"

    if [[ $? -ne 0 ]] ; then
      unit.teardown 1 
    fi

    echo ""
  fi
}

unit.teardown() {
  if [[ $1 -eq 0 || $# -eq 0 ]] ; then
    unit.show "\nAll test passed with success!" $GREEN
  else
    unit.show "\nOne or more tests are failed!" $RED
  fi

  rm -rf "${TMP_PREFIX}"-* &> /dev/null

  exit "${1:-0}"
}

########################################################################################

test.getBucketSizeNoConfigs() {
  local data_dir

  conf_dir=$(unit.mkdir)

  unit.isEqual "$(getBucketSize)" "64"

  return $?
}

test.getBucketSize64() {
  local data_dir

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"

  echo "server {\n  server_name test1.domain.com test2.domain.com test3.domain.com test4.domain.com test5.domain.com test6.domain.com test7.domain.com;\n}\n" > "$data_dir/test1.conf"
  echo "server {\n  server_name 1111222233abcd.test.domain.com;\n}\n" > "$data_dir/test2.conf"

  unit.isEqual "$(getBucketSize)" "64"

  return $?
}

test.getBucketSize128() {
  local data_dir

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"

  echo "server {\n  server_name test.domain.com;\n}\n" > "$data_dir/test1.conf"
  echo "server {\n  server_name 123456789012345678901234567890123456789012345678901234567890.com;\n}\n" > "$data_dir/test2.conf"

  unit.isEqual "$(getBucketSize)" "128"

  return $?
}

test.getBucketSize256() {
  local data_dir

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"

  echo "server {\n  server_name test.domain.com;\n}\n" > "$data_dir/test1.conf"
  echo "server {\n  server_name 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234.com;\n}\n" > "$data_dir/test2.conf"

  unit.isEqual "$(getBucketSize)" "256"

  return $?
}

test.getBucketSize512() {
  local data_dir

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"

  echo "server {\n  server_name test.domain.com;\n}\n" > "$data_dir/test1.conf"
  echo "server {\n  server_name 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890.com;\n}\n" > "$data_dir/test2.conf"

  unit.isEqual "$(getBucketSize)" "512"

  return $?
}

test.configureBucketSizeDefault() {
  local data_dir

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"

  echo "server {\n  server_name test.domain.com;\n}\n" > "$data_dir/test1.conf"

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureBucketSize

  unit.contains "$conf_file" "server_names_hash_bucket_size 64;"

  if [[ $? -ne 0 ]] ; then
    grep 'server_names_hash_bucket_size ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")
  
  configureBucketSize

  unit.contains "$conf_file" "server_names_hash_bucket_size 64;"

  if [[ $? -ne 0 ]] ; then
    grep 'server_names_hash_bucket_size ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  return 0
}

test.configureBucketSizeNoConfigs() {
  local data_dir

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureBucketSize

  unit.contains "$conf_file" "server_names_hash_bucket_size 64;"

  if [[ $? -ne 0 ]] ; then
    grep 'server_names_hash_bucket_size ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")
  
  configureBucketSize

  unit.contains "$conf_file" "server_names_hash_bucket_size 64;"

  if [[ $? -ne 0 ]] ; then
    grep 'server_names_hash_bucket_size ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  return 0
}

test.configureBucketSizeDisableTuning() {
  local data_dir

  WEBKAOS_DISABLE_BUCKET_TUNE=true
  WEBKAOS_HASH_BUCKET_SIZE=128

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureBucketSize

  unit.contains "$conf_file" "server_names_hash_bucket_size 128;"

  if [[ $? -ne 0 ]] ; then
    grep 'server_names_hash_bucket_size ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")
  
  configureBucketSize

  unit.contains "$conf_file" "server_names_hash_bucket_size 128;"

  if [[ $? -ne 0 ]] ; then
    grep 'server_names_hash_bucket_size ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  WEBKAOS_DISABLE_BUCKET_TUNE=""
  WEBKAOS_HASH_BUCKET_SIZE=""

  return 0
}

test.configureBucketSizeIncreased() {
  local data_dir

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"

  echo "server {\n  server_name test.domain.com;\n}\n" > "$data_dir/test1.conf"
  echo "server {\n  server_name 123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234.com;\n}\n" > "$data_dir/test2.conf"

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureBucketSize

  unit.contains "$conf_file" "server_names_hash_bucket_size 256;"

  if [[ $? -ne 0 ]] ; then
    grep 'server_names_hash_bucket_size ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")

  configureBucketSize

  unit.contains "$conf_file" "server_names_hash_bucket_size 256;"

  if [[ $? -ne 0 ]] ; then
    grep 'server_names_hash_bucket_size ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  return 0
}

test.configureBucketSizeSedError() {
  local data_dir

  data_dir=$(unit.mkdir)
  conf_dir="$data_dir"
  conf_file="/__UNKNOWN__"

  WEBKAOS_DISABLE_BUCKET_TUNE=true
  WEBKAOS_HASH_BUCKET_SIZE=128

  configureBucketSize

  unit.hasError "(entrypoint) [ERROR] Can't update configuration file $conf_file"

  if [[ $? -ne 0 ]] ; then
    return 1
  fi

  WEBKAOS_DISABLE_BUCKET_TUNE=""
  WEBKAOS_HASH_BUCKET_SIZE=""

  error_message=""

  configureBucketSize

  unit.hasError "(entrypoint) [ERROR] Can't update configuration file $conf_file"

  return $?
}

test.getCPULimitsCG1CpuacctNoLimit() {
  cg1_cfs_quota_file=$(unit.mkfile "cpu.cfs_quota_us")
  cg1_cfs_period_file=$(unit.mkfile "cpu.cfs_period_us")

  echo "-1" > "$cg1_cfs_quota_file"
  echo "100000" > "$cg1_cfs_period_file"

  unit.isEqual "$(getCPULimitsCG1Cpuacct)" "-1"

  return $?
}

test.getCPULimitsCG1CpuacctSmall() {
  cg1_cfs_quota_file=$(unit.mkfile "cpu.cfs_quota_us")
  cg1_cfs_period_file=$(unit.mkfile "cpu.cfs_period_us")

  # 0.1 CPU
  echo "10000" > "$cg1_cfs_quota_file"
  echo "100000" > "$cg1_cfs_period_file"

  unit.isEqual "$(getCPULimitsCG1Cpuacct)" "1"

  return $?
}

test.getCPULimitsCG1CpuacctNormal() {
  cg1_cfs_quota_file=$(unit.mkfile "cpu.cfs_quota_us")
  cg1_cfs_period_file=$(unit.mkfile "cpu.cfs_period_us")

  # 4.5 CPU
  echo "450000" > "$cg1_cfs_quota_file"
  echo "100000" > "$cg1_cfs_period_file"

  unit.isEqual "$(getCPULimitsCG1Cpuacct)" "5"

  return $?
}

test.getCPULimitsCG1CpusetNoLimit() {
  cg1_effective_cpus_file=$(unit.mkfile "cpuset.effective_cpus")

  # All 8 CPU's
  echo "0-7" > "$cg1_effective_cpus_file"

  unit.isEqual "$(getCPULimitsCG1Cpuset)" "8"

  return $?
}

test.getCPULimitsCG1CpusetCustom() {
  cg1_effective_cpus_file=$(unit.mkfile "cpuset.effective_cpus")

  echo "0-3,6,8,9-12,14" > "$cg1_effective_cpus_file"

  unit.isEqual "$(getCPULimitsCG1Cpuset)" "11"

  return $?
}

test.getCPULimitsCG2CpuMaxNoLimit() {
  cg2_cpu_max_file=$(unit.mkfile "cpu.max")

  echo "max 100000" > "$cg2_cpu_max_file"

  unit.isEqual "$(getCPULimitsCG2CpuMax)" "-1"

  return $?
}

test.getCPULimitsCG2CpuMaxSmall() {
  cg2_cpu_max_file=$(unit.mkfile "cpu.max")

  # 0.15 CPU
  echo "15000 100000" > "$cg2_cpu_max_file"

  unit.isEqual "$(getCPULimitsCG2CpuMax)" "1"

  return $?
}

test.getCPULimitsCG2CpuMaxNormal() {
  cg2_cpu_max_file=$(unit.mkfile "cpu.max")

  # 4.8 CPU
  echo "480000 100000" > "$cg2_cpu_max_file"

  unit.isEqual "$(getCPULimitsCG2CpuMax)" "5"

  return $?
}

test.getCPULimitsCG2CpusetNoLimit() {
  cg2_effective_cpus_file=$(unit.mkfile "cpuset.cpus.effective")

  # All 8 CPU's
  echo "0-7" > "$cg2_effective_cpus_file"

  unit.isEqual "$(getCPULimitsCG2Cpuset)" "8"

  return $?
}

test.getCPULimitsCG2CpusetCustom() {
  cg2_effective_cpus_file=$(unit.mkfile "cpuset.cpus.effective")

  echo "0-3,6,8,9-12,14" > "$cg2_effective_cpus_file"

  unit.isEqual "$(getCPULimitsCG2Cpuset)" "11"

  return $?
}

test.getCPULimitsCG1Cpuacct() {
  cg1_cfs_quota_file=$(unit.mkfile "cpu.cfs_quota_us")
  cg1_cfs_period_file=$(unit.mkfile "cpu.cfs_period_us")
  cg1_effective_cpus_file=$(unit.mkfile "cpuset.effective_cpus")

  echo "50000" > "$cg1_cfs_quota_file"
  echo "100000" > "$cg1_cfs_period_file"
  echo "0-7" > "$cg1_effective_cpus_file"

  unit.isEqual "$(getCPULimitsCG1)" "1"

  return $?
}

test.getCPULimitsCG1Cpuset() {
  cg1_cfs_quota_file=$(unit.mkfile "cpu.cfs_quota_us")
  cg1_cfs_period_file=$(unit.mkfile "cpu.cfs_period_us")
  cg1_effective_cpus_file=$(unit.mkfile "cpuset.effective_cpus")

  echo "-1" > "$cg1_cfs_quota_file"
  echo "100000" > "$cg1_cfs_period_file"
  echo "0-1,3" > "$cg1_effective_cpus_file"

  unit.isEqual "$(getCPULimitsCG1Cpuset)" "3"

  return $?
}

test.getCPULimitsCG2CpuMax() {
  cg2_cpu_max_file=$(unit.mkfile "cpu.max")
  cg2_effective_cpus_file=$(unit.mkfile "cpuset.cpus.effective")

  echo "200000 100000" > "$cg2_cpu_max_file"
  echo "0-7" > "$cg2_effective_cpus_file"

  unit.isEqual "$(getCPULimitsCG2)" "2"

  return $?
}

test.getCPULimitsCG2Cpuset() {
  cg2_cpu_max_file=$(unit.mkfile "cpu.max")
  cg2_effective_cpus_file=$(unit.mkfile "cpuset.cpus.effective")

  echo "800000 100000" > "$cg2_cpu_max_file"
  echo "0-1,4" > "$cg2_effective_cpus_file"

  unit.isEqual "$(getCPULimitsCG2)" "3"

  return $?
}

test.configureProcNumNoCG() {
  local system_procs

  system_procs=$(getNumProc)

  cg1_cfs_quota_file=""
  cg1_cfs_period_file=""
  cg1_effective_cpus_file=""
  cg2_cpu_max_file=""
  cg2_effective_cpus_file=""

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      $system_procs;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      $system_procs;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  return 0
}

test.configureProcNumDisableTuning() {
  local system_procs

  system_procs=$(getNumProc)

  WEBKAOS_DISABLE_PROC_TUNE=true

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      auto;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      auto;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  WEBKAOS_DISABLE_PROC_TUNE=""

  return 0
}

test.configureProcNumSedError() {
  cg1_cfs_quota_file=""
  cg1_cfs_period_file=""
  cg1_effective_cpus_file=""
  cg2_cpu_max_file=""
  cg2_effective_cpus_file=""

  conf_file="__UNKNOWN__"

  WEBKAOS_DISABLE_PROC_TUNE=true

  configureProcNum

  unit.hasError "(entrypoint) [ERROR] Can't update configuration file $conf_file"

  if [[ $? -ne 0 ]] ; then
    return 1
  fi

  WEBKAOS_DISABLE_PROC_TUNE=""

  error_message=""

  configureProcNum

  unit.hasError "(entrypoint) [ERROR] Can't update configuration file $conf_file"

  return $?
}

test.configureProcNumCG1NoLimits() {
  local system_procs

  system_procs=$(getNumProc)

  cg1_cfs_quota_file=$(unit.mkfile "cpu.cfs_quota_us")
  cg1_cfs_period_file=$(unit.mkfile "cpu.cfs_period_us")
  cg1_effective_cpus_file=$(unit.mkfile "cpuset.effective_cpus")
  cg2_cpu_max_file=""
  cg2_effective_cpus_file=""

  echo "-1" > "$cg1_cfs_quota_file"
  echo "100000" > "$cg1_cfs_period_file"
  echo "0-31" > "$cg1_effective_cpus_file"

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      $system_procs;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      $system_procs;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  return 0
}

test.configureProcNumCG1Custom() {
  cg1_cfs_quota_file=$(unit.mkfile "cpu.cfs_quota_us")
  cg1_cfs_period_file=$(unit.mkfile "cpu.cfs_period_us")
  cg1_effective_cpus_file=$(unit.mkfile "cpuset.effective_cpus")
  cg2_cpu_max_file=""
  cg2_effective_cpus_file=""

  echo "200000" > "$cg1_cfs_quota_file"
  echo "100000" > "$cg1_cfs_period_file"
  echo "0-31" > "$cg1_effective_cpus_file"

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      2;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      2;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  return 0
}

test.configureProcNumCG2NoLimits() {
  local system_procs

  system_procs=$(getNumProc)

  cg1_cfs_quota_file=""
  cg1_cfs_period_file=""
  cg1_effective_cpus_file=""
  cg2_cpu_max_file=$(unit.mkfile "cpu.max")
  cg2_effective_cpus_file=$(unit.mkfile "cpuset.cpus.effective")

  echo "max 100000" > "$cg2_cpu_max_file"
  echo "0-31" > "$cg2_effective_cpus_file"

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      $system_procs;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      $system_procs;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  return 0
}

test.configureProcNumCG2Custom() {
  cg1_cfs_quota_file=""
  cg1_cfs_period_file=""
  cg1_effective_cpus_file=""
  cg2_cpu_max_file=$(unit.mkfile "cpu.max")
  cg2_effective_cpus_file=$(unit.mkfile "cpuset.cpus.effective")

  echo "200000 100000" > "$cg2_cpu_max_file"
  echo "0-31" > "$cg2_effective_cpus_file"

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker.conf" "webkaos-docker.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      2;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  conf_file=$(unit.mkcopy "../SOURCES/webkaos-docker-unprivileged.conf" "webkaos-docker-unprivileged.conf")

  configureProcNum

  unit.contains "$conf_file" "worker_processes      2;"

  if [[ $? -ne 0 ]] ; then
    grep 'worker_processes ' "$conf_file" | sed 's/^/\n    /'
    return 1
  fi

  return 0
}

test.minCPUVariations() {
  if ! unit.isEqual "$(minCPU '-1' '3')" "3" ; then
    return 1
  fi

  if ! unit.isEqual "$(minCPU '3' '-1')" "3" ; then
    return 1
  fi

  if ! unit.isEqual "$(minCPU '2' '8')" "2" ; then
    return 1
  fi

  if ! unit.isEqual "$(minCPU '6' '2')" "2" ; then
    return 1
  fi

  # Minimal number of CPU is 1
  if ! unit.isEqual "$(minCPU '6' '0')" "1" ; then
    return 1
  fi

  return 0
}

test.templatesDefault() {
  templates_dir=$(unit.mkdir)
  conf_dir=$(unit.mkdir)

cat << EOF > "$templates_dir/mytest.conf.template"
server {
  listen 443 ssl http2;
  server_name \${MYHOST}.com;

  location / {
    root /srv/\$MYHOST/data;
  }
}
EOF

  export MYHOST="mysuperhost"

  renderTemplates

  if ! unit.isExist "$conf_dir/mytest.conf" ; then
    return 1
  fi

  if ! unit.contains "$conf_dir/mytest.conf" "server_name mysuperhost.com" ; then
    return 1
  fi

  if ! unit.contains "$conf_dir/mytest.conf" "root /srv/mysuperhost/data" ; then
    return 1
  fi

  return 0
}

test.templatesDefaultWithDir() {
  templates_dir=$(unit.mkdir)
  conf_dir=$(unit.mkdir)

  mkdir "${templates_dir}/websites"

cat << EOF > "$templates_dir/websites/mytest.conf.template"
server {
  listen 443 ssl http2;
  server_name \${MYHOST}.com;

  location / {
    root /srv/\$MYHOST/data;
  }
}
EOF

  export MYHOST="mysuperhost"

  renderTemplates

  if ! unit.isExist "$conf_dir/websites" ; then
    return 1
  fi

  if ! unit.isExist "$conf_dir/websites/mytest.conf" ; then
    return 1
  fi

  if ! unit.contains "$conf_dir/websites/mytest.conf" "server_name mysuperhost.com" ; then
    return 1
  fi

  if ! unit.contains "$conf_dir/websites/mytest.conf" "root /srv/mysuperhost/data" ; then
    return 1
  fi

  return 0
}

test.templatesDisabled() {
  templates_dir=$(unit.mkdir)
  conf_dir=$(unit.mkdir)

cat << EOF > "$templates_dir/mytest.conf.template"
server {
  listen 443 ssl http2;
  server_name \${MYHOST}.com;

  location / {
    root /srv/\$MYHOST/data;
  }
}
EOF

  export MYHOST="mysuperhost"

  WEBKAOS_DISABLE_TEMPLATES=true

  renderTemplates

  if ! unit.isNotExist "$conf_dir/mytest.conf" ; then
    return 1
  fi

  WEBKAOS_DISABLE_TEMPLATES=""

  return 0
}

test.templatesNoTemplates() {
  templates_dir=$(unit.mkdir)
  conf_dir=$(unit.mkdir)

  renderTemplates

  if ! unit.isEqual "$(ls -1 "$conf_dir" | wc -l)" "0" ; then
    return 1
  fi

  return 0
}

test.templatesEmptyTemplate() {
  templates_dir=$(unit.mkdir)
  conf_dir=$(unit.mkdir)

  touch "$templates_dir/mytest.conf.template"

  renderTemplates

  if ! unit.isEqual "$(ls -1 "$conf_dir" | wc -l)" "0" ; then
    return 1
  fi

  return 0
}

########################################################################################

# Check if two values are equal
#
# 1: First value (String)
# 2: Second value (String)
#
# Code: Yes
# Echo: No
unit.isEqual() {
  if [[ "$1" != "$2" ]] ; then
    unit.show "  ${CL_RED}•${CL_NORM} \"$1\" ≠ \"$2\""
    return 1
  fi

  unit.show "  ${CL_GREEN}•${CL_NORM} ${CL_GREY}\"$1\" = \"$2\"${CL_NORM}"
  return 0
}

# Check if two values are NOT equal
#
# 1: First value (String)
# 2: Second value (String)
#
# Code: Yes
# Echo: No
unit.isNotEqual() {
  if [[ "$1" == "$2" ]] ; then
    unit.show "  ${CL_RED}•${CL_NORM} \"$1\" ≠ \"$2\""
    return 1
  fi

  unit.show "  ${CL_GREEN}•${CL_NORM} ${CL_GREY}\"$1\" = \"$2\"${CL_NORM}"
  return 0
}

# Check if file contains given substring
#
# 1: File path (String)
# 2: Sub-string to search (String)
#
# Code: Yes
# Echo: No
unit.contains() {
  local filename

  filename=$(unit.formatPath "$1")

  if ! grep -q "$2" "$1" ; then
    unit.show "  ${CL_RED}•${CL_NORM} $filename doesn't contain \"$2\""
    return 1
  fi

  unit.show "  ${CL_GREEN}•${CL_NORM} ${CL_GREY}$filename contains \"$2\"${CL_NORM}"
  return 0
}

# Check if file or directory exists
#
# 1: Path (String)
#
# Code: Yes
# Echo: No
unit.isExist() {
  local obj

  obj=$(unit.formatPath "$1")

  if [[ ! -e "$1" ]] ; then
    unit.show "  ${CL_RED}•${CL_NORM} Object \"$obj\" doesn't exist"
    return 1
  fi

  unit.show "  ${CL_GREEN}•${CL_NORM} ${CL_GREY}Object \"$obj\" exists${CL_NORM}"
  return 0
}

# Check if file or directory doesn't exist
#
# 1: Path (String)
#
# Code: Yes
# Echo: No
unit.isNotExist() {
  local obj

  obj=$(unit.formatPath "$1")

  if [[ -e "$1" ]] ; then
    unit.show "  ${CL_RED}•${CL_NORM} Object \"$obj\" exists"
    return 1
  fi

  unit.show "  ${CL_GREEN}•${CL_NORM} ${CL_GREY}Object \"$obj\" doesn't exist${CL_NORM}"
  return 0
}

# Check if error message contains given message
#
# 1: Error text (String)
#
# Code: No
# Echo: No
unit.hasError() {
  if [[ "$error_message" != "$1" ]] ; then
    unit.show "  ${CL_RED}•${CL_NORM} \"$1\" ≠ \"$error_message\""
    return 1
  fi

  unit.show "  ${CL_GREEN}•${CL_NORM} ${CL_GREY}${error_message}${CL_NORM}"
  return 0
}

# Create temporary directory
#
# Code: No
# Echo: Path to directory (String)
unit.mkdir() {
  mktemp -d "$TMP_PREFIX-XXXXXXXXX"
}

# Create temporary file
#
# 1: File name (String)
#
# Code: No
# Echo: Path to file (String)
unit.mkfile() {
  local tmp_dir

  tmp_dir=$(unit.mkdir)
  touch "${tmp_dir}/$1"

  echo "${tmp_dir}/$1"
}

# Create temporary copy of file
#
# 1: Source file (String)
# 2: File name (String)
#
# Code: No
# Echo: Path to file (String)
unit.mkcopy() {
  local tmp_dir

  tmp_dir=$(unit.mkdir)
  cat "$1" > "${tmp_dir}/$2"

  echo "${tmp_dir}/$2"
}

# Format path to file or directory in temporary directory
#
# 1: Path (String)
#
# Code: No
# Echo: Formatted path (String)
unit.formatPath() {
  echo "${1##$TMP_PREFIX-?????????/}"
}

########################################################################################

# Show message
#
# 1: Message (String)
# 2: Message color (Number) [Optional]
#
# Code: No
# Echo: No
unit.show() {
  if [[ -n "$2" ]] ; then
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
unit.error() {
  unit.show "$*" $RED 1>&2
}

########################################################################################

source "entrypoint.sh"

unit.start "$@"
