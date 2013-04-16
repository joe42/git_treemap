#!/usr/bin/python
# -*- coding: utf-8 -*-
#================================================================================
# List of all the files, total count of files and folders & Total size of files.
#================================================================================
import os
import sys
from copy import deepcopy
import json
import re
from string import Template
import codecs

rootdir = sys.argv[1]

def get_color_by_filesize(size_in_bytes):
    if size_in_bytes > 20000:
        return "#bd0000"
    if size_in_bytes > 17500:
        return "#eb0603"#
    if size_in_bytes > 15000:
        return "#d96901"
    if size_in_bytes > 10000:
        return "#0554d9"
    if size_in_bytes > 6200:
        return "#0200e8"
    else:
        return "#0300c7"

    
def get_color_by_changed_lines(lines):
    if lines > 50:
        return "#990000"
    if lines > 30:
        return "#FF0000"
    if lines > 16:
        return "#FF6600"
    if lines > 8:
        return "#FFCC00"
    if lines > 4:
        return "#145214"
    else:
        return "#33CC33"    
    
def get_commit_color_by_time(last_changed):
    "last_changed - time in seconds from epoche "
    difference_in_hours = last_changed/60.0/60
    if difference_in_hours > 14*24:
        return "#020092"
    if difference_in_hours > 7*24:
        return "#0200fc"
    if difference_in_hours > 48:
        return "#0663ff"
    if difference_in_hours > 24:
        return "#ff7c01"
    if difference_in_hours > 12:
        return "#eb0603"
    else:
        return "#a80000"
    
def get_package_color_by_time(last_changed):
    "last_changed - time in seconds from epoche "
    difference_in_hours_to_now = (time.time() - last_changed)/60.0/60
    if difference_in_hours_to_now > 48:
        return "#444444"
    else:
        return "#990000"

class MyFolder(object):
    def __init__(self, path):
        self.__items = {}
        self.__path = path
        self.__name = os.path.basename(path)
        self.__parent_dir = os.path.dirname(path)

    def get_name(self):
        return self.__name
    
    def get_path(self):
        return self.__path
    
    def get_parent_dir(self):
        return self.__parent_dir

    def get_size(self):
        ret = 0
        for item in self.__items.values():
            ret += item.get_size()
        return ret
    
    def get_items(self):
        return self.__items

    def add_item(self, item):
        self.__items[item.get_name()] = item

    def del_item(self, item_name):
        del self.__items[item_name]
        
    def get_dict_repr(self):
        ret = {}
        children = []
        for item in self.__items.values():
            children.append( item.get_dict_repr() )
        ret["children"] = children
        ret["id"] = self.get_path()
        ret["name"] = self.get_name()
        ret["data"] = {"$area":self.get_size(), "isPackage": True}
        return ret
    #deprecated
    def __get_size_of_largest_file(self):
        ret = 0
        for item in self.__items.values():
            try:
                val = item.__get_size_of_largest_file()
            except:
                val = item.get_size()
            if val > ret:
                ret = val 
        return ret
        

class MyFile(object):
    def __init__(self, path):
        self.__path = path
        self.__name = os.path.splitext(os.path.basename(path))[0]
        self.__size_in_bytes = os.path.getsize(path)
        self.__parent_dir = os.path.dirname(path)
        self.__lines = len(open(path).readlines())

    def get_name(self):
        return self.__name
    
    def get_path(self):
        return self.__path
    
    def get_parent_dir(self):
        return self.__parent_dir

    def get_size(self):
        return self.__size_in_bytes
    
    def cnt_lines(self):
        return self.__lines
    
    def get_dict_repr(self):
        ret = {}
        children = []
        ret["children"] = []
        ret["data"] = {"$color": get_color_by_filesize(self.get_size()), "$area": self.get_size(), "lines":self.cnt_lines(), "isPackage": False}
        ret["id"] = self.get_path()
        ret["name"] = self.get_name()
        return ret

from git import *
import git
import time
    
class GitFolder(MyFolder): 
    def __init__(self, path):
        super(GitFolder, self).__init__(path)
    
    def get_changed_lines(self):  
        ret = 0
        for item in self.get_items().values():
            ret += item.get_changed_lines()
        return ret
    
    def get_changed_lines_max(self):  
        ret = 0
        for item in self.get_items().values():
            if isinstance(item, GitFolder):
                if ret < item.get_changed_lines_max():
                    ret = item.get_changed_lines_max()
            else:
                if ret < item.get_changed_lines():
                    ret = item.get_changed_lines()
        return ret
    
    def get_recent_commit_date(self):  
        ret = 1
        for item in self.get_items().values():
            if ret < item.get_recent_commit_date():
                ret = item.get_recent_commit_date()
        return ret

    def get_dict_repr(self):
        ret = {}
        children = []
        for item in self.get_items().values():
            if item.get_changed_lines() == 0:
                continue
            children.append( item.get_dict_repr() )
        ret["children"] = children
        ret["id"] = self.get_path()
        ret["name"] = self.get_name()
        area = self.get_changed_lines()
        ret["data"] = {"$area":area, "$color": get_package_color_by_time(self.get_recent_commit_date()), "isPackage": True}
        return ret
        
