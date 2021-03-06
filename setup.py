#
from setuptools import setup


requires = (
    'addict==0.4.0',
    'arrow==0.8.0',
    'bumpversion==0.5.3',
    'jinja2==2.8',
    'loadconfig==0.1.1',
    'sortedcontainers==1.5.3',
    'requests==2.10.0',
    'pytest==3.0.6',
    'pyyaml==3.11',
    'requests==2.10.0',
)

from echo import \
    __author__, \
    __version__

setup(name="echo",
      version="0.1.0",
      url="https://github.com/nabeelio/echo",
      author="Nabeel Shahzad",
      author_email="hi@nabs.io",
      install_requires=requires,
      test_suite='test',
      entry_points={
        'console_scripts': [
            'echo = echo.app:main',
        ]
      }
)
