from setuptools import setup, find_packages


def read_requirements(filename):
    with open(filename) as f:
        reqs = f.readlines()
    return [r.strip() for r in reqs
            if r[0] != '#' and r[:4] != 'git+' and r[:2] != '-r']


def read_dependency_links(filename):
    with open(filename) as f:
        reqs = f.readlines()
    return [r.strip() for r in reqs
            if r[0] != '#' and r[:4] == 'git+' and r[:3] != '-r']


install_reqs = read_requirements('./requirements.txt')
dependency_links = read_dependency_links('./requirements.txt')


setup(
    name='crypto',
    version='1.0',
    author='Oriol Alfonso',
    author_email='oriolalfonso91@gmail.com',
    package_dir={'': './'},
    packages=find_packages(where='./'),
    include_package_data=True,
    install_requires=install_reqs,
    dependency_links=dependency_links,
    python_requires='>=3.7',
)
