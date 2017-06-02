import os
from distutils.core import setup
from setuptools import find_packages
import dju_common


setup(
    name='dju-common',
    version=dju_common.__version__,
    description='Django Utils: Common Library',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst')).read(),
    license='MIT',
    author='Igor Melnyk @liminspace',
    author_email='liminspace@gmail.com',
    url='https://github.com/liminspace/dju-common',
    packages=find_packages(exclude=('tests', 'tests.*')),
    include_package_data=True,
    zip_safe=False,  # because include static
    install_requires=[
        'django>=1.8,<1.12',
        'simplejson',
    ],
)
