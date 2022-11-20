#Imported Python Libraries
import os,re,requests,whois,jsbeautifier,cssbeautifier
from bs4 import BeautifulSoup
from pathlib import Path
from unidecode import unidecode
from urllib.parse import urljoin
import urllib.request

#File Functions
def Project_Directory(path):#Change Working Directory to path (string literal) - Requires: os, pathlib
    path = Path(path)#Changes Varible to Path Object
    if os.path.isdir(path) is False:#Checks if Path is a File
        path = path.parent.absolute()#Changes Path to Parent Folder
    os.chdir(path)#Change Directory to Path
    cwd = os.getcwd()#Get the current working directory (cwd)
    files = os.listdir(cwd)# Get all the files in that directory
    print("Current working directory = %r \nFiles: %s" % (cwd, files)) #Print Current Working Directory & its Files
def opener(path, flags):#Open File from Path - Requires: os
    OpenedFile = os.open(path, flags)
    return os.open(path, flags) #Return File Contents
def isLink(path):#Checks if path (String) is Valid Link - Requires: re
    if isinstance(path, str) == True:#Check if path is String
        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)#Compiles Regex to Match Valid Links
        Output = re.match(regex, path) is not None #Output is True if regex matches
    else:#Return False if path is not String
        print("Error: Path not String")
        Output = False
    return(Output)#Return True/False Boolean
def HtmlSoup(FileInfoAttrs):#Format and save an Html File from File Path(HtmlFile) - Requires: os, BeautifulSoup, unidecode, urllib.request, pathlib, re - Uses Functions: Project_Directory,opener,isLink
    HtmlFilePath = FileInfoAttrs["File"]#String Varible for URL
    if isLink(HtmlFilePath) == True:#Checks if Path is Valid Link
        Project_Directory(os.path.dirname(os.path.realpath(__file__)))#Change Directory to Parent Directory of This File's Location
        soup = BeautifulSoup(requests.get(HtmlFilePath).text, 'html.parser')#Create Html Soup
        FileInfoAttrs["FileName"] = " ".join(''.join([c for c in unidecode(soup.find_all('title')[0].get_text().strip()) if c not in set(['#', '%', '&', '{', '}', '\\', '<', '>', '*', '?', '/', '|', '$', '!', '"', ':', '@', '+', '`', '='])]).split()) #String Varible for Website Name excluding invalid characters
        if FileInfoAttrs["DebugOutput"] == True:#Log Soup if Debug Output == True
            print(soup.prettify())
    else:
        Project_Directory(os.path.dirname(HtmlFilePath))#Change Directory to Parent Directory of Html File
        FileInfoAttrs["FileName"] = str(os.path.basename(HtmlFilePath)).split('.')[0]#Save File Name for Html
        with open(os.path.basename(HtmlFilePath), 'r', opener=opener) as readfile:#Open and Read Html file
            soup = BeautifulSoup(readfile.read(), 'html.parser')#Create Html Soup
            if FileInfoAttrs["DebugOutput"] == True:#Log Soup if Debug Output == True
                print(soup.prettify())
    FileInfoAttrs["Soup"] = soup#Save Soup to FileInfoAttrs Dictionary
    return(FileInfoAttrs)#Return Dictionary With Html Soup

#Soup Functions
def Tags(FileInfoAttrs):#Find/List all Tags in soup - Requires: BeautifulSoup
    soup = FileInfoAttrs["Soup"]
    Tags = []#Storage Var
    for Tag in soup.findChildren():#Find Tags in soup
        if Tag.name not in Tags:#Prevent Duplicates in Output
            Tags.append(Tag.name)
            if FileInfoAttrs["DebugOutput"] == True:#Optional Debug Logging for Tags
                print(Tag.name)
    return(Tags)    #Return List of Tags
def Links(FileInfoAttrs):#Find links in soup - Requires: BeautifulSoup, urllib.parse
    URL = FileInfoAttrs["File"]
    soup = FileInfoAttrs["Soup"]
    links=[]#Storage Var
    for link in soup.find_all( href=True):#Find all links in soup
        FullLink = urljoin(URL,link['href']).split(' ', 1)[0]#Creates Full Link from Relative Path
        if FullLink not in links:#Remove Duplicates
            links.append(FullLink)
            if FileInfoAttrs["DebugOutput"] == True:#Optional Debug Logging for Tags
                print(FullLink)
    return(links)   #return List of links
