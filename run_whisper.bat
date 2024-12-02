@echo off
echo 'Witaj w whisper!!!'

:: Wybierz sciezke do modelu
set model_path="D:\Ai\Audio-Classifier\whisper\Whisper-1.12.0\models\large_v3.bin"

:: Wybierz sciezke do whispera
set whisper_folder="D:\Ai\Audio-Classifier\whisper\Whisper-1.12.0\x64\Release\main.exe"

:: Iterate through each line in lista.txt and call whisper for each file
for /f "delims=" %%a in (lista.txt) do (
    echo Przetwarzanie %%a
    %whisper_folder% -tr -l pl -m %model_path% -f "%%a" -osrt
)

exit
