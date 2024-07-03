
    echo 'Witaj w whisper!!!'

    :: Wybierz sciezke do modelu
    set model_path="C:\SEdit\Whisper\Models\large.bin"
    ::Wybierz sciezke do whispera
	
	set whisper_folder="whisper\Whisper-1.11.0\x64\Debug\main.exe"

    ::usuwa wszytskie CRLF z lista.txt i tworzy jeden string zawierajacy sciezki plikow oddzielone spacj¹
    setlocal enabledelayedexpansion
    set "line="
    for /f "delims=" %%a in (lista.txt) do set "line=!line!%%a "

    :: odpala whispera z atrybutami (-translate -langue  -model -file -save as srt)
    %whisper_folder% -tr -l pl -m %model_path% -f %line% -osrt 

    exit
    