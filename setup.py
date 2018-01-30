from setuptools import setup, find_packages

requirements = [
    'future',
    'numpy',
    'pandas',
    'scipy',
]

test_requirements = [
    'pytest',
]

setup(
    name='eaarl',
    version='0.0.1',
    description='EAARL processing library',
    packages=find_packages('eaarl'),
    package_dir={'eaarl': 'eaarl'},
    install_requires=requirements,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Scientific/Engineering :: GIS',
    ],
    test_suite='tests',
    tests_requires=test_requirements
)
