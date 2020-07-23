# This is the build script. Build by running:
# >python build.py
# This will create a .exe in ./dist and move the necessary resources there

import PyInstaller.__main__
import shutil

PyInstaller.__main__.run([
    '--name=TSReporter',
    '--onefile',
    '--version=0.2.0',
    '--icon=resources/icon.ico',
    "main.py",
])

shutil.copyfile('chromedriver.exe', 'dist/chromedriver.exe')
shutil.copyfile('geckodriver.exe', 'dist/geckodriver.exe')
shutil.copyfile('README.md', 'dist/README.md')
