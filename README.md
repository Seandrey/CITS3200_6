# CITS3200_6

## How to install
First, clone the repository into your folder of choice.

### Windows
1. Ensure you have Python installed.
2. Run `setup.bat`.

### Unix-based systems (Linux, Mac, Cygwin, etc.)
1. Ensure you have Python 3 installed (such as from your OS' package manager).
2. Run `setup.sh`.

## How to launch

### From command line

1. Ensure you are in the .venv virtual environment. If not, re-enter by running the `setup` script again.
2. Run `flask run`.
3. Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser of choice.

### From VSCode

1. Install the [VSCode Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) if you haven't already.
2. Go to the `Run and Debug` pane (Ctrl+Shift+D).
3. Click `Add Configuration`.
4. Select `Python` as the category.
5. Select `Flask` as the debug category.
6. Now either click the `Python: Flask` button or press `F5` on your keyboard.
7. Open [http://127.0.0.1:5000/](http://127.0.0.1:5000/) in your browser of choice.
