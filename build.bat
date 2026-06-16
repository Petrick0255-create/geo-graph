@echo off

echo =====================
echo 기존 빌드 삭제
echo =====================

rmdir /s /q build
rmdir /s /q dist

del /q *.spec

echo =====================
echo EXE 생성 시작
echo =====================

pyinstaller ^
--noconfirm ^
--clean ^
--windowed ^
--onefile ^
--name "판경계그래프" ^
app.py

echo.
echo =====================
echo 완료!
echo dist\판경계그래프.exe
echo =====================

pause