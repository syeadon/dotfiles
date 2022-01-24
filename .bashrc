source ~/.common-functions
source ~/.git-functions
source ~/.gitlab-functions

alias ll='ls -lah --color=always'
alias gh='history|grep'
alias matrix='/F/Source/my-projects/Scripticus/shell/matrix.sh'
alias reload='source ~/.bashrc'

alias gmg='/F/Source/my-projects/syeadon-miscellany/git/scripts/GitMeGoing.sh'
alias gds='/F/Source/my-projects/syeadon-miscellany/git/git-helpers/GitDirectoryStatus.sh'
alias gfd='/F/Source/my-projects/syeadon-miscellany/git/git-helpers/GitFetch.sh'

alias egrep='grep -Ei'

alias npp='npp'

alias g='git'
# should add auto completion back into g ...
# see: https://stackoverflow.com/questions/9869227/git-autocomplete-in-bash-aliases
__git_complete g __git_main


alias glmr='mr'
alias glpl='pl'

alias brc='bat ~/.bashrc'
alias grc='bat ~/.gitconfig'


# add auto completion back into git branches
# see: https://levelup.gitconnected.com/upgrade-your-command-line-for-software-development-with-git-autocomplete-1fb946c14750
test -f ~/.git-completion.bash && . $_


# Theme
THEME=$HOME/.bash/themes/git_bash_windows_powerline/theme.bash
if [ -f $THEME ]; then
  . $THEME
fi
unset THEME
