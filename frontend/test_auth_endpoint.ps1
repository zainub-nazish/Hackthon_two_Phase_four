Start-Process -NoNewWindow npm -ArgumentList "run", "dev"
Start-Sleep -Seconds 10
Invoke-WebRequest -Uri http://localhost:3000/api/auth/sign-in/email -Method POST