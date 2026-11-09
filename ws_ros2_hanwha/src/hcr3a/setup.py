from setuptools import setup
from glob import glob
import os

package_name = 'hcr3a'

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join(path, filename))
    return paths

worlds_files = []
for file_path in package_files('worlds'):
    # Obliczamy ścieżkę instalacji (np. share/pakiet/worlds/assets/full)
    install_dir = os.path.join('share', package_name, os.path.dirname(file_path))
    worlds_files.append((install_dir, [file_path]))

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, glob('launch/*.py')),
        ('share/' + package_name+'/config', glob('config/*')),
  	('share/' + package_name+'/urdf', glob('urdf/*')),
  	('share/' + package_name+'/rviz', glob('rviz/*')),
  	('share/' + package_name+'/meshes/collision', glob('meshes/collision/*')),
  	('share/' + package_name+'/meshes/visual', glob('meshes/visual/*')),
    ] + worlds_files,
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Michał Mazur',
    maintainer_email='micmazur@pg.edu.pl',
    description='HCR3a robot description and simulation package',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
        ],
    },
)
