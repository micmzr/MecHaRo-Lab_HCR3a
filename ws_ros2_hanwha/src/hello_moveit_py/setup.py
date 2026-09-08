from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'hello_moveit_py'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*'))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Michał Mazur',
    maintainer_email='micmazur@pg.edu.pl',
    description='Simple MoveIt2 Python example for HCR3a robot',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'hello_moveit_py = hello_moveit_py.hello_moveit_py:main'
        ],
    },
)
