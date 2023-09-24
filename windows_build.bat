echo "Start Windows build"
pyinstaller --onefile --noconsole --collect-data sv_ttk space_dbg_start.py
pyinstaller --onefile --noconsole --collect-data sv_ttk space_dbg.py
copy space_debugger_run_windows.bat dist
xcopy /s /i locales dist\locales
xcopy /s /i resources dist\resources