def IDs(FileInfoAttrs):#Find IDs in soup - Requires: BeautifulSoup
    soup = FileInfoAttrs["Soup"]
    IDs=[]#Storage Var
    for ID in soup.find_all(id=True):#findall links in soup
        if ID['id'] not in IDs:#Remove Duplicates
            IDs.append(ID['id'])
            if FileInfoAttrs["DebugOutput"] == True:#Optional Debug Logging for Tags
                print(ID['id'])
    return(IDs)   #return List of IDs
def Classes(FileInfoAttrs):#Find Classes in soup - Requires: BeautifulSoup
    soup = FileInfoAttrs["Soup"]
    Classes=[]#Storage Var
    for Tag in soup.findChildren():#Find all Tags in soup
         if Tag.has_attr( "class" ):#Find all Tags with Classes in soup
            TagClasses = Tag['class']#Storage Var for Classes in Tag
            if len( TagClasses ) != 0:
                for Class in TagClasses:#Loop to add Unique Classes to Output List
                    if Class not in Classes:#Prevent Duplicates and Null Values in Output
                        Classes.append(Class)
                        if FileInfoAttrs["DebugOutput"] == True:#Optional Debug Logging for Tags
                            print(Class)
    return(Classes)   #return List of Classes
def DataSources(FileInfoAttrs):#Find Sources in soup - Requires: BeautifulSoup, re, urllib.parse  - Uses Functions: isLink
    URL = FileInfoAttrs["File"]
    soup = FileInfoAttrs["Soup"]

    DataSources=[]#Storage Var
    TagSrcs=[]#Storage Var
    Src=[]#Storage Var
    for Tag in soup.findChildren():#Search all tags
        if Tag.has_attr( "data-src" ):#Search all tags for data-src Attribute
            TagSrcs.append(Tag['data-src'])#Add Src to List
        if Tag.has_attr( "data-srcset" ):#Search all tags for data-srcset Attribute
            for i in Tag['data-srcset'].split(','):#Split Srcset list into Individual Links
                if len(i.strip()) > 0 and i.strip() not in TagSrcs:#Check for Duplicates
                    TagSrcs.append(i.strip())#Add Src to List
        if Tag.has_attr( "src" ):#Search all tags for src Attribute
            TagSrcs.append(Tag['src'])#Add Src to List
    if len( TagSrcs ) != 0:
        for Src in TagSrcs:#Loop through list of all sources
            if Src not in DataSources:#Add unique Links to Output List
                if isLink(URL) == True:#Check if Valid Link
                    Link = urljoin(URL,Src).split(' ', 1)[0]#Creates Full Link from Relative Path
                    DataSources.append(Link)
                else:
                    Link = Src
                    DataSources.append(Link)
                if FileInfoAttrs["DebugOutput"] == True:#Optional Debug Logging for Tags
                    print(Link)
    return(DataSources)   #return List of Sources

#Output Functions
def PrintDictLists(Dictionary):#Print All lists & it's Values in a Dictionary
    for Value in Dictionary.values():#Iterate Dictionary Values
        if type(Value) is list:#Check if Value is a List
            Value.sort()#Sort List for Clairity
            Key = str([Key for Key, v in Dictionary.items() if v == Value][0])#Get Ket for Value
            Padding = ""
            for i in range(int((24 - len(Key))/2)):#Create Text Padding for Output
                Padding += "-"
            print("\n"+Padding+Key+Padding)#Print Key as a Title
            for i in Value:
                print(" ┕ "+str(i))#Print List Values
def MakeDirectory(ParentDir, DirList):#Create Directory from ParentDir (Path) and Subdirectories from DirList (List) - Requires: os
        try:
            os.mkdir(ParentDir)#Create Parent Folder
        except OSError as error:#Throw if Parent Folder already exists
            print(error)#Log Error
        for Directories in DirList:#Create Sub Folders inside Parent Folder
            if Directories not in os.listdir(ParentDir):#Skips if Folder Already Exists
                try:
                    os.mkdir(os.path.join(ParentDir, Directories))#Create Folder
                except OSError as error:#Throw if Folder Cannot be Created
                    print(error)#Log Error

