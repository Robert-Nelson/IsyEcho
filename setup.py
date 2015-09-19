from distutils.core import setup

setup(
    name='pyISYEcho',
    version='0.9.1',
    packages=['pyISYEcho', 'ISY'],
    package_dir={'ISY': 'ISYlib-python/ISY', 'pyISYEcho': 'pyISYEcho'},
    include_package_data=True,
    package_data={
        'pyISYEcho': [
            'static/*.css',
            'static/*.gif',
            'static/*.js',
            'static/*.png',
            'templates/*.html'
        ]
    },
    data_files=[
        ('var/pyHueISY-instance', ['instance/Readme'])
    ],
    scripts=[
        'pyHueISYServer.py'
    ],
    url='http://github.com/open-sw/pyISYEcho',
    license='',
    author='robert',
    author_email='robertn@the-nelsons.org',
    description='Controlling Software for Universal Device\'s ISY 994i and Amazon Echo',
    install_requires=['flask']
)
