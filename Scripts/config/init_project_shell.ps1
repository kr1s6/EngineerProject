function OperationFailed {
    param ([string]$message)
    Write-Host $message -ForegroundColor Red
    exit 1
}

# Funkcja do porównania wersji
function Compare-Version {
    param (
        [string]$Version1,
        [string]$Version2
    )
    $v1 = $Version1.Split(".") | ForEach-Object { [int]$_ }
    $v2 = $Version2.Split(".") | ForEach-Object { [int]$_ }

    for ($i = 0; $i -lt [Math]::Max($v1.Count, $v2.Count); $i++) {
        $part1 = $v1[$i]  # Część wersji 1
        $part2 = $v2[$i]  # Część wersji 2

        # Jeśli którejś części brakuje, ustaw 0
        if ($null -eq $part1) { $part1 = 0 }
        if ($null -eq $part2) { $part2 = 0 }

        # Porównanie wersji
        if ($part1 -lt $part2) { return -1 }
        if ($part1 -gt $part2) { return 1 }
    }
    return 0
}

Write-Host "----Start Django project initialization----" -ForegroundColor Cyan
$MIN_ALLOWABLE_PYTHON_VERSION = "3.9.1"

# Aktywacja środowiska wirtualnego
Write-Host "Activating Python environment" -ForegroundColor Cyan
if (Test-Path "./env/") {
    . ./env/Scripts/Activate.ps1
    Write-Host "Env activated" -ForegroundColor Green
} else {
    Write-Host "Environment not created already" -ForegroundColor Yellow
    $current_python_version = (python --version 2>&1).Split()[1]
    Write-Host "Current Python version: $current_python_version" -ForegroundColor Cyan
    if ((Compare-Version $current_python_version $MIN_ALLOWABLE_PYTHON_VERSION) -ge 0) {
        Write-Host "Python version is equal or greater. That's good :)" -ForegroundColor Green
        python -m venv env
        Write-Host "Environment created. Let's activate it" -ForegroundColor Green
        . ./env/Scripts/Activate.ps1
    } else {
        OperationFailed "Python version $current_python_version is too low. Update it or download it at: https://www.python.org/downloads/"
    }
}

# Sprawdzenie, czy środowisko jest aktywne
Write-Host "----Checking whether env is activated----" -ForegroundColor Cyan
. ./env/Scripts/Activate.ps1

$current_python = (Get-Command python).Source
Write-Host "Python executable path: $current_python" -ForegroundColor Yellow

# Sprawdzanie aktywacji środowiska
if ($current_python -match "\\env\\Scripts\\python.exe$") {
    Write-Host "Env is activated: $current_python. Downloading dependencies" -ForegroundColor Green
    pip install -r Docs/requirements.txt
    pip list
} else {
    OperationFailed "Env is not activated. Something went wrong"
}

# Sprawdzenie folderu migracji
Write-Host "----Checking whether migrations folder exists----" -ForegroundColor Cyan
$migrations_dir = "./webStore/migrations"
if (!(Test-Path $migrations_dir)) {
    Write-Host "Migrations folder does not exist. Creating one..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $migrations_dir | Out-Null
    New-Item -ItemType File -Path "$migrations_dir/__init__.py" | Out-Null
} else {
    Write-Host "Migrations folder exists. Cleaning if necessary" -ForegroundColor Green
    Get-ChildItem $migrations_dir -File | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
}

# Tworzenie migracji
Write-Host "----Creating migrations----" -ForegroundColor Cyan
python manage.py makemigrations

# Tworzenie bazy danych
Write-Host "----Creating Database if migrations succeeded----" -ForegroundColor Cyan
$extra_files = Get-ChildItem $migrations_dir -File | Where-Object { $_.Name -ne "__init__.py" }
if ($extra_files) {
    Write-Host "Found additional migration files. Creating sqlite3 database..." -ForegroundColor Green
    python manage.py migrate
    if (Test-Path "./db.sqlite3") {
        Write-Host "Migration has been successful. Creating superuser" -ForegroundColor Green
        python Scripts/create_superuser.py
    } else {
        OperationFailed "Migrations failed"
    }
} else {
    Write-Host "No additional migration files found." -ForegroundColor Yellow
}

# Uruchomienie serwera
Write-Host "----Running server----" -ForegroundColor Cyan
python manage.py runserver
