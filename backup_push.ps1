Write-Host "====================================="
Write-Host " TRISHULA CAPITAL BACKUP + GITHUB "
Write-Host "====================================="


# GITIGNORE
@"
.venv/
__pycache__/
*.pyc

node_modules/
.next/

.env
.env.local

.cache/

*.log
"@ | Out-File ".gitignore" -Encoding utf8


Write-Host "Gitignore updated"


# DATABASE BACKUP

$DATE = Get-Date -Format "yyyy-MM-dd_HH-mm"

$BACKUP = "trishula_database_$DATE.sql"


Write-Host "Backing up database..."

& "C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" `
-U postgres `
-d trishula `
-f $BACKUP


if(Test-Path $BACKUP){

    Write-Host "Database backup created"
    Write-Host $BACKUP

}
else{

    Write-Host "Database backup failed"

}


# GITHUB PUSH

Write-Host "Uploading to Github..."


git add .


git commit -m "Trishula backup $DATE"


git push origin main


Write-Host "DONE"