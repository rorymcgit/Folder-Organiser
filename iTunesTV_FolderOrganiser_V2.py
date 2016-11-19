import os
import sys
import wx
import shutil
import re

versionNumber = 'v2.0'

"""
This application is for use with the iTunes TV packaging workflow.
Instructions for use:
    - Drop folder containing unsorted episode MOVs and/or metadata XMLs and/or QC note PDFs into according tab
    - Hit 'Organise Folder' to create folders and move files into corresponding folder.

    nb. Metadata XMls will be renamed, removing appended 1/2/3 etc.
"""


class ScrolledWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(410, 200), style=wx.DEFAULT_FRAME_STYLE & ~ (wx.RESIZE_BORDER |
                                                wx.RESIZE_BOX | wx.MAXIMIZE_BOX))

        self.tabbed = wx.Notebook(self, -1, style=(wx.NB_TOP))

        menuBar = wx.MenuBar()
        self.CreateStatusBar()
        self.SetMenuBar(menuBar)

        self.findMovemovs = MovMoverFolderMaker(self.tabbed, self)
        self.moveXMLPDF = PDF_XML_mover(self.tabbed, self)

        self.tabbed.AddPage(self.findMovemovs, "MOV")
        self.tabbed.AddPage(self.moveXMLPDF, "PDF / XML")
        self.tabbed.SetSelection(0)

        wx.CallAfter(self.SetStatusText, "Hungry for folders...")

        self.SetBackgroundColour((210, 210, 210))

        self.Centre()
        self.Show()


class MovMoverFolderMaker(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent)

        outputtxt3 = '''Drop iTunes TV Container ID folder to package MOVs:'''
        wx.StaticText(self, -1, outputtxt3, pos=(5, 10), style=wx.ALIGN_CENTRE)

        self.drop_target = MyFileDropTarget(self)
        self.SetDropTarget(self.drop_target)
        self.tc_files = wx.TextCtrl(self, wx.ID_ANY, pos=(10, 40), size=(365, 25))

        self.buttonClose = wx.Button(self, -1, "Close", pos=(5, 75))
        self.buttonClose.Bind(wx.EVT_BUTTON, self.OnClose)

        self.buttonSubmit = wx.Button(self, -1, "Organise Folder", pos=(185, 15), size=(180, 140))
        self.buttonSubmit.Bind(wx.EVT_BUTTON, self.findMoveMovs)

        self.SetBackgroundColour((205, 205, 205))

        self.Show()

    def findMoveMovs(self, event):
        """Traverses directories in drop target, if MOVs are found they are moved to corresponding .ITMSP (using
         MOV filename). If .ITMSP doesn't exist, it is created with MOV filename as foldername."""
        
        for root, dirs, files in os.walk(self.dropFiles):
            for file1 in files:
                if file1.endswith('.mov') and not file1.startswith('.'):
                    filenamepath = os.path.join(root, file1)
                    newITMSP = filenamepath.replace(".mov", ".itmsp")

                    if not os.path.isdir(newITMSP):
                        os.mkdir(newITMSP)
                        shutil.move(filenamepath, newITMSP)
                    elif os.path.isdir(newITMSP):
                        shutil.move(filenamepath, newITMSP)

    def setSubmissionDrop(self, dropFiles):
        self.listEmpty = False
        self.tc_files.SetValue(','.join(dropFiles))
        self.dropFiles = dropFiles[0]

    def OnClose(self, e):
        CloseApp()


class PDF_XML_mover(wx.Panel):
    def __init__(self, parent, frame):
        wx.Panel.__init__(self, parent)

        outputtxt3 = '''Drop iTunes TV Container ID folder to package XMLs/PDFs:'''
        wx.StaticText(self, -1, outputtxt3, pos=(5, 10), style=wx.ALIGN_CENTRE)

        self.drop_target = MyFileDropTarget(self)
        self.SetDropTarget(self.drop_target)
        self.tc_files = wx.TextCtrl(self, wx.ID_ANY, pos=(10, 40), size=(365, 25))

        self.buttonClose = wx.Button(self, -1, "Close", pos=(5, 75))
        self.buttonClose.Bind(wx.EVT_BUTTON, self.OnClose)

        self.buttonSubmit = wx.Button(self, -1, "Organise Folder", pos=(185, 15), size=(180, 140))
        self.buttonSubmit.Bind(wx.EVT_BUTTON, self.pdfMove)
        self.buttonSubmit.Bind(wx.EVT_BUTTON, self.xmlMove)

        self.SetBackgroundColour((205, 205, 205))

        self.Show()

    def pdfMove(self, event):
        """Traverses directories in drop target, if PDFs are found they are moved to corresponding .ITMSP (using
         the vendor ID from head of PDF filename). If .ITMSP doesn't exist, it is created"""
        for root, dirs, files in os.walk(self.dropFiles):
            for file2 in files:
                if file2.endswith('.pdf') and not file2.startswith('.'):
                    filenamepath2 = os.path.join(root, file2)
                    filename_prefix = file2.split('-')[0]
                    dest_dir = os.path.join(root, filename_prefix + '.itmsp')

                    if not os.path.isdir(dest_dir):
                        os.mkdir(dest_dir)

                    os.rename(filenamepath2, os.path.join(dest_dir, file2))

            event.Skip()
            break

    def xmlMove(self, event):
        """Traverses directories in drop target, if XMLs are found they are moved to corresponding .ITMSP (using
         the vendor ID from within the XML). If .ITMSP doesn't exist, it is created."""
        for root, dirs, files in os.walk(self.dropFiles):
            for file3 in files:
                if file3.endswith('.xml') and not file3.startswith('.'):
                    filenamepath3 = os.path.join(root, file3)

                    with open(filenamepath3) as f:
                        content = f.readlines()

                        for a in content:
                            if '<vendor_id>' in a:
                                a = re.sub('<vendor_id>', '', a)
                                a = re.sub('</vendor_id>', '', a)
                                a = re.sub(' ', '', a)
                                a = re.sub('\n', '', a)
                                dest_dir2 = os.path.join(root, a + '.itmsp')

                                if not os.path.isdir(dest_dir2):
                                    os.mkdir(dest_dir2)

                                os.rename(filenamepath3, os.path.join(dest_dir2, re.sub(r'\d+', '', file3)))
            event.Skip()
            break

    def setSubmissionDrop(self, dropFiles):
        self.listEmpty = False
        self.tc_files.SetValue(','.join(dropFiles))
        self.dropFiles = dropFiles[0]

    def OnClose(self, e):
        CloseApp()


class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, window):
        wx.FileDropTarget.__init__(self)
        self.window = window

    def OnDropFiles(self, x, y, filenames):
        self.window.setSubmissionDrop(filenames)


class CloseApp(wx.Frame):
    def __init__(e):
        sys.exit(0)

if __name__ == "__main__":
    app = wx.App()
    ScrolledWindow(None, -1, 'iTunes TV Folder Organiser ' + versionNumber)
    app.MainLoop()


