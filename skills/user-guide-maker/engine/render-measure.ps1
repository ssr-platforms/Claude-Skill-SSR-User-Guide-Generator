param([string]$Deck, [string]$OutDir, [string]$Json, [int]$Width = 1600)
$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
Get-ChildItem $OutDir -Filter *.png | Remove-Item
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($Deck, -1, 0, 0)
$h = [int]($Width * $p.PageSetup.SlideHeight / $p.PageSetup.SlideWidth)
$m = @{}
for ($i = 1; $i -le $p.Slides.Count; $i++) {
  $s = $p.Slides.Item($i)
  $s.Export((Join-Path $OutDir ("slide-{0:D2}.png" -f $i)), "PNG", $Width, $h)
  $d = @{}
  foreach ($sh in $s.Shapes) { if ($sh.Name -like "Desc *") { $d[$sh.Name] = $sh.TextFrame.TextRange.BoundHeight } }
  $m["$i"] = $d
}
$p.Close()
if ($app.Presentations.Count -eq 0) { $app.Quit() }
$m | ConvertTo-Json -Depth 4 | Set-Content -Encoding UTF8 $Json
"done"
