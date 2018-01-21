#!/usr/bin/env python
from distutils.core import setup
setup(name='SonyPhotobooth',
      version='1.0',
      py_modules=['SonyPhotobooth'],
      description='Photobooth for Sony Cameras',
      author='Marius Hofmann',
      author_email='programmiermarius@yahoo.de',
      url='https://github.com/GithubMarius/SonyPhotobooth',
      modules=['SonyPhotobooth','SonyPhotobooth.CamCon','SonyPhotobooth.ImageProcessing','SonyPhotobooth.Input','SonyPhotobooth.PostProcessing','SonyPhotobooth.Serial','SonyPhotobooth.Disp']
      )