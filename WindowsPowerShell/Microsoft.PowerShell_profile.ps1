# load scripts from the script dir
$PoshScriptsDir = 'F:\Source\my-projects\Scripticus\Posh\Scripts'




# load scripts    ##############################################################
# load all scripts ## Get-ChildItem "${PoshScriptsDir}\*.ps1" | % {.$_} 
$scripts = @('downloader/Get-Download.ps1'
           , 'Clear-SpecFlowCache.ps1'
           , 'Web-Functions.ps1'
           , 'Restart-Powershell.ps1'
           , 'nuget-functions.ps1'
           , 'Helpfull-Console-Utils.ps1'
           , 'Take-Ownership.ps1'
           , 'File-Access.ps1'
		   , 'docker-helper.ps1'
		   , 'msbuild-functions.ps1')

$scripts | % { . $(Join-Path $PoshScriptsDir $_) } 

$more_scripts = @()
$more_scripts += "F:\source\my-projects\syeadon-miscellany\git\git-helpers\git-functions.ps1"
$more_scripts += "F:\source\my-projects\syeadon-miscellany\git\gitlab-helpers\gitlab-functions.ps1"
$more_scripts | % { . $_ } 

# not needed anymore - only used it for the prompt customisation
#if(!(get-module posh-git -ListAvailable)){
#  Install-Module posh-git
#}else{
#  Import-Module posh-git
#}

# set up icons
Import-Module -Name Terminal-Icons

# set up read line
Import-Module PSReadLine
Set-PSReadLineOption -PredictionSource History

# better navigation
Import-Module z

# set up promt ui
Set-PoshPrompt -Theme Star

# set up aliases
Set-Alias -name g -value git
set-alias -name vim -value C:\tools\neovim\neovim\bin\nvim.exe


# THIS NEEDS TO STAY AT THEN END OF THE PROFILE, IT IS USED BY THE RELOAD FUNC #
$parentProcessId = (Get-WmiObject Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parentProcessName = (Get-WmiObject Win32_Process -Filter "ProcessId=$parentProcessId").ProcessName

if ($host.Name -eq 'ConsoleHost') {
    if (-not($parentProcessName -eq 'powershell.exe')) {
        Invoke-PowerShell
    }
}

# Chocolatey profile
$ChocolateyProfile = "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
if (Test-Path($ChocolateyProfile)) {
  Import-Module "$ChocolateyProfile"
}