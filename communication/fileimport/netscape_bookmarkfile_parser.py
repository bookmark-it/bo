from html.parser import HTMLParser

# create a subclass and override the handler methods
class BookmarkNetscapeHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.parent_folder = None
        self.current_folder = None
        self.folder_list = []

        self.bookmark_list = []
        self.current_link_object = dict()

        self.currentIsFolder = False
        self.currentIsHyperLink = False
        self.inAGroup = False

    def handle_starttag(self, tag, attrs):
        #print(self.curentFolderName)
        if tag == 'dl' :
            self.inAGroup = True
            print("+++ NEW GROUP START+++")
            print(self.current_folder)

        if tag == 'h3' :
            self.currentIsFolder = True

        if tag == 'a' :
            self.currentIsHyperLink = True
            #print(attrs[1])
            for x, y in attrs :
                self.current_link_object[x] = y

    def handle_data(self, data):
        if self.inAGroup == True :
            pass

        if self.currentIsHyperLink == True :
            #print("a")
            self.current_link_object['title'] = data
            self.current_link_object['folder'] = self.current_folder
            self.current_link_object['folder_parent'] = self.parent_folder
            self.bookmark_list.append(self.current_link_object)

            pass
            #print("Current folder : ", self.curentFolderName)
            #print("Bookmark title: ", data)

        if self.currentIsFolder == True :
            if self.parent_folder :
                #print('has a parent')
                self.current_folder = data
                #self.folder_list.append(self.current_folder)
                temp_folder = dict()
                temp_folder['name'] = data
                temp_folder['parent'] = self.parent_folder
                self.folder_list.append(temp_folder)
                self.parent_folder = temp_folder['name']
            else :
                self.parent_folder = 'Root'



    def handle_endtag(self, tag):
        if tag == 'h3' :
            self.currentIsFolder = False

        if tag == 'a' :
            self.currentIsHyperLink = False
            self.current_link_object = dict()


        if tag == 'dl' :
            self.inAGroup = False
            print("+++ NEW GROUP END +++")
