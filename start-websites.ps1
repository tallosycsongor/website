[CmdletBinding()]
param(
    [switch]$All
)

$ErrorActionPreference = 'Stop'

$websites = @(
    [PSCustomObject]@{ Name = 'OPSENTRA';        Folder = 'nexorawebsite'; Port = 3000 }
    [PSCustomObject]@{ Name = 'Neon Pulse';      Folder = 'neon-pulse';    Port = 3001 }
    [PSCustomObject]@{ Name = 'Csiperkegomba';   Folder = 'csiperkegomba'; Port = 3002 }
    [PSCustomObject]@{ Name = 'Csaladi indulo';  Folder = 'csaladiindulo'; Port = 3003 }
    [PSCustomObject]@{ Name = 'GyogyszerVan';    Folder = 'gyogyszervan';  Port = 3004 }
    [PSCustomObject]@{ Name = 'Helyi Figyelo';   Folder = 'helyifigyelo';  Port = 3005 }
    [PSCustomObject]@{ Name = 'Kosaror';         Folder = 'kosaror';       Port = 3006 }
    [PSCustomObject]@{ Name = 'Mikor jar le?';   Folder = 'mikorjarle';    Port = 3007 }
    [PSCustomObject]@{ Name = 'PC Orszem';       Folder = 'homersekletfigyelo'; Port = 3008 }
    [PSCustomObject]@{ Name = 'LocsolOr';         Folder = 'locsolor';           Port = 3009 }
    [PSCustomObject]@{ Name = 'OddsPilot';       Folder = 'oddsagent';          Port = 3010 }
    [PSCustomObject]@{ Name = 'Irattar';         Folder = 'dokumentum-asszisztens'; Port = 3011 }
)

function Test-PortInUse {
    param([int]$Port)

    $listeners = [System.Net.NetworkInformation.IPGlobalProperties]::GetIPGlobalProperties().GetActiveTcpListeners()
    return $null -ne ($listeners | Where-Object { $_.Port -eq $Port } | Select-Object -First 1)
}

function Start-Website {
    param([PSCustomObject]$Website)

    $projectPath = Join-Path $PSScriptRoot $Website.Folder
    $packageFile = Join-Path $projectPath 'package.json'

    if (-not (Test-Path -LiteralPath $packageFile)) {
        Write-Host "HIBA: Nem talalhato: $packageFile" -ForegroundColor Red
        return
    }

    if (Test-PortInUse -Port $Website.Port) {
        Write-Host "$($Website.Name) mar fut vagy a $($Website.Port)-as port foglalt." -ForegroundColor Yellow
        return
    }

    if ($Website.Folder -eq 'homersekletfigyelo') {
        $dashboardLauncher = Join-Path $projectPath 'start-dashboard.ps1'
        Start-Process powershell.exe -Verb RunAs -ArgumentList @(
            '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', ('"' + $dashboardLauncher + '"')
        )
        Write-Host "$($Website.Name) inditasa folyamatban: http://localhost:$($Website.Port)" -ForegroundColor Green
        return
    }

    $windowTitle = "$($Website.Name) - localhost:$($Website.Port)"
    $command = "title $windowTitle && npm.cmd run dev"
    Start-Process -FilePath 'cmd.exe' -ArgumentList @('/d', '/k', $command) -WorkingDirectory $projectPath
    Write-Host "$($Website.Name) inditva: http://localhost:$($Website.Port)" -ForegroundColor Green
}

function Start-AllWebsites {
    foreach ($website in $websites) {
        Start-Website -Website $website
    }
}

if ($All) {
    Start-AllWebsites
    exit 0
}

while ($true) {
    Clear-Host
    Write-Host 'Weboldal indito' -ForegroundColor Cyan
    Write-Host '---------------' -ForegroundColor Cyan

    for ($index = 0; $index -lt $websites.Count; $index++) {
        $website = $websites[$index]
        $status = if (Test-PortInUse -Port $website.Port) { 'FUT' } else { 'all' }
        $color = if ($status -eq 'FUT') { 'Green' } else { 'DarkGray' }
        Write-Host ("{0}. {1,-18} http://localhost:{2} [{3}]" -f ($index + 1), $website.Name, $website.Port, $status) -ForegroundColor $color
    }

    Write-Host ''
    Write-Host 'A. Osszes inditasa'
    Write-Host 'F. Allapot frissitese'
    Write-Host 'Q. Kilepes'
    Write-Host ''

    $choice = (Read-Host 'Valassz').Trim()

    if ($choice -match '^[qQ]$') {
        break
    }

    if ($choice -match '^[aA]$') {
        Start-AllWebsites
        Write-Host 'Nyomj Entert a menuhoz...' -ForegroundColor DarkGray
        [void](Read-Host)
        continue
    }

    if ($choice -match '^[fF]$') {
        continue
    }

    $selectedNumber = 0
    if ([int]::TryParse($choice, [ref]$selectedNumber) -and $selectedNumber -ge 1 -and $selectedNumber -le $websites.Count) {
        Start-Website -Website $websites[$selectedNumber - 1]
    }
    else {
        Write-Host 'Ervenytelen valasztas.' -ForegroundColor Red
    }

    Write-Host 'Nyomj Entert a menuhoz...' -ForegroundColor DarkGray
    [void](Read-Host)
}
