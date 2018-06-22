from setuptools import setup, find_packages

requirements = [
    'future',
    'numpy',
    'pandas',
    'scipy',
]

setup(
    name='eaarl',
    version='1.1.0',
    description='EAARL processing library',
    packages=find_packages(include=['eaarl.*']),
    package_dir={'eaarl': 'eaarl'},
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)