class GitFile(MyFile):
    def __init__(self, path, max_commits=6):
        super(GitFile, self).__init__(path)
        self._repo = Repo(rootdir)    
        self.__max_commits = max_commits
    
    def get_max_commits(self):
        return self.__max_commits
    
    def get_changed_lines(self):  
        ret = 0
        cnt_commits = self.get_max_commits()
        for commit in self.__get_last_commits():
            if cnt_commits == 0 or (self._repo.head.commit.committed_date-commit.committed_date)/60.0/60 > 28*24:
                break
            cnt_commits -= 1
            ret += self._get_changed_lines_of_commit(commit.hexsha)
        return ret
    
    def _get_changed_lines_of_commit(self, hash):
        ret = 0
        g=git.Git(rootdir)
        log = g.log('--shortstat', '--pretty=tformat:','-1', hash,self.get_path())
        added_lines = re.findall(' (\\d+) insertion', log) # 1 file changed, 4 insertions(+), 7 deletions(-)
        deleted_lines = re.findall(' (\\d+) deletion', log) # 1 file changed, 4 insertions(+), 7 deletions(-)
        if len(added_lines) > 0:
            ret += sum(map(int, list(added_lines[0])))
        if len(deleted_lines) > 0:
            ret += sum(map(int, list(deleted_lines[0])))
        return ret
    
    def get_recent_commit_date(self):
        """returns: seconds from epoche of the most recent commit date or 1 if there is no commit"""
        for commit in self.__get_last_commits():
            return commit.committed_date #return first commit date
        return 1

        
    def get_dict_repr(self):
        total_size_of_commits = 0
        children = []
        #dont show old commits
        cnt_commits = self.get_max_commits()
        for commit in self.__get_last_commits():
            if cnt_commits == 0 or (self._repo.head.commit.committed_date-commit.committed_date)/60.0/60 > 28*24:
                break
            cnt_commits -= 1
            child = {}
            child["children"] = []
            changed_lines = self._get_changed_lines_of_commit(commit.hexsha)
            child["data"] = {"$color": get_commit_color_by_time(self._repo.head.commit.committed_date-commit.committed_date ), 
                             "$area": changed_lines, 
                             "changed lines:": changed_lines, 
                             "date": time.ctime(commit.committed_date),
                             "hash": commit.hexsha,
                             "message": commit.message,
                             "isPackage": False}
            child["id"] = commit.hexsha+self.get_path()
            child["name"] = "commit"
            total_size_of_commits += changed_lines
            children.append(child)
        ret = {}
        ret["children"] = children
        ret["id"] = self.get_path()
        ret["name"] = self.get_name()
        ret["data"] = {"$area":total_size_of_commits, "isPackage": False}
        return ret
        
    def __get_last_commits(self):
        ret = []
        g=git.Git(rootdir)
        hashes = g.log('--pretty=%H','--follow','--',self.get_path()).split('\n') 
        if hashes[0] != '':
            ret = [self._repo.rev_parse(hash) for hash in hashes]
        return ret
    
class GitFolderByAuthor(GitFolder):
    def __init__(self, path):
        super(GitFolder, self).__init__(path)
    
    def get_dict_repr(self, author=None):
        ret = {}
        if author == None:
            #print "Starts folder by author:"
            for author in self.get_authors():
                #print self.get_name()+" author "+author
                repr = {}
                children = []
                for item in self.get_items().values():
                    if item.get_changed_lines(author) == 0:
                        continue
                    children.append( item.get_dict_repr(author) )
                repr["children"] = children
                repr["id"] = self.get_path()
                repr["name"] = self.get_name()
                area = self.get_changed_lines(author)
                repr["data"] = {"$area":area, "$color": get_package_color_by_time(self.get_recent_commit_date()), "isPackage": True}
                ret[author] = repr
        else:
            #print "start with author:"+author.encode("utf8")
            ret = {}
            children = []
            for item in self.get_items().values():
                if item.get_changed_lines(author) == 0:
                    continue
                children.append( item.get_dict_repr(author) )
            ret["children"] = children
            ret["id"] = self.get_path()
            ret["name"] = self.get_name()
            area = self.get_changed_lines(author)
            ret["data"] = {"$area":area, "$color": get_package_color_by_time(self.get_recent_commit_date()), "isPackage": True}
        return ret
    
    
    def get_changed_lines(self, author):  
        ret = 0
        for item in self.get_items().values():
            ret += item.get_changed_lines(author)
        return ret
    
    def get_authors(self):
        g=git.Git(rootdir)
        authors = g.log('--format="%aN"').replace('"','').split('\n')
        #print repr(set(authors))
        return list(set(authors))

