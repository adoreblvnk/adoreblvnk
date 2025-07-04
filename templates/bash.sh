#!/usr/bin/env bash
set -euo pipefail

# global variables
readonly VAR_1=0.0.1
# set in _set_global_var()
DYNAMIC_VAR=""

# ----- PRINT FUNCTIONS -----

# Set text colours if supported.
# Arguments:
#   $1: boolean indicating if colours is enabled
colours() {
  NC="" BOLD="" RED="" GREEN="" YELLOW="" BLUE="" MAGENTA="" CYAN=""
  if [[ $(tput colors) -ge 8 ]] && [[ $1 == true ]]; then
    NC=$(tput sgr0) BOLD=$(tput bold) # text reset (select graphic representation default)
    RED=$(tput setaf 1) GREEN=$(tput setaf 2) YELLOW=$(tput setaf 3) BLUE=$(tput setaf 4) MAGENTA=$(tput setaf 5) CYAN=$(tput setaf 6)
  fi
}

_info_msg() { printf "%s\n" "${BOLD}${BLUE}Info:${NC} $1"; }

_success_msg() { printf "%s\n" "${BOLD}${GREEN}Success:${NC} $1"; }

_warning_msg() { printf "%s\n" "${BOLD}${YELLOW}Warning:${NC} $1"; }

_error_msg() { printf "%s\n" "${BOLD}${RED}Error:${NC} $1" && exit 1; }

_usage() {
  cat <<EOF
<bash_template> description

${YELLOW}Usage:${NC} <bash_template> ${CYAN}[Options]${NC} ${CYAN}[Command]${NC}

${YELLOW}Options:${NC}
  ${GREEN}-n, --no-colour  ${NC} Do not output any colour. Useful when redirecting output to a logfile
  ${GREEN}-h, --help       ${NC} Print help information

${YELLOW}Commands:${NC}
  ${GREEN}command 1 ${NC} Description of command 1

${YELLOW}Example:${NC} <bash_template> ${CYAN}--no-colour${NC}

${YELLOW}Project Homepage:${NC} ${MAGENTA}https://github.com/adoreblvnk/${NC}
EOF
}

# ----- SET GLOBAL VARIABLES -----

# Set complex global variables that require commands to be set.
# Globals:
#   DYNAMIC_VAR
_set_global_var() { DYNAMIC_VAR="some value"; }

# ----- HELPERS -----

# ----- OPTIONS -----

# ----- COMMANDS -----

# Example command function.
# Arguments:
#   $1: Argument
command_1() {
  [[ -z "${1:-}" ]] && _error_msg "Argument not supplied"
  _info_msg "Argument: $1"
}

# ----- MAIN -----

main() {
  colours true # PRINT FUNCTIONS
  _set_global_var

  [[ $# -gt 0 ]] || { _usage && _error_msg "No argument(s)"; }

  while [[ $# -gt 0 ]]; do
    case $1 in
      -h | --help) _usage && exit ;;
      # OPTIONS
      -n | --no-colour) colours false ;;
      # COMMANDS
      command_1) command_1 "$2"; shift ;;
      *) _usage && _error_msg "Invalid argument(s)" ;;
    esac; shift
  done
}

main "$@"
