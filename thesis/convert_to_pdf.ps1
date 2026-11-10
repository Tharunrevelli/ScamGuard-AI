param(
    [string]$docxPath,
    [string]$pdfPath
)

$resolvedDocx = (Resolve-Path $docxPath).Path
if (-not $pdfPath) {
    $resolvedPdf = [System.IO.Path]::ChangeExtension($resolvedDocx, '.pdf')
} else {
    $resolvedPdf = [System.IO.Path]::GetFullPath($pdfPath)
}

Write-Output "Converting $resolvedDocx to $resolvedPdf ..."

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($resolvedDocx)
    $wdFormatPDF = 17
    $doc.SaveAs([ref]$resolvedPdf, [ref]$wdFormatPDF)
    $doc.Close([ref]0)
    Write-Output "Successfully generated: $resolvedPdf"
} catch {
    Write-Error "Failed to export PDF: $_"
    exit 1
} finally {
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
}