class GitFileByAuthor(GitFile):
    def __init__(self, path, max_commits=6):
        super(GitFileByAuthor, self).__init__(path, max_commits)
    
    def get_changed_lines(self, author):  
        ret = 0
        cnt_commits = self.get_max_commits()
        for commit in self.__get_last_commits(author):
            if cnt_commits == 0 or (self._repo.head.commit.committed_date-commit.committed_date)/60.0/60 > 28*24:
                break
            cnt_commits -= 1
            ret += self._get_changed_lines_of_commit(commit.hexsha)
        return ret
        
    def __get_last_commits(self, author):
        ret = []
        g=git.Git(rootdir)
        hashes = g.log('--pretty=%H', '--author', author.decode("utf8").encode("utf8"),'--follow','--',self.get_path()).split('\n') 
        #print hashes
        if hashes[0] != '':
            ret = [self._repo.rev_parse(hash) for hash in hashes]
        return ret

    def get_dict_repr(self, author):
        total_size_of_commits = 0
        children = []
        #dont show old commits
        cnt_commits = self.get_max_commits()
        for commit in self.__get_last_commits(author):
            if cnt_commits == 0 or (self._repo.head.commit.committed_date-commit.committed_date)/60.0/60 > 28*24:
                break
            cnt_commits -= 1
            child = {}
            child["children"] = []
            changed_lines = self.get_changed_lines(author)
            child["data"] = {"$color": get_commit_color_by_time(self._repo.head.commit.committed_date-commit.committed_date ), 
                             "$area": changed_lines, 
                             "changed lines:": changed_lines, 
                             "date": time.ctime(commit.committed_date),
                             "hash": commit.hexsha,
                             "message": commit.message,
                             "isPackage": False}
            child["id"] = commit.hexsha+self.get_path()
            child["name"] = "commit"
            total_size_of_commits += changed_lines
            children.append(child)
        ret = {}
        ret["children"] = children
        ret["id"] = self.get_path()
        ret["name"] = self.get_name()
        ret["data"] = {"$area":total_size_of_commits, "isPackage": False}
        return ret
    

            
class SimpleTreeMapBuilder(object):  
    def create_dir(self, path):
        return MyFolder(path)
    
    def create_file(self, path):
        return MyFile(path)
    
    def build_structure(self, parent_dir="."):
        """Build a directory structure with MyFolder and MyFile objects."""         
        src_directory = self.create_dir(parent_dir)
        walk_dict = {parent_dir: src_directory}
        for root, subFolders, files in os.walk(rootdir):
            dir = walk_dict[root] 
            for file in files:
                path = root+"/"+file
                dir.add_item(self.create_file(path))
            for subFolder in subFolders:
                path = root+"/"+subFolder
                folder = self.create_dir(path)
                dir.add_item( folder )
                walk_dict[path] = folder  
        return src_directory
    
class GitTreeMapBuilder(SimpleTreeMapBuilder):
    """Build a directory structure with GitFolder and GitFile objects."""  
    def create_dir(self, path):
        return GitFolder(path)
    
    def create_file(self, path):
        return GitFile(path)
    
class GitTreeMapByAuthorBuilder(GitTreeMapBuilder):
    """Build a directory structure with GitFolderByAuthor and GitFileByAuthor objects."""        
    def create_dir(self, path):
        return GitFolderByAuthor(path)
    
    def create_file(self, path):
        return GitFileByAuthor(path)
    
src_directory_simple = SimpleTreeMapBuilder().build_structure(rootdir)
src_directory_git = GitTreeMapBuilder().build_structure(rootdir)
src_directory_authors = GitTreeMapByAuthorBuilder().build_structure(rootdir)


template = Template(codecs.open('treemap.tpl','r', encoding = "utf8").read())
html = template.safe_substitute(dict(filesize_treemap=json.dumps(src_directory_simple.get_dict_repr(), indent=4),
                                     git_treemap=json.dumps(src_directory_git.get_dict_repr(), indent=4),
                                     authors_treemap=json.dumps(src_directory_authors.get_dict_repr(), indent=4).encode('utf8'),
                                     authors=json.dumps(src_directory_authors.get_authors(), indent=4).encode('utf8')))
#print html
codecs.open('treemap.html','w', encoding = "utf8").write(html)

