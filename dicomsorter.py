import os
import dicom
import re
import shutil

def clean_path(path):
	badchars = '[\\\:\*\?\"\<\>\| ]+'
	return re.sub(badchars,'_',path)

def isdicom(filename):
	try:
		return dicom.read_file(filename) 
	except dicom.filereader.InvalidDicomError:
		return False

class Dicom():
	def __init__(self,filename):
		"""
		Takes a dicom filename in and returns instance that can be used to sort
		"""
		# Be sure to do encoding because Windows sucks
		self.filename = os.path.abspath(filename.encode("UTF-8"))

		# Load the DICOM object
		self.dicom = dicom.ReadFile(self.filename)

		# Specify which field-types to override
		self.overrides = {'ImageType':self._get_image_type,
						  'SeriesDescription':self._get_series_description}

		# Don't anonymize initially unless specified
		self.anonymized = False

	def __getitem__(self,attr):
		"""
		Points the reference to the property unless an override is specified
		"""
		try:
			return self.overrides[attr]()
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

	def get_destination(self,root,dFormat=['%(SeriesDescription)s',],
						fFormat='%(ImageType)s (%(InstanceNumber)04d)'):
		directory = os.path.join(root,*dFormat)
		return os.path.join(directory,fFormat) % self

	def sort(self,root,dirFields,fnameString):
		destination = self.get_destination(root,dirFields,fnameString)

		if self.anonymized:
			self.dicom.SaveAs(destination)
		else:
			shutil.copyfile(self.filename,destination)

	def anonymize(self,anondict=None):
		if not anondict:
			anondict = {'PatientsName':'ANONYMOUS',
						'PatientID':'id',
						'PatientsBirthDate':''}

		self.anonymized = True 

		for field in fields.keys():
			setattr(self.dicom,field,fields[field])

class DicomSorter():
	def __init__(self,pathname=None):
		# Use current directory by default
		if not pathname:
			pathname = os.getcwd()

		self.pathname = pathname

		self.folders	= []
		self.filename	=  

		# Include the series subdirectory by default
		self.includeSeries = True
		self.seriesDefault = '%(SeriesDescription)s'

	def sort(self,outputDir):
		
	

	def set_include_series_auto(self,val):
		if val not True and val not False:
			raise Exception('Valid values include True or False')

		self.includeSeries = val

	def get_available_fields(self):
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


