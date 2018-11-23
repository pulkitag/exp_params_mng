import setuptools
from setuptools.command.install import install
from os import path as osp
import os
import yaml

class CustomInstall(install):
  """Make the config file before running the installation."""
  def run(self):
    dirName = osp.join(os.getenv('HOME'), '.exp_params_mng')
    configFile = osp.join(dirName, 'config.yml')
    if not osp.exists(dirName):
      os.makedirs(dirName)
    dat = {}
    dat['host'] = 'localhost'
    dat['port'] = 27900
    dat['database'] = 'dev'
    dat['user'] = 'default_user'
    dat['password'] = 'password'
    yaml.dump(dat, open(configFile, 'wb'), default_flow_style=False)
    install.run(self)

setuptools.setup (
  name="exp_params_mng",
  version="1.0",
  author="Pulkit Agrawal",
  author_email="pulkitag@berkeley.edu",
  description="Database utilities for managing experiments",
  dependency_links=[
    "git+https://github.com/pulkitag/pyhelper_fns.git",
  ],
  install_requires=[
    "numpy",
    "pymongo",
    "datetime",
    "yaml",
  ],
  packages=['exp_params_mng'],
  zip_safe=True,
  cmdclass={
        'install': CustomInstall,
    },
)