#Duplicate Site Functions
def DuplicateSite(FileInfoAttrs,FileInfo):#Duplicate Website Locally - Requires: os, BeautifulSoup, pathlib - Uses Functions: MakeDirectory, MakeScripts, MakeCSS, SaveData
    soup = FileInfoAttrs["Soup"]
    Dir = os.path.join(os.getcwd(), FileInfoAttrs["FileName"] + " - Local Clone")#Path For Local Clone Folder
    ChDirs = ["Scripts","Styles","Sources"]#List of Child Folders to Create
    #######-WORK IN PROGRESS-#######
    # for i in FileInfo["DataSources"]:#Loop Through DataSources to Find Other Folders to Create
    #     if bool([e for e in [".js",".css"] if(e in i)]) == False:#Skip Css/Js Sources
    #         Folder = str(Path(i).parent.absolute()).split('\\')[-1]#Parse Parent Directory Name from Source File as String
    #         if Folder not in ChDirs and "\\" not in Folder:#Check for Duplicates and Non-Valid Names
    #             ChDirs.append(Folder.capitalize())#Add Folder to List of Child Directories to Create
    #######-WORK IN PROGRESS-#######
    MakeDirectory(Dir, ChDirs)#Create Directories
    FileInfoAttrs["Output"] = True
    FileInfoAttrs = MakeScripts(FileInfoAttrs,FileInfo,Dir)
    FileInfoAttrs = MakeCSS(FileInfoAttrs,FileInfo,Dir)
    FileInfoAttrs = SaveData(FileInfoAttrs,FileInfo,Dir)

    with open(os.path.join(Dir,FileInfoAttrs["FileName"] + ".html"), 'w', opener=opener, encoding="utf-8") as writefile:
        writefile.write(FileInfoAttrs["Soup"].prettify())#Save Formated Html
def MakeScripts(FileInfoAttrs,FileInfo,Dir):
    soup = FileInfoAttrs["Soup"]
    SaveJS = FileInfoAttrs["SaveJS"]
    OuputBoolean = FileInfoAttrs["Output"]
    c = 0
    for Tag in soup.find_all("script"):
        if SaveJS == False:
            Tag.decompose()
        else:
            File = "Script-" + str(c) + ".js"
            Path = os.path.join(Dir,"Scripts",File)
            c+=1
            if len(Tag.contents) > 0:
                Code = Tag.contents[-1]
                Tag.clear()
                Tag['src'] = Path
            else:
                if Tag.has_attr( "src" ):
                    Code = requests.get([i for i in FileInfo["DataSources"] if Tag['src'] in i][-1]).text
                    Tag['src'] = Path
            with open(Path, 'w+', opener=opener, encoding="utf-8") as writefile:
                if OuputBoolean == True:
                    print("Saved File " + File)
                writefile.write(jsbeautifier.beautify(Code, jsbeautifier.default_options()))#Save Formated Html

    FileInfoAttrs["Soup"] = soup
    return(FileInfoAttrs)
def MakeCSS(FileInfoAttrs,FileInfo,Dir):
    soup = FileInfoAttrs["Soup"]
    OuputBoolean = FileInfoAttrs["Output"]
    c = 0
    # for Link in :
    for Tag in soup.find_all(["style","link"]):
        File = "Style-" + str(c) + ".css"
        Path = os.path.join(Dir,"Styles",File)
        FileList = [ i for i in Tag.attrs.values() if ".css" in i ]
        if len(FileList) > 0:
            FileList2 = [l for l in [ i for i in list(set(FileInfo["Links"] + FileInfo["DataSources"])) if ".css" in i] if FileList[0] in l]
            if  len(FileList2) > 0:
                Code = requests.get(FileList2[0]).text
                Tag[[k for k, v in Tag.attrs.items() if v == FileList[0]][0]] = Path
                with open(Path, 'w+', opener=opener, encoding="utf-8") as writefile:
                    if OuputBoolean == True:
                        print("Saved File " + File)
                    writefile.write(cssbeautifier.beautify(Code, cssbeautifier.default_options()))#Save Formated Html
                    c+=1

    FileInfoAttrs["Soup"] = soup
    return(FileInfoAttrs)
