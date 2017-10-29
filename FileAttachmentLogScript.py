import os, sys, tempfile, datetime
import maya.standalone
maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm

filePath = sys.argv[1]
listPath = sys.argv[2]
errorListPath = listPath.replace('.txt', '_error.txt')
logfile = listPath.replace('.txt', '_batchLog.txt')

def logging(inText):
	efile = open(logfile, 'a')
	now = datetime.datetime.now().strftime('%H:%M:%S')
	inText = str('\n%s %s'%(now, str(inText)))
	efile.write(inText)
	efile.close()


def exitstand(e=None):
	maya.standalone.uninitialize()
	if e != None:
		errorfile = '%s%s' %(tempfile.gettempdir(), 'batchResult.txt')
		if os.path.exists(errorfile):os.remove(errorfile)
		with open(errorfile, 'w') as mfile:
			mfile.write(str(e))
		mfile.close()
		sys.exit(-1)
	else:
		sys.exit(0)

plugin_list = ['GamePipeline', 'MayaMuscle', 'redshift4maya', 'bifrostvisplugin', 'dx11Shader', 'Mayatomr',
			'BifrostMain', 'deformerEvaluator', 'shaderFXPlugin', 'bifrostshellnode',
			'gameFbxExporter', 'GPUBuiltInDeformer', 'stereoCamera', 'lookdevKit', 'Unfold3D',
			'Type', 'poseDeformer', 'fbxmaya', 'poseReader', 'modelingToolkit', 'OneClick', 'AbcImport', 'AbcExport', 'AbcBullet']

logging('initializing maya')

try:
	mel.eval("source UserSetupStand.mel")
	execfile('%s//userSetup.py' %(os.environ['myDocPath']))
	loaded_plugins = cmds.pluginInfo(query=True, listPlugins=True)
	for p in plugin_list:
		if p not in loaded_plugins:
			cmds.loadPlugin(p)
except Exception, e:
	exitstand(str(repr(e)))

logging('maya initialized')

'''
This function unlocks and loads references in the maya file.
'''
def unLocknLoadReferences():
	
	badRefs = ['sharedReferenceNode', '_UNKNOWN_REF_NODE_']

	logging('Unlocking refereneces')

	#load file without any references
	cmds.file(filePath, open=True, force=True, lrd='none', pmt=False)

	#unlock any locked references and load them
	for i in cmds.ls(type='reference'):
		if i not in badRefs:
			logging('Unlocking %s' %i)
			cmds.setAttr('%s.locked' %i, False)
			logging('Loading %s' %i)
			cmds.file(lr=i, lrd="all")

'''
This function checks for drive letters in all file paths, if found
add it to a list and return the list.
'''
def checkDriveLetter():
	errorFiles = []

	#file nodes
	for i in pm.ls(type='file'):
		if not i.getAttr('ftn').startswith('$'):
			errorFiles.append(i.getAttr('ftn'))

	#references
	for i in pm.listReferences():
		if not i.unresolvedPath().startswith('$'):
			errorFiles.append(i.unresolvedPath())

	#cache
	for i in pm.ls(type='cacheFile'):
		if i.getAttr('cachePath') and not i.getAttr('cachePath').startswith('$'):
			errorFiles.append(i.getAttr('cachePath'))

	#redshiftproxy
	for i in pm.ls(type='RedshiftProxyMesh'):
		if not i.getAttr('fn').startswith('$'):
			errorFiles.append(i.getAttr('fn'))

	#alembiccache
	for i in pm.ls(type='AlembicNode'):
		if not i.getAttr('abc_File').startswith('$'):
			errorFiles.append(i.getAttr('abc_File'))

	return errorFiles


def main():

	unLocknLoadReferences()
	logging('Scene file opened')

	logging('Checking for drive letter')
	error = checkDriveLetter()

	#if drive letter found in any path, write the paths to a file and return.
	if error:
		logging('Driveletter found')
		with open(errorListPath, 'w') as erList:
			for e in error:
				erList.write(e+"\n")
		print 'Environment path missing in some files. Check' + errorListPath + 'for more details'
		return

	#if all paths are good, fetch the paths and write it out to a file.
	logging('Paths are good')
	logging('Getting Files')
	files = cmds.file(q=True, l=True)

	logging('Writing to %s' %listPath)

	with open(listPath, 'w') as _list:
		for _file in files:
			if _file != filePath:
				_list.write(_file + "\n")

	logging('Done')


try:
	main()
except Exception, e:
	exitstand(str(repr(e)))


