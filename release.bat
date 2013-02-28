del inx2csv.zip
rmdir /s /q dist
rmdir /s /q inx2csv
python setup.py py2exe
ping localhost -n 5 > nul
rename dist inx2csv
"C:\Program Files\7-Zip\7z.exe" a inx2csv.zip inx2csv