from cx_Freeze import Executable, setup

build_exe_options = {
      "packages": ['requests', 'selenium', 'tkinter'],
      "include_files": [
            'config.py', 'information_compile.py', 'reporter.py', 'sector_seek.py',
            'utils.py', 'versions.py', 'chromedriver.exe', 'README.md'
      ]
}

setup(
      name='TSReporter',
      description='A handy reporting tool for testers',
      version='0.1.0',
      options={"build_exe": build_exe_options},
      executables=[
            Executable('main.py', targetName="TSReporter.exe", icon='resources/icon.ico')
      ]
)
