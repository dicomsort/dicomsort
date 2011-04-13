import os
import re

class PathGen:
	"""
	Generates the paths for each dicom
	"""
	def __init__(self):
		# Description_of_series_Series0001
		self.dFormat = ['%(SeriesDescription)s_Series%(SeriesNumber)04d',]
		# Image (0001)
		self.fFormat = '%(CustomImageType)s (%(InstanceNumber)04d)'

		self.defaultDict = {'CustomImageType':'Image'};

	def ConstructDict(self,dcm,fstring):
		fields = re.findall('(?<=%\().*?(?=\))',fstring)

		res = self.defaultDict;

		for field in fields:
			if hasattr(dcm,field):
				res[field] = getattr(dcm,field)

		return res

	def GetFullPath(self,dcm,root=None):
		path = os.path.join(self.GetFolderName(dcm),self.GetFileName(dcm))

		if root:
			path = os.path.join(root,path)

		return path

	def GetFileName(self,dcm):
		return self.fFormat % self.ConstructDict(dcm,self.fFormat)

	def GetFolderName(self,dcm):

		folderList = []

		for item in self.dFormat:
			folderList.append(item % self.ConstructDict(dcm,item))

		# Form this into a valid filepath
		path = os.path.join(*folderList)
		# Remove spaces because they are a nuissance
		return path.replace(' ','_')

import dicom

dcm = dicom.ReadFile('dicoms/Image (0001)')

pg = PathGen()

print pg.GetFullPath(dcm,'/usr/local/bin')
"""

class Sorter:

	def __init__(self):
		# Set default tokens to use if non provided by the user
		self.directoryTokens = ['%SeriesDescription%_Series%04SeriesNumber%',]
		self.filenameTokens  = '%ImageType% (%04InstanceNumber%)'
		self.formatString    = '%(SeriesDescription)s_Series%(SeriesNumber)04d'

	def getTargetPath(self,dicomObject):
		folderName = ''

		for token in self.directoryTokens:
			try:
				value = getattr(dicomObject,token)
			except AttributeError:
				return None

			folderName = os.path.join(folderName,str(value))
		return folderName

	def deTokenize(self,tokenString,dicomObj):
		tokens = re.findall('%.*?%',tokenString)

		for token in tokens:
			# Look at what is between the %'s
			actual = token[1:-1]

			# Determine if formating info is there
			num = re.findall('[0-9]+',actual)

			if num:
				padVal	= num[0][0]
				padSize = num[0][1:]

			actual.replace(

			# Determine if this is a valid attribute of dicomObj
			#try:
			#	value = getattr(dicomObj,actual)
			#except AttributeError:
			#	value = None

			# Basically determine if we need formatting
			nums = re.findall('[0-9]+',actual)
			"""
