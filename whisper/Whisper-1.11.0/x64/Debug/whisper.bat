
echo 'Witaj w whisper!!!'

:: Wybierz sciezke do modelu
set model_path="C:\SEdit\Whisper\Models\large.bin"

::usuwa wszytskie CRLF z lista.txt i tworzy jeden string zawierajacy sciezki plikow oddzielone spacją
setlocal enabledelayedexpansion
set "line="
for /f "delims=" %%a in (lista.txt) do set "line=!line!%%a "


:: odpala whispera z atrybutami (-translate -langue -diarize -model -file -save as srt)
main.exe -tr -l pl -di -m %model_path% -f %line%  -osrt

:: 3 razy pauza zeby nie zamknac omylkowo terminala missclickiem
echo 3 nacisniecia dowolnego klawisza zamkna program !!
pause
pause
pause

exit