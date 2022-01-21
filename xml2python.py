
import sys
import os
import xmltodict
from typing import List

# change class dict_path_finder from https://github.com/kingname/JsonPathFinder/blob/main/JsonPathFinder.py
class dict_path_finder:
    def __init__(self, data, mode='key'):
        self.data = data
        self.mode = mode

    def iter_node(self, rows, road_step, target):
        if isinstance(rows, dict):
            key_value_iter = (x for x in rows.items())
        elif isinstance(rows, list):
            key_value_iter = (x for x in enumerate(rows))
        else:
            return
        for key, value in key_value_iter:
            current_path = road_step.copy()
            current_path.append(key)
            if self.mode == 'key':
                check = key
            else:
                check = value
            if check == target:
                yield current_path
            if isinstance(value, (dict, list)):
                yield from self.iter_node(value, current_path, target)

    def iter_node_all_keys(self, rows, road_step):
        if isinstance(rows, dict):
            key_value_iter = (x for x in rows.items())
        elif isinstance(rows, list):
            key_value_iter = (x for x in enumerate(rows))
        else:
            return
        for key, value in key_value_iter:
            current_path = road_step.copy()
            current_path.append(key)
            if self.mode == 'key':
                check = key
                if isinstance(value,str) or isinstance(value,str):
                    current_path.append('='+str(value))    
                yield current_path    
            if isinstance(value, (dict, list)):
                yield from self.iter_node_all_keys(value, current_path)
    
    def find_one(self, target: str) -> list:
        path_iter = self.iter_node(self.data, [], target)
        for path in path_iter:
            return path
        return []

    def find_all(self, target) -> List[list]:
        path_iter = self.iter_node(self.data, [], target)
        return list(path_iter)
    
    def find_all_keys(self):
        path_iter = self.iter_node_all_keys(self.data, [])
        return path_iter
    

class TreeNode(object):
    def __init__(self, name, parent=None):
        super(TreeNode, self).__init__()
        self.name = name
        self.parent = parent
        self.child = {}
        self.data = None

    def __repr__(self) :
        return 'TreeNode(%s)' % self.name

    def __contains__(self, item):
        return item in self.child

    def __len__(self):
        """return number of children node"""
        return len(self.child)

    def __bool__(self):
        """always return True for exist node"""
        return True

    @property
    def path(self):
        """return path string (from root to current node) recursion"""
        if self.parent:
            ret = '%s/%s' % (self.parent.path.strip(), self.name)
            return ret
        else:
            return self.name

    def get_child(self, name, default=None):
        """get a child node of current node"""
        return self.child.get(name, default)

    def add_child(self, name, data):
        obj = TreeNode(name)
        obj.data = data
        obj.parent = self
        self.child[name] = obj
        return obj

    def del_child(self, name):
        """remove a child node from current node"""
        if name in self.child:
            del self.child[name]    
        
    def find_child(self, path, create=False):
        """find child node by path/name, return None if not found"""
        # convert path to a list if input is a string
        path = path if isinstance(path, list) else path.split()
        cur = self
        for sub in path:
            # search
            obj = cur._get_child(sub)
            if obj is None and create:
                # create new node if need
                obj = cur.add_child(sub)
            # check if search done
            if obj is None:
                break
            cur = obj
        return obj

    def items(self):
        return self.child.items()

    def dump(self,ss,indent=0):
        """dump tree to string"""
        # ╚ ∟ ┗ └
        tab = '    '*(indent-1) + ' └- ' if indent > 0 else ''
        if isinstance(self.data,str) or isinstance(self.data,int):
#            print('%s%s%s' % (tab, str(self.name) + ':',self.data))
            ret = '%s%s%s%s' % (tab, str(self.name) + ':',self.data,'\n')
            ss[0] += ret
        else:    
#            print('%s%s' % (tab, self.name))
            ret = '%s%s%s' % (tab, str(self.name),'\n')
            ss[0] += ret
        for name, obj in self.items():
            obj.dump(ss,indent+1)
    
    def _get_child(self, name):
        if name in self.child:
            return self.child[name]
        else:
            ret = []
            for k,v in self.child.items():
                if isinstance(k,int):
                    if name in v.child:
                        ret.append(v.child)
            return ret
        return None   
    
    def get_parent(self):
        if isinstance(self.parent.name,str):
            return self.parent
        else:
            if isinstance(self.parent.name, int):
                return self.parent.parent
            else:
                return None
          
def add_root_tree_node():
    root = TreeNode('')
    return root

def add_tree_node_in_folder(node,d):
    if isinstance(d,dict):
        for k,v in d.items():
            if isinstance(v,str) or isinstance(v,int): 
                ret = node.add_child(k,v)
                add_tree_node_in_folder(ret, v)
            else:
                ret = node.add_child(k,v)
                add_tree_node_in_folder(ret, v)                
    elif isinstance(d,list):     
        for dd in d:
            ret = node.add_child(d.index(dd),dd)
            add_tree_node_in_folder(ret, dd) 
    else:
        pass

if __name__ == '__main__':
    if '.xml' not in sys.argv[1]:
        print('Error need xml file','python3 xml2python.py xxx.xml')
        exit()
    try:
        f = open(sys.argv[1],'rb')
        xml = f.read()
    except Exception as e:
        print(e)
        exit()
    f.close()
    code_head = '''
# pip install addict
# pip install xmltodict
from addict import Dict
import xmltodict
def change_dict_list(d,key=None):
    l=[]
    global isGo
    if isinstance(d,dict):
        for k,v in d.items():
            if isinstance(k,int)==False:
                isGo = d
                change_dict_list(v,k)
            else:
                l=[v for (_,v) in d.items()]
                isGo[key]=l
                break
    for i in l:
        change_dict_list(i)
                    
def gen_xml():
    d=Dict()
{code_block}
    d = d.to_dict()
    change_dict_list(d)
    xml = xmltodict.unparse(d, pretty=True)
    return xml

print(gen_xml())
'''           
    try:
        d = xmltodict.parse(xml)
    except Exception as e:
        print('Error in xmltodict.parse:',e)
        exit(0)                                  
    root = add_root_tree_node()
    add_tree_node_in_folder(root,d)
    sss = ['']
    sss_path = ''
    root.dump(sss)
    finder = dict_path_finder(d)
    path = finder.find_all_keys()
    code_list = []
    for i in path:
        code = 'd'
        for step in i:
            step = str(step)
            if '=' in step:
                code += '="' + step.split('=',1)[1] +'"'
                code_list.append(code)
            elif step.isdigit():
                code += '['+step+']'
            else:
                code += '["'+step+'"]'
    code_list_str = ''
    for i in code_list:
        code_list_str+= '    '+i+'\n'
    code_head = code_head.format(code_block=code_list_str)             
    print(code_head)        
