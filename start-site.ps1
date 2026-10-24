param([switch]$CheckOnly)
$ErrorActionPreference = 'Stop'
$siteDirectory = $PSScriptRoot
$docsDirectory = Join-Path $siteDirectory 'docs'
$cacheDirectory = Join-Path $siteDirectory '.cache'
$pythonExecutable = 'C:\Users\lenovo\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$previewUrl = 'http://localhost:3000/'
$expectedTitle = [regex]::Match([IO.File]::ReadAllText((Join-Path $docsDirectory 'index.html')), '<title>(.*?)</title>').Groups[1].Value
function Get-PreviewResponse {
    try { return Invoke-WebRequest -Uri 'http://127.0.0.1:3000/' -TimeoutSec 3 -UseBasicParsing } catch { return $null }
}
$response = Get-PreviewResponse
if ($response -and -not $response.Content.Contains("<title>$expectedTitle</title>")) {
    throw 'Port 3000 belongs to another application. It was not stopped or replaced.'
}
if (-not $response) {
    if ($CheckOnly) { throw 'The preview server is not running.' }
    if (-not (Test-Path -LiteralPath $pythonExecutable)) { throw 'The configured Python runtime is missing.' }
    New-Item -ItemType Directory -Path $cacheDirectory -Force | Out-Null
    $server = Start-Process -FilePath $pythonExecutable -ArgumentList "-m http.server 3000 --bind 127.0.0.1 --directory `"$docsDirectory`"" -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $cacheDirectory 'static.stdout.log') -RedirectStandardError (Join-Path $cacheDirectory 'static.stderr.log')
    [IO.File]::WriteAllText((Join-Path $cacheDirectory 'static.pid'), [string]$server.Id)
    for ($attemptNumber = 0; $attemptNumber -lt 20; $attemptNumber++) {
        $response = Get-PreviewResponse
        if ($response) { break }
        Start-Sleep -Milliseconds 200
    }
    if (-not $response -or -not $response.Content.Contains("<title>$expectedTitle</title>")) { throw 'The local preview did not start. See .cache/static.stderr.log.' }
}
if ($CheckOnly) { Write-Output '637 preview is ready on localhost:3000.' } else { Start-Process $previewUrl }
