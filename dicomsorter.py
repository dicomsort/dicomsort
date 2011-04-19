import os
import dicom
import re
import shutil
import itertools
from threading import *

def grouper(iterable,n):
	return map(None, *[iter(iterable),] * n)

def clean_path(path):
	badchars = '[\\\:\*\?\"\<\>\| ]+'
	return re.sub(badchars,'_',path)

def isdicom(filename):
	try:
		return dicom.read_file(filename) 
	except dicom.filereader.InvalidDicomError:
		return False

class Dicom():
	def __init__(self,filename,dcm=None):
		"""
		Takes a dicom filename in and returns instance that can be used to sort
		"""
		# Be sure to do encoding because Windows sucks
		self.filename = filename.encode("UTF-8")

		# Load the DICOM object
		if dcm:
			self.dicom = dcm
		else:
			self.dicom = dicom.ReadFile(self.filename)

		# Specify which field-types to override
		self.default_overrides = {'ImageType':self._get_image_type,
						  'SeriesDescription':self._get_series_description}

		# Combine with anons - Empty but provides the option to have defaults
		anondict = dict()
		self.overrides = dict(self.default_overrides, **anondict);

	def __getitem__(self,attr):
		"""
		Points the reference to the property unless an override is specified
		"""
		try:
			item = self.overrides[attr]
			if not isinstance(item,str):
				return item()
			return item
		except KeyError:
			return getattr(self.dicom,attr)

	def _get_series_description(self):
		if not hasattr(self.dicom,'SeriesDescription'):
			return 'Series%(n)04d' % {'n':self.dicom.SeriesNumber}
		else:
			d = {'d':self.dicom.SeriesDescription,'n':self.dicom.SeriesNumber}
			return '%(d)s_Series%(n)04d' % d

	def _get_image_type(self):
		"""
		Determines the human-readable type of the image
		"""
		phaseSet = set(['P',]);
		magSet	 = set(['FFE','M'])

		imType = set(self.dicom.ImageType)

		if len(phaseSet.intersection(imType)):
			return 'Phase'
		elif len(magSet.intersection(imType)):
			return 'Mag'
		else:
			return 'Image'

	def get_destination(self,root,dirFormat,fileFormat):
		directory = os.path.join(root,*dirFormat)
		return os.path.join(directory,fileFormat) % self

	def SetAnonRules(self,anondict):
		# Appends the rules to the overrides so that we can alter them
		if isinstance(anondict,dict):
			self.anondict = anondict
		else:
			raise Exception('Anon rules must be a dictionary')

		# Update the override dictionary
		self.overrides = dict(self.default_overrides,**anondict)

	def is_anonymous(self):
		return self.default_overrides != self.overrides

	def check_dir(self,dest):
		dest = os.path.dirname(dest)
		if not os.path.exists(dest):
			os.makedirs(dest)

	def sort(self,root,dirFields,fnameString):
		destination = self.get_destination(root,dirFields,fnameString)

		self.check_dir(destination)

		if self.is_anonymous():
			self.dicom.SaveAs(destination)
		else:
			shutil.copy(self.filename,destination)

class Sorter(Thread):
	def __init__(self,files,outDir,dirFormat,fileFormat,anon=dict(),keep_filename=False):
		self.dirFormat = dirFormat
		self.fileFormat = fileFormat
		self.fileList = files
		self.anondict  = anon
		self.keep_filename = keep_filename
		self.outDir = outDir

		Thread.__init__(self)
		self.start()

	def run(self):

		files = self.fileList

		root = os.path.dirname(files[0])

		for file in files:
			if file == None:
				continue

			dcm = isdicom(file)
			if dcm:
				dcm = Dicom(file,dcm)
				dcm.SetAnonRules(self.anondict)
				if self.keep_filename:
					dcm.sort(self.outDir,self.dirFormat,file)
				else:
					dcm.sort(self.outDir,self.dirFormat,self.fileFormat)

class DicomSorter():
	def __init__(self,pathname=None):
		# Use current directory by default
		if not pathname:
			pathname = os.getcwd()

		self.pathname = pathname

		self.folders	= []
		self.filename	= '%(ImageType)s (%(InstanceNumber)04d)' 

		# Include the series subdirectory by default
		self.includeSeries = True
		self.seriesDefault = '%(SeriesDescription)s'

		# Don't anonymize by default
		self.anondict = dict()

		self.keep_filename = False

	def SetAnonRules(self,anondict):
		# Appends the rules to the overrides so that we can alter them
		if isinstance(anondict,dict):
			self.anondict = anondict
		else:
			raise Exception('Anon rules must be a dictionary')

	def GetFolderFormat(self):
		# Make a local copy
		folderList = self.folders[:]

		if self.includeSeries:
			folderList.append(self.seriesDefault)

		return folderList			

	def Sort(self,outputDir):
		# This should be moved to a worker thread

		dirFormat = self.GetFolderFormat()

		fileList = list()

		for root,dir,files in os.walk(self.pathname):
			for file in files[2:]:
				fileList.append(os.path.join(root,file))

		numberOfThreads = 2
		numberOfFiles = len(fileList)

		numberPerThread = int(round(float(numberOfFiles)/float(numberOfThreads)))

		fileGroups = grouper(fileList,numberPerThread)

		dirFormat = self.GetFolderFormat()

		s = list()

		for group in fileGroups:
			s = Sorter(group,outputDir,dirFormat,self.filename,self.anondict,self.keep_filename)
			# We want to wait until we are completely done
			s.join()

	def SetIncludeSeriesAuto(self,val):
		self.includeSeries = val

	def GetAvailableFields(self):
		for root,dirs,files in os.walk(self.pathname):
			for file in files[2:]:
				filename = os.path.join(root,file)
				dcm = isdicom(filename)
				if dcm:
					return dcm.dir('') 

		raise DicomFolderError(''.join(pathname,' contains no DICOMs'))

class DicomFolderError(Exception):
	def __init__(self,value):
		self.value = value
	
	def __str__(self):
		return repr(self.value)