def SaveData(FileInfoAttrs,FileInfo,Dir):
    soup = FileInfoAttrs["Soup"]
    c = 0
    OuputBoolean = FileInfoAttrs["Output"]
    for Tag in soup.findChildren():#Search all tags
        if Tag.has_attr( "data-src" ):#Search all tags for Src
            Link = [i for i in FileInfo["DataSources"] if Tag['data-src'] in i][-1]
            print(Link)
            Folder = os.path.join(Dir,"Sources","Image-"+str(c)+"."+Link.split('.')[-1].split("?")[0])
            # Folder = os.path.join(Dir,str(Path(Link).parent.absolute()).split('\\')[-1].capitalize(),"Image-"+str(c)+"."+Link.split('.')[-1].split("?")[0])
            urllib.request.urlretrieve(Link, Folder)
            if OuputBoolean == True:
                print("Saved Image-"+str(c))
            Tag['data-src'] = Folder
            c+=1
        if Tag.has_attr( "data-srcset" ):
            SrcSet = []
            SrcSet2 = []
            for i in Tag['data-srcset'].split(','):
                if len(i.strip()) > 0 :
                    SrcSet.append(i.strip())
            for Src in SrcSet:
                Link = [i for i in FileInfo["DataSources"] if Src.split(' ', 1)[0] in i][-1]+"%20"+Src.split(' ', 1)[-1]
                print(Link)
                Folder = os.path.join(Dir,"Sources","Image-"+str(c)+"."+Link.split('.')[-1].split("?")[0])
                # Folder = os.path.join(Dir,str(Path(Link).parent.absolute()).split('\\')[-1].capitalize(),"Image-"+str(c)+"."+Link.split('.')[-1].split("?")[0])
                SrcSet2.append(Folder)
                urllib.request.urlretrieve(Link, Folder)
                if OuputBoolean == True:
                    print("Saved Image-"+str(c))
                c+=1
            Tag['data-srcset'] = ','.join(SrcSet2)

        if Tag.has_attr( "src" ):
            if ".js" not in Tag['src'] and ".css" not in Tag['src']:
                Link = [i for i in FileInfo["DataSources"] if Tag['src'] in i][-1]
                print(Link)
                Folder = os.path.join(Dir,"Sources","Image-"+str(c)+"."+Link.split('.')[-1].split("?")[0])
                # Folder = os.path.join(Dir,str(Path(Link).parent.absolute()).split('\\')[-1].capitalize(),"Image-"+str(c)+"."+Link.split('.')[-1].split("?")[0])
                if ".js" not in Folder:
                    urllib.request.urlretrieve(Link, Folder)
                    if OuputBoolean == True:
                        print("Saved Image-"+str(c))
                    Tag['src'] = Folder
                    c+=1



    FileInfoAttrs["Soup"] = soup
    return(FileInfoAttrs)

#Input Functions
def InputBoolean(Prompt):
    run = True
    while run == True:
        UserInput = str(input(Prompt + " - Input Y/N\n")).upper().strip()
        if UserInput[0] == 'Y':
            run = False
            UserInput = True
        elif UserInput[0] == 'N':
            run = False
            UserInput = False
        else:
            print(UserInput + " is an Invalid Input")
    return(UserInput)

#Main Function
def main():

    file = r'C:\Users\Marcu\Dropbox\000-BRANDING\000-Fragile Branding\Archive\HtmlPages\Home\Home.html'
    # URL = "https://luu-dan.com"
    # URL = "https://fragileservices.com"
    # URL = "https://kong.cash"
    print("Enter a URL to CLone Webpage")
    URL = input("Input URL: ")


    FileInfoAttrs = {}#Attributes for File/Script
    FileInfoAttrs["File"] = URL#Webpage to Grab
    FileInfoAttrs["Output"] = InputBoolean("File Save Output Log: ")#Boolean to Log File Saving in Console
    FileInfoAttrs["DebugOutput"] = InputBoolean("Debug Output Log: ")#Boolean to Log Debug Points in Console
    FileInfoAttrs["SaveJS"] = InputBoolean("Save JS From Site? (May Slow Page Load Time): ")#Boolean to Save JS Files from site, If True site may take longer to load.
    FileInfoAttrs = HtmlSoup(FileInfoAttrs)


    FileInfo = {
        "Tags" : Tags(FileInfoAttrs),
        "Links" : Links(FileInfoAttrs),
        "IDs" : IDs(FileInfoAttrs),
        "Classes" : Classes(FileInfoAttrs),
        "DataSources" : DataSources(FileInfoAttrs),
    }
    DuplicateSite(FileInfoAttrs,FileInfo)
    PrintDictLists(FileInfo)


if __name__ == "__main__":
    main()
