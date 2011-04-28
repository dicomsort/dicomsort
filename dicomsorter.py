import collections
import os
import dicom
import gui
import shutil
import itertools
from threading import *

def grouper(iterable,n):
    return map(None, *[iter(iterable),] * n)

def clean_path(path):
    badchars = '[\\\:\*\?\"\<\>\| ]+'
    return e.sub(badchars,'_',path)

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
            if isinstance(item,collections.Callable):
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
        magSet   = set(['FFE','M'])

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

    def sort(self,root,dirFields,fnameString,test=False):
        destination = self.get_destination(root,dirFields,fnameString)

        if test:
            print(destination)
            return

        self.check_dir(destination)

        if self.is_anonymous():
            # Actually write the anononymous data
            # write everything in anondict -> Parse it so we can have dynamic fields
            for key in self.anondict.keys():
                replacementvalue = self.anondict[key] % self
                self.dicom.data_element(key).value = replacementvalue

            self.dicom.SaveAs(destination)
        else:
            shutil.copy(self.filename,destination)

class Sorter(Thread):
    def __init__(self,files,outDir,dirFormat,fileFormat,
                    anon=dict(),keep_filename=False,iterator=None,test=False,
                    listener=None,total=None):

        self.dirFormat = dirFormat
        self.fileFormat = fileFormat
        self.fileList = files
        self.anondict  = anon
        self.keep_filename = keep_filename
        self.outDir = outDir
        self.test = test
        self.iter = iterator
        
        if total == None:
            self.total = len(self.fileList)
        else:
            self.total = total

        self.isgui = False

        if listener:
            self.listener = listener
            self.isgui = True

        Thread.__init__(self)
        self.start()

    def run(self):

        if self.isgui:
            import wx

        files = self.fileList

        for file in files:
            if file == None:
                continue

            #try:

            dcm = isdicom(file)
            if dcm:
                dcm = Dicom(file,dcm)
                dcm.SetAnonRules(self.anondict)
                if self.keep_filename:
                    origFile = os.path.basename(file)
                    dcm.sort(self.outDir,self.dirFormat,origFile,test=self.test)
                else:
                    dcm.sort(self.outDir,self.dirFormat,self.fileFormat,test=self.test)

            if self.iter:
                count = self.iter.next()
                if self.isgui:
                    event = gui.CounterEvent(Count=count,total=self.total)
                    wx.PostEvent(self.listener,event)
            #except:
            #    dlg = gui.CrashReporter(fullstack=traceback.format_exc())
            #    dlg.ShowModal()

class DicomSorter():
    def __init__(self,pathname=None):
        # Use current directory by default
        if not pathname:
            pathname = [os.getcwd(),]

        if not isinstance(pathname,list):
            pathname = [pathname,]

        self.pathname = pathname

        self.folders    = []
        self.filename   = '%(ImageType)s (%(InstanceNumber)04d)' 

        # Include the series subdirectory by default
        self.includeSeries = True
        self.seriesDefault = '%(SeriesDescription)s'

        self.sorters = list()

        # Don't anonymize by default
        self.anondict = dict()

        self.keep_filename = False

    def IsSorting(self):
        for sorter in self.sorters:
            if sorter.isAlive():
                return True

        return False

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

    def Sort(self,outputDir,test=False,listener=None):
        # This should be moved to a worker thread

        dirFormat = self.GetFolderFormat()

        fileList = list()

        for path in self.pathname:
            for root,dir,files in os.walk(path):
                for file in files[2:]:
                    fileList.append(os.path.join(root,file))

        # Make sure that we don't have duplicates
        fileList = list(set(fileList))

        numberOfThreads = 2
        numberOfFiles = len(fileList)

        numberPerThread = int(round(float(numberOfFiles)/float(numberOfThreads)))

        fileGroups = grouper(fileList,numberPerThread)

        dirFormat = self.GetFolderFormat()

        self.sorters = list()

        iterator = itertools.count(1)

        for group in fileGroups:
            self.sorters.append(Sorter(group,outputDir,dirFormat,self.filename,
                    self.anondict,self.keep_filename,iterator=iterator,
                    test=test,listener=listener,total=numberOfFiles))

    def SetIncludeSeriesAuto(self,val):
        self.includeSeries = val

    def GetAvailableFields(self):
        for path in self.pathname:
            for root,dirs,files in os.walk(path):
                for file in files[2:]:
                    filename = os.path.join(root,file)
                    dcm = isdicom(filename)
                    if dcm:
                        return dcm.dir('')

        raise DicomFolderError(''.join([';'.join(self.pathname),' contains no DICOMs']))

class DicomFolderError(Exception):
    def __init__(self,value):
        self.value = value
    
    def __str__(self):
        return repr(self.value)


