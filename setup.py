from setuptools import setup

setup(
    name='Configri',
    version='0.2',
    packages=['configri', 'configri.main', 'configri.test', 'configri.utils', 'configri.backends', 'configri.backends.ini', 'configri.backends.base',
              'configri.backends.json', 'configri.backends.toml'],
    url='https://github.com/inimitable/configri',
    license='GNU AFFERO GENERAL PUBLIC LICENSE V3',
    author='Rob Ewing',
    author_email='inimitable@users.noreply.github.com',
    description='A simple, extensible, cross-platform config manager framework.'
    )
