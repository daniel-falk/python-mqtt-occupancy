from distutils.core import setup

setup(
        name = 'occupancy-mqtt',
        version = 0.1,
        description = 'Accumulates people counter data to occupancy data',
        author = 'Daniel Falk',
        author_email = 'daniel@da-robotteknik.se',
        url = '***********',
        license = 'MIT',
        install_requires = [
            'mysqlclient',
            'sqlalchemy',
            'paho-mqtt',
            'requests'],
        package_data = {},
        zip_safe = False)
