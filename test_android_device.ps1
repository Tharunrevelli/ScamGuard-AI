# Automated On-Device Testing & Verification Script for ScamGuard PRO
Param(
    [switch]$UninstallOnFinish = $false
)

$adb = "C:\Users\revelli tharun\AppData\Local\Android\Sdk\platform-tools\adb.exe"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "     ScamGuard PRO - Physical Android Device Test Suite   " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Device Info
$model = (& $adb shell getprop ro.product.model).Trim()
$osVer = (& $adb shell getprop ro.build.version.release).Trim()
$sdkVer = (& $adb shell getprop ro.build.version.sdk).Trim()
Write-Host "[OK] Connected to: $model (Android $osVer, SDK $sdkVer)" -ForegroundColor Cyan

# 2. Reverse Port
Write-Host "[1/5] Configuring USB reverse proxy (tcp:8000 -> localhost:8000)..." -ForegroundColor Green
& $adb reverse tcp:8000 tcp:8000
Write-Host "[OK] USB proxy configured." -ForegroundColor Cyan

# 3. Install APK
Write-Host "[2/5] Installing ScamGuard APK (web/ScamGuard.apk)..." -ForegroundColor Green
& $adb install -r -d "web\ScamGuard.apk"

# 4. Grant Permissions
Write-Host "[3/5] Granting security permissions via ADB..." -ForegroundColor Green
& $adb shell pm grant com.scamguard.app android.permission.RECEIVE_SMS
& $adb shell pm grant com.scamguard.app android.permission.POST_NOTIFICATIONS
& $adb shell appops set com.scamguard.app SYSTEM_ALERT_WINDOW allow
Write-Host "[OK] Permissions granted." -ForegroundColor Cyan

# 5. Launch App
Write-Host "[4/5] Launching ScamGuard PRO..." -ForegroundColor Green
& $adb shell am start -n com.scamguard.app/.MainActivity
Start-Sleep -Seconds 2

# Clear logcat
& $adb logcat -c

# 6. Execute Test Scenarios
Write-Host "[5/5] Executing On-Device Test Scenarios..." -ForegroundColor Green

# Test 1: Benign
Write-Host ">>> [TEST 1] Benign Personal Message..." -ForegroundColor Yellow
& $adb shell am broadcast -a com.scamguard.app.TEST_SMS -n com.scamguard.app/.SmsReceiver --es sender "+15551234567" --es text "Hey, are you free for lunch today at 1pm?"
Start-Sleep -Milliseconds 800

# Test 2: Smishing Phishing
Write-Host ">>> [TEST 2] High-Risk Banking Smishing..." -ForegroundColor Yellow
& $adb shell am broadcast -a com.scamguard.app.TEST_SMS -n com.scamguard.app/.SmsReceiver --es sender "CHASE-ALERT" --es text "URGENT: Chase Bank alert! Unusual login from Russia. Account locked. Verify at https://chase-security-verify.xyz immediately."
Start-Sleep -Milliseconds 800

# Test 3: Truncated Payload
Write-Host ">>> [TEST 3] Truncated URL Smishing..." -ForegroundColor Yellow
& $adb shell am broadcast -a com.scamguard.app.TEST_SMS -n com.scamguard.app/.SmsReceiver --es sender "USPS-UPDATE" --es text "Your parcel is held at depot. Reschedule http://usps-re"
Start-Sleep -Milliseconds 800

# Test 4: Suspicious URL
Write-Host ">>> [TEST 4] Financial Impersonation..." -ForegroundColor Yellow
& $adb shell am broadcast -a com.scamguard.app.TEST_SMS -n com.scamguard.app/.SmsReceiver --es sender "PAYPAL-SEC" --es text "Security notice: Unauthorized transaction of $849.99 approved. Cancel here: https://paypal-dispute-resolve.com"
Start-Sleep -Seconds 1

Write-Host "================ Logcat Verification Capture ================" -ForegroundColor Cyan
& $adb logcat -d -s ScamGuard:I
Write-Host "=============================================================" -ForegroundColor Cyan

if ($UninstallOnFinish) {
    Write-Host "[CLEANUP] Uninstalling com.scamguard.app..." -ForegroundColor Yellow
    & $adb uninstall com.scamguard.app
    Write-Host "[OK] Cleaned up." -ForegroundColor Green
} else {
    Write-Host "[COMPLETED] App is live and running on your OPPO device." -ForegroundColor Green
}
