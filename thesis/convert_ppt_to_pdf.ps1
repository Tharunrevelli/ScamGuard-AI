param(
    [string]$pptxPath,
    [string]$pdfPath
)

$resolvedPptx = (Resolve-Path $pptxPath).Path
if (-not $pdfPath) {
    $resolvedPdf = [System.IO.Path]::ChangeExtension($resolvedPptx, '.pdf')
} else {
    $resolvedPdf = [System.IO.Path]::GetFullPath($pdfPath)
}

Write-Output "Converting $resolvedPptx to $resolvedPdf ..."

$ppt = New-Object -ComObject PowerPoint.Application
try {
    # Open presentation (ReadOnly = -1, Untitled = 0, WithWindow = 0)
    $pres = $ppt.Presentations.Open($resolvedPptx, -1, 0, 0)
    # 32 = ppSaveAsPDF
    $pres.SaveAs($resolvedPdf, 32)
    $pres.Close()
    Write-Output "Successfully generated: $resolvedPdf"
} catch {
    Write-Error "Failed to export PDF: $_"
    exit 1
} finally {
    $ppt.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
}
