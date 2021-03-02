import setuptools

setuptools.setup(name='xchanger',
    entry_points={
        'console_scripts': [
            'xchanger = xchanger:main',
        ],
    })