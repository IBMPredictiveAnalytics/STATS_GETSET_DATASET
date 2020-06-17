#/***********************************************************************
# * Licensed Materials - Property of IBM 
# *
# * IBM SPSS Products: Statistics Common
# *
# * (C) Copyright IBM Corp. 1989, 2020
# *
# * US Government Users Restricted Rights - Use, duplication or disclosure
# * restricted by GSA ADP Schedule Contract with IBM Corp. 
# ************************************************************************/


import spss, spssaux

"""STATS VALLBLS FROMDATA extension command"""

__author__ =  'IBM SPSS, JKP'
__version__=  '1.0.0'

# history
# 29-Jun-2015 Original version


import spss, spssaux, spssdata, random
from extension import Template, Syntax, processcmd

v22ok = spss.GetDefaultPlugInVersion() >= "spss220"
customdsattr = "$PERMANENTDSNAME"

def doactions(filespec=None, conflict="noname", currentactivedsn=None):
    """Execute command"""
    
    # debugging
    # makes debug apply only to the current thread
    try:
        import wingdbstub
        if wingdbstub.debugger != None:
            import time
            wingdbstub.debugger.StopDebug()
            time.sleep(1)
            wingdbstub.debugger.StartDebug()
        import _thread
        wingdbstub.debugger.SetDebugThreads({_thread.get_ident(): 1}, default_policy=0)
        # for V19 use
        ##    ###SpssClient._heartBeat(False)
    except:
        pass    
    if filespec is None and currentactivedsn is None:
        raise ValueError(_("No actions were specified for this command"))
    activeds = spss.ActiveDataset().lower()
    alldatasets = getAllDatasetNames()
    
    if currentactivedsn is not None:
        if currentactivedsn.lower() != activeds and \
           currentactivedsn.lower() in alldatasets:
            raise ValueError(_("""The dataset name to be assigned is already in use for another dataset: %s""")\
                % currentactivedsn)
        spss.Submit("""DATASET NAME %(currentactivedsn)s.
            DATAFILE ATTRIBUTE ATTRIBUTE=%(customdsattr)s(%(currentactivedsn)s).""")
        
    if filespec is not None:
        # The unnamed active dataset might be empty, but we preserve it in case it isn't
        if activeds == "*":
            spss.Submit("""DATASET NAME %s.""" % ("D" + random.ranunif(.1, 1.)))        
        spss.Submit("""GET FILE="%s". """ % filespec)
        thedsn = spss.GetDataFileAttributes(customdsattr)
        if len(thedsn) == 0:
            print(_("The data file does not contain a permanent dataset name.  No session dataset name has been assigned."))
        else:
            if thedsn[0].lower() in alldatasets:
                if conflict != "override":
                    print(_("The permanent dataset name is already in use in this session. No session dataset name has been assigned."))
                else:
                    print(_("The dataset name has been removed from an already open dataset: %s") % thedsn[0])
                    spss.Submit("""DATASET NAME %s.""" % thedsn[0])
            
def getAllDatasetNames():
    """Return a list of all dataset names currently in use in lower case"""
    
    tag = "D" + str(random.uniform(.1, 1))
    spss.Submit("""OMS select tables /IF COMMAND='Dataset Display'/DESTINATION xmlworkspace='%(tag)s' VIEWER=NO
        /TAG="%(tag)s".
    DATASET DISPLAY.
    OMSEND /TAG='%(tag)s'.""" % locals())
    
    # columns were added to Datasets pivot table in V22
    if v22ok:
        xpathexpr= '//pivotTable[@subType="Datasets"]//category/dimension[@axis="column"]/category[position()=1]/cell/@text'
    else:
        xpathexpr = '//pivotTable[@subType="Datasets"]//cell/@text'
    
    # if there are no real datasets, the name (unnamed) or its translation will be in the table
    ds = spss.EvaluateXPath(tag, "/", xpathexpr)
    spss.DeleteXPathHandle(tag)
    return [d.lower() for d in ds]

def Run(args):
    """Execute the STATS GETSAV DATASETextension command"""

    args = args[list(args.keys())[0]]

    oobj = Syntax([
        Template("FILE", subc="",  ktype="literal", var="filespec"),
        Template("CONFLICTS", subc="",  ktype="str", var="conflicts", 
            vallist = ["NONAME", "OVERRIDE"]),
        Template("CURRENTACTIVEDSN", subc="", ktype="varname", var="currentactivedsn"),

        Template("HELP", subc="", ktype="bool")])

    #enable localization
    global _
    try:
        _("---")
    except:
        def _(msg):
            return msg
    # A HELP subcommand overrides all else
    if "HELP" in args:
        #print helptext
        helper()
    else:
        processcmd(oobj, args, doactions)

def helper():
    """open html help in default browser window

    The location is computed from the current module name"""

    import webbrowser, os.path

    path = os.path.splitext(__file__)[0]
    helpspec = "file://" + path + os.path.sep + \
        "markdown.html"

    # webbrowser.open seems not to work well
    browser = webbrowser.get()
    if not browser.open_new(helpspec):
        print(("Help file not found:" + helpspec))
try:    #override
    from extension import helper
except:
    pass        
