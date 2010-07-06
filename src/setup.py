from distutils.core import setup
import py2exe
import os

py2exe_options = dict(
                       ascii=True,  # Exclude encodings
                       excludes=['_ssl',  # Exclude _ssl
                                 'pyreadline', 'difflib', 'doctest', 'locale',
                                 'optparse', 'pickle', 'calendar', 'pbd', 'unittest', 'inspect'],  # Exclude standard library
                       dll_excludes=['msvcr71.dll', 'w9xpopen.exe'],  # Exclude msvcr71
                       compressed=True,  # Compress library.zip
                       bundle_files = 2,
                       )
map_files = ['maps/'+name for name in os.listdir('maps/') if name.endswith('.jpg')]

setup(name='',
      version='5.0.0.0',
      description='',
      author='Sph4ck',
      console=['launcher.py'],
      #console = [{ 'script': "launcher.py", 'uac_info': "requireAdministrator", },],
      options={'py2exe': py2exe_options},
      data_files = [('', ['config', 'README.txt']),
                    ('maps', map_files)],
      #zipfile = None,
      )