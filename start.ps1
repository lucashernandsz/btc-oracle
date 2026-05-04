$root = "C:\Users\lucas\Desktop\Projetos\btc-oracle"

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\backend\api'; & '$root\.venv\Scripts\Activate.ps1'; uvicorn main:app --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm start"
