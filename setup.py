from setuptools import setup

setup(name='smappPy',
      version='0.1.32',
      description='NYU SMaPP lab utility library',
      author='NYU SMaPP',
      license='GPLv2',
      author_email='smapp_programmer-group@nyu.edu',
      url='http://smapp.nyu.edu',
      packages=['smappPy', 'smappPy.facebook', 'smappPy.networks', 'smappPy.tools',
                'smappPy.topics', 'smappPy.user_collection'],
      requires=[
          'tweepy',
          'bson',
          'urllib',
          'simplejson',
          'matplotlib',
      ],
     )
