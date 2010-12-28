from distutils.core import setup
import py2exe #@UnusedImport
import os

py2exe_options = dict(
                       ascii=True,  # Exclude encodings
                       excludes=['_ssl',  # Exclude _ssl
                                 'pyreadline', 'difflib', 'doctest', 'locale',
                                 'optparse', 'pickle', 'calendar', 'pbd', 'unittest', 'inspect'],  # Exclude standard library
                       dll_excludes=['msvcr71.dll', 'w9xpopen.exe',
                                     'API-MS-Win-Core-LocalRegistry-L1-1-0.dll',
                                     'API-MS-Win-Core-ProcessThreads-L1-1-0.dll',
                                     'API-MS-Win-Security-Base-L1-1-0.dll',
                                     'KERNELBASE.dll',
                                     'POWRPROF.dll',
                                     ],
                       compressed=True,  # Compress library.zip
                       bundle_files = 2,
                       )
map_files = ['maps/'+name for name in os.listdir('maps/') if name.endswith('.jpg')]
sprite_files = ['sprites/'+name for name in os.listdir('sprites/') if name.endswith('.jpg') or name.endswith('.png')]

setup(name='',
      version='1.5.0.0',
      description='',
      author='Sph4ck',
      console=['launcher.py'],
      options={'py2exe': py2exe_options},
      data_files = [('', ['config', 'README.txt']),
                    ('maps', map_files),
                    ('sprites', sprite_files)],
#      data_files = [('', ['README.txt', ]),
#                    ],
      #zipfile = None,
      )