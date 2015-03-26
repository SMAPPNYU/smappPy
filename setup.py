from setuptools import setup

setup(name='smappPy',
      version='0.1.13',
      description='NYU SMaPP lab utility library',
      author='NYU SMaPP',
      license='GPLv2',
      author_email='smapp_programmer-group@nyu.edu',
      url='http://smapp.nyu.edu',
      packages=['smappPy'],
      requires=[
          'tweepy',
          'bson',
          'urllib',
          'simplejson',
          'matplotlib',
      ],
     )
