#alias fork="/C/Users/syeadon/AppData/Local/Fork/Fork.exe '$(pwd -W)'"
alias ll='ls -lah --color=always'
alias gh='history|grep'
alias matrix='/F/Source/my-projects/Scripticus/shell/matrix.sh'
alias reload='source ~/.bashrc'

alias gmg='/F/Source/my-projects/syeadon-miscellany/GitHelpers/GitMeGoing.sh'
alias gsd='/F/Source/my-projects/syeadon-miscellany/GitHelpers/GitDirectoryStatus.sh'
alias gfd='/F/Source/my-projects/syeadon-miscellany/GitHelpers/GitFetch.sh'

alias g='git'

alias glmr='mr'
alias glpl='pl'


fork() {
  if [ "$#" -ne 1 ] || [ "$1" -eq '.' ]; then
    path=$(pwd -W)
  else
    #to do fix linux path issues
    linuxPath=$(readlink -f $1)
    path=$1
  fi

  #echo "/C/Users/syeadon/AppData/Local/Fork/Fork.exe '$path'"
  /C/Users/syeadon/AppData/Local/Fork/Fork.exe "$path"
}

show-pipeline() {
  original_working_dir=$(pwd)

  if [ "$#" -ne 1 ]; then
    echo "Opening gitlab pipeline for current working directory"
  else
    path="$1"
    echo "Opening gitlab pipeline for the supplied directory: $path"
    cd $path
  fi

  baseurl=$(git remote show origin | grep -oP "(?<=Fetch URL:\s).*(?=\.git)")

  url="${baseurl}/pipelines"

  echo "$url"
  start $url

  cd $original_working_dir
}

show-merge-requests() {
  original_working_dir=$(pwd)

  if [ "$#" -ne 1 ]; then
    echo "Opening gitlab merge requests for current working directory"
  else
    path="$1"
    echo "Opening gitlab merge requests for the supplied directory: $path"
    cd $path
  fi

  baseurl=$(git remote show origin | grep -oP "(?<=Fetch URL:\s).*(?=\.git)")

  url="${baseurl}/-/merge_requests"

  echo "$url"
  start $url

  cd $original_working_dir
}

new-merge-request() {
  # remote:   http://eqcs-gitlab.icecloudnp.onmicrosoft.com/icenet-tools/data-migration/-/merge_requests/new?merge_request%5Bsource_branch%5D=feature%2Fice-24716

  original_working_dir=$(pwd)

  if [ "$#" -ne 1 ]; then
    echo "Using current working directory"
  else
    path="$1"
    echo "moving to the supplied directory: '$path'"
    cd $path
  fi

  baseurl=$(git remote show origin | grep -oP "(?<=Fetch URL:\s).*(?=\.git)")

  currentBranch=$(git branch --show-current | sed 's/\//%2F/g;')

  url="${baseurl}/-/merge_requests/new?merge_request%5Bsource_branch%5D=${currentBranch}"

  echo "$url"
  start $url

  cd $original_working_dir
}

mr(){
  if [[ "$1" == "list" ]]; then
    show-merge-requests
  elif [[ "$1" == "new" ]]; then
    new-merge-request
  elif [[ $# -eq 0 ]]; then
    echo "No verb supplied"
  else
    echo "Unrecognised verb $1"
  fi
}

pl(){
  if [[ "$1" == "list" ]]; then
    show-pipeline
  elif [[ $# -eq 0 ]]; then
    echo "No verb supplied"
  else
    echo "Unrecognised verb $1"
  fi
}

# Theme
THEME=$HOME/.bash/themes/git_bash_windows_powerline/theme.bash
if [ -f $THEME ]; then
  . $THEME
fi
unset THEME
