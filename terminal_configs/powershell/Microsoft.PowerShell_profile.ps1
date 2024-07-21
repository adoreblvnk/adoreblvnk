# C:\Users\<username>\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1

$isAdministrator = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]'Administrator')
function Prompt {
    $currentDir = [regex]::match($pwd, '\\(?:.(?!\\))+$').Groups[0].Value
    $currentDir = $currentDir.SubString(1, $currentDir.Length - 1)
    $currentDir = "$env:UserName@" + "$env:ComputerName " + $currentDir

    $prefix = ''
    if ($isAdministrator) {
        $prefix = 'ADMIN: '
    }
    $Host.UI.RawUI.WindowTitle = "$prefix$currentDir"

    $prompt = '$'
    if ($isAdministrator) {
        $prompt = '#'
    }
    return "$currentDir $prompt "
}
