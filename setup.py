from cx_Freeze import Executable, setup
build_exe_options = {
      "packages": ['requests', 'selenium', 'tkinter'],
      "include_files": [
            'config.py', 'information_compile.py', 'reporter.py', 'sector_seek.py',
            'utils.py', 'versions.py', 'chromedriver.exe', 'README.md', 'assets.py', 'batch.py', 'bugs.py', 'build.py',
            'geckodriver.exe', 'chromedrivers.py', 'main.py', 'gui_bughandler.py', 'password.py', 'upload.py'
      ]
}
setup(
      name='TSReporter',
      description='A handy reporting tool for testers',
      version='0.1.0',
      options={"build_exe": build_exe_options},
      executables=[
            Executable('gui.py', targetName="TSReporter.exe", icon='resources/icon.ico')
      ]
)
