=@echo off
chcp 65001
setlocal

:: �������⻷��
call venv\Scripts\activate.bat

:: ���� Start.py
python Start.py

:: ��ѡ��ͣ���������д��ڣ��鿴���
pause

endlocal
