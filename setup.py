import setuptools

setuptools.setup(
	name='styx',
	version='0.0.1',
    author='Dataptive',
    author_email='hello@dataptive.io',
    description='Dataptive Styx Python client library',
	packages=setuptools.find_packages(),
	python_requires='>=3.6',
    install_requires=[
        'aiohttp',
        'websockets'
    ]
)
