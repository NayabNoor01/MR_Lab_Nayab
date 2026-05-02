from setuptools import find_packages, setup

package_name = 'my_turtle_package'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='nayab',
    maintainer_email='noorelahi1948@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'my_node = my_turtle_package.move_turtle:main',
            'task_1 = my_turtle_package.task_1:main',
            'task_2 = my_turtle_package.task_2:main',
            'task_3 = my_turtle_package.task_3:main',
        ],
    },
)
