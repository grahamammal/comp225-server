from setuptools import find_packages, setup
# makes the app installalbe
setup(
    name='assassin_server',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'assassin_server',
    ],
)
