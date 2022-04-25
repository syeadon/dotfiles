# load scripts from the script dir
$PoshScriptsDir = 'F:\Source\my-projects\Scripticus\Posh\Scripts'




# load scripts    ##############################################################
# load all scripts ## Get-ChildItem "${PoshScriptsDir}\*.ps1" | % {.$_} 
$scripts = @('downloader/Get-Download.ps1'
           , 'Clear-SpecFlowCache.ps1'
           , 'Web-Functions.ps1'
           , 'Restart-Powershell.ps1'
		   , 'nuget.ps1'
		   , 'Take-Ownership.ps1'
		   , 'Helpfull-Console-Utils.ps1')
$scripts | % { . $(Join-Path $PoshScriptsDir $_) } 




# THIS NEEDS TO STAY AT THEN END OF TEH PROFILE, IT IS USED BY THE RELOAD FUNC #
$parentProcessId = (Get-WmiObject Win32_Process -Filter "ProcessId=$PID").ParentProcessId
$parentProcessName = (Get-WmiObject Win32_Process -Filter "ProcessId=$parentProcessId").ProcessName

if ($host.Name -eq 'ConsoleHost') {
    if (-not($parentProcessName -eq 'powershell.exe')) {
        Invoke-PowerShell
    }
}
