# iTunes TV Folder Organiser

This application is for use with the iTunes TV packaging workflow.

Requires compilation with py2app or similar.

Instructions for use:

- Drop folder containing unsorted episode MOVs and/or metadata XMLs and/or QC note PDFs into according tab.
    
- Hit 'Organise Folder' to create .iTMSP folders and move all files into corresponding folder.

    nb. Metadata XMLs will be renamed, removing each appended sequential digit.
 

---
I used:
- Python 2.7
- wxPython (a GUI framework)


Written as I learnt my first programming language. Basic principles such as SRP and DRY were not adhered to.
