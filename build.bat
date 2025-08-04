rmdir /S /Q dist\my-selling

pyinstaller --noconfirm --windowed --onedir --collect-all reportlab.graphics.barcode start.pyw
mkdir dist\start\app
robocopy /MIR app dist\start\app

move dist\start\start.exe dist\start\my-selling.exe
move dist\start dist\my-selling