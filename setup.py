from setuptools import setup

setup(name='tap-linkedin',
      version='0.0.1',
      description='Singer.io tap for scraping data from LinkedIn',
      author='Kelly Mondor',
      url='https://singer.io',
      classifiers=['Programming Language :: Python :: 3 :: Only'],
      py_modules=['tap_linkedin'],
      install_requires=[
          'backoff==1.8.0',
          'requests==2.20.1',
          'singer-python==5.12.1'
      ],
      entry_points='''
          [console_scripts]
          tap-linkedin=tap_linkedin:main
      ''',
      packages=['tap_linkedin', 'tap_linkedin.streams'],
      package_data={
          "schemas": ["tap_linkedin/schemas/*.json"]
      },
      include_package_data=True,
    )
