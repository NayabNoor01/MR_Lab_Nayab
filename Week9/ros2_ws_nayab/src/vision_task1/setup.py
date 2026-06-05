from setuptools import find_packages, setup

package_name = 'vision_task1'

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
        'task_1 = vision_task1.task_1:main',
        'task_2 = vision_task1.task_2:main',
        'task_3 = vision_task1.task_3:main',
        'task_4 = vision_task1.task_4:main',
        'task_5 = vision_task1.task_5:main',
        'excercise_4= vision_task1.excercise_4:main',
        'excercise_1= vision_task1.excercise_1:main',
        'excercise_2= vision_task1.excercise_2:main',
        'excercise_3= vision_task1.excercise_3:main',
        ],
    },
)
