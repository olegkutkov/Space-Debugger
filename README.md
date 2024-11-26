# Space Debugger
### Visualize and  analyze Starlink debug data JSON
----
![](https://raw.githubusercontent.com/olegkutkov/Space-Debugger/main/doc/space-debugger-on-linux.png)

### Requirements
Python >= 3.6
Pillow
sv-ttk
pyperclip

## Run Space Debugger
#### Install required packages
>pip3 install -r requirements.txt

#### Run source selector
>python3 space_dbg_start.py

![](https://raw.githubusercontent.com/olegkutkov/Space-Debugger/main/doc/space-debugger-start-window.png)

Select JSON file or paste copied JSON text to the window

![](https://github.com/olegkutkov/Space-Debugger/blob/main/doc/space-debugger-json-paste-window.png?raw=true)

Or run space debugger directly:
>python3 space_dbg.py -f debug_data.json

### Run on MacOS
Update or install Xcode cmd tools:
>sudo rm -rf /Library/Developer/CommandLineTools
>sudo xcode-select --install

Install python-tk with brew:
>brew install python-tk

Install pyperclip:
>curl https://files.pythonhosted.org/packages/a7/2c/4c64579f847bd5d539803c8b909e54ba087a79d01bb3aba433a95879a6c5/pyperclip-1.8.2.tar.gz > pyperclip.tar.gz
>tar -xzvf pyperclip.tar.gz
>cd pyperclip-1.8.2/
>python3 setup.py install

Run Space debugger:
> python3 space_dbg_start.py

![](https://raw.githubusercontent.com/olegkutkov/Space-Debugger/main/doc/space-debugger-on-mac.png)

### Precompiled binaries for Windows
Windows users can use precompiled exe files from the latest release v0.7 [archive](https://github.com/olegkutkov/Space-Debugger/releases/download/v0.7/space_dbg_windows_bundle-07.zip)

Just extract the archive and run `space_dbg_start.exe`

![](https://raw.githubusercontent.com/olegkutkov/Space-Debugger/main/doc/space-debugger-on-windows.png)

## Localization
Space Debugger uses gettext to support different languages. Currently supported languages: English, Ukrainian and French.

## Debug data
Space Debugger show various information about your Dishy, router and local device (used to get the data).
All data values are clickable and automatically copied to the clipboard.

![](https://raw.githubusercontent.com/olegkutkov/Space-Debugger/main/doc/space-debugger-copy-to-clipboard.png)

All images are clickable and open full size in your system's default image viewer.

### Obstructions data
![](https://raw.githubusercontent.com/olegkutkov/Space-Debugger/main/doc/space-debugger-obstructions-view.png)
Average obstructions data are plotted on a circle diagram and split into 30-degree sectors.
The Top is North, the right is East, the bottom is South, and the left is West. More red lines in the given sector mean more obstructions in this direction. 
It's just a 'weight' and doesn't represent actual surroundings.
