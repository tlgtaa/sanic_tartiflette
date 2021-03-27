import setuptools


install_requires = []
with open('requirements.txt') as requirements:
    for requirement in requirements.read().splitlines():
        requirement = requirement.strip()
        if requirement.startswith('#'):
            continue

        if requirement.startswith('git'):
            dependency_name = requirement.split('egg=')[-1]
            install_requires.append('{} @ {}'.format(dependency_name, requirement))
        else:
            install_requires.append(requirement)


setuptools.setup(
    name='sanic-tartiflette',
    version='0.1',
    description='Wrapper of Sanic which includes the Tartiflette Graphql Engine',
    long_descriptioon=open('README.md').read().strip(),
    classifiers=[
        'Development Status :: 0.1 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='sanic tartiflette graphql',
    author='Talgat Abdraimov',
    author_email='fghdot25@gmail.com',
    url='https://github.com/tlgtaa/sanic_tartiflette',
    license='Other/Proprietary License',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
)
