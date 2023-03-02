from setuptools import setup, find_packages

setup(
    name='espnff',
    version='0.1.0',
    author='Jonathan Cheng',
    author_email='jonchengw@gmail.com',
    description='ESPN data analysis',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/jon-cheng/espnff',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=[
        'numpy',
        'pandas',
        'matplotlib',
    ]
)
