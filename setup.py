#!/usr/bin/env python

 # 
 # Copyright 2009 
 #
 # Licensed under the Apache License, Version 2.0 (the "License");
 # you may not use this file except in compliance with the License.
 # You may obtain a copy of the License at
 #
 #      http://www.apache.org/licenses/LICENSE-2.0
 #
 # Unless required by applicable law or agreed to in writing, software
 # distributed under the License is distributed on an "AS IS" BASIS,
 # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 # See the License for the specific language governing permissions and
 # limitations under the License.

from setuptools import setup
import os

#install_requires = [
#]

version = '0.0.0'

basedir = os.path.dirname(__file__)
README = os.path.join(basedir, 'README')
long_description = open(README).read() + 'nn'

#scriptdir = os.path.join(basedir, 'bin')
#exes = os.listdir(scriptdir)
#scripts = filter(os.path.isfile,[os.path.join(scriptdir, x) for x in exes])

setup(
	name="Py2JSON",
	description="Python to JSON translator",
	url='http://www.igorgue.info/',
	author="Igor Guerrero",
	license='ASLv2',
	version=version,
	packages=['py2json'],
	#install_requires=install_requires,
	#test_suite='py2json.test',
	long_description=long_description,
	#scripts=scripts,
	)
