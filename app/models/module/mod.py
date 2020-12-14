from enum import Enum
import zipfile
import os
import shutil
import requests

class Status(Enum):
    UNFIND  = 0
    INCLOUD = 1
    USED    = 2
    UNUSED  = 3

class RunStatus(Enum):
    SUCCESS = 0
    DID     = 1
    FAILURE = 2

class ModuleBag:
    name: str
    main_version_status:Status
    def __init__(self, name: str):
        pass


class Module:
    name: str
    version: str
    unique_name: str
    status: Status = None
    url: str = ''
    # 不要调用
    tag: str 
    description: str
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.unique_name = name + (version if version != '~' else '')
        self.status = property(self.get_status,self.set_status)
    def get_status(self):
        path = 'app/modules.mods'
        para = Tool.get_params(path,self.unique_name)
        if para == None:
            return Status.INCLOUD
        elif para[2] == 'False':
            return Status.UNUSED
        else:
            return Status.USED
    def set_status(self, status):
        path = 'app/modules.mods'
        if self.status == status:
            return
        # 当是已下载的状态
        if self.status == Status.USED or self.status == Status.UNUSED:
            if status == Status.USED:
                Tool.set_params(path,self.unique_name,[self.unique_name,'True'])
            elif status == Status.UNUSED:
                Tool.set_params(path,self.unique_name,[self.unique_name,'False'])
            else:
                # 当新状态不是已下载状态时
                # 擦除行
                Tool.del_line(path,self.unique_name + ' ')
        else:
            # 当本身不存在时,
            if status == Status.UNUSED:
                Tool.add_line(path,self.unique_name + 'False')
            elif status == Status.USED:
                Tool.add_line(path,self.unique_name + 'True')
        self.status = status


    def get_url(self):
        if self.version == '~':
            url = Tool.get_params('downloads/store.conf','mod ' + self.name)[3]
            # 添加zip文件地址的后缀
            url += '/archive/main.zip'
            return url
        else:
            return None
    # 安装
    def install(self):
        if self.status == Status.INCLOUD:
            # 下载
            self.download_module()
            # 解压
            self.unzip()
            #设置状态为未使用
            self.status = Status.UNUSED
            # 使用
            self.use()
        elif self.status == Status.UNFIND:
            return RunStatus.FAILURE
        else:
            return RunStatus.DID

    # 卸载
    def uninstall(self):
        # 禁用
        self.unuse()
        # 删除各种文件
        self.delete_module()
        # 设置状态为云端
        self.status = Status.INCLOUD

    # 使用
    def use(self):
        if self.status == Status.UNUSED:
            # 往main文件里注入代码
            name = self.unique_name
            tag = self.get_tag()
            code = \
f'''# {name}>
from .insmodes.{name}.route import bp as {name}_route
app.include_router(
    {name}_route,
    prefix=url_prefix + '/{name}',
    tags=['{tag}'],)
# <{name}
'''
            # 在文件中插入代码
            with open("app/main.py",'r') as r:
                lines = r.readlines()
            for i in range(len(lines)):
                if lines[i] == '# for modules>\n':
                    lines[i+1] = '\n' + code
                    break
            with open("app/main.py",'w') as w:
                w.write(''.join(lines))
            # 设置状态为已使用
            self.status = Status.USED

    # 禁用
    def unuse(self):
        if self.status == Status.USED:
            name = self.unique_name
            # 从main中删除代码
            with open("app/main.py",'r') as r:
                lines = r.readlines()
            for i in range(len(lines)):
                if lines[i] == f'# {name}>\n':
                    head = i
                    continue
                elif lines[i] == f'# <{name}\n':
                    foot = i
                    break
            del lines[head:foot+1]
            with open("app/main.py",'w') as w:
                w.write(''.join(lines))
        
    # 获取api的标签
    def get_tag(self):
        if self.tag == '':
            self.tag = Tool.get_params(self.get_mod_path(False)+'/config.conf','api_tag')[1]
        return self.tag

    def unzip(self):
        Tool.unzip(self.get_zip_path(),self.get_mod_path(True),self.unique_name)

    # 删除压缩文件和文件夹
    def delete_module(self):
        os.remove(self.get_zip_path())
        shutil.rmtree(self.get_mod_path(False))

    # 下载zip,下载完后将以唯一名称进行保存在downloads中
    def download_module(self):
        Tool.download_file(self.url,self.get_zip_path())

    # 获取压缩包地址
    def get_zip_path(self):
        return 'downloads/'+ self.unique_name +'.zip'

    # 获取安装后的文件夹位置
    def get_mod_path(self,isFather:bool):
        if isFather:
            return 'app/insmodes/'
        return 'app/insmodes/' + self.unique_name

    

class Tool:
    # 获取文件内的参数
    @staticmethod
    def get_params(path: str,posi: str):
        with open(path,'r') as r:
            lines = r.readlines()
        for line in lines:
            # 历遍所有行,
            if line[:len(posi)] == posi:
                return line.split(' ')
        return None

    # 设置文件内的参数
    @staticmethod
    def set_params(path: str,posi:str,line_data:list):
        line_str = ' '.join(line_data) + ' \n'
        with open(path,'r') as r:
            lines = r.readlines()
        for i in range(len(lines)):
            # 历遍所有行,
            if lines[i][:len(posi)] == posi:
                lines[i] = line_str
                break
        with open(path,'w') as w:
            w.write(''.join(lines))

    # 删除某行
    @staticmethod
    def del_line(path: str,posi: str):
        with open(path,'r') as r:
            lines = r.readlines()
        for i in range(len(lines)):
            # 历遍所有行,
            if lines[i][:len(posi)] == posi:
                lines[i] = ''
                break
        with open(path,'w') as w:
            w.write(''.join(lines))

    # 增加一行
    @staticmethod
    def add_line(path: str,line_data:list):
        line_data.append('')
        with open(path,'a')as f:
            f.write(''.join(line_data))

    # 解压zip,重命名
    @staticmethod
    def unzip(oldpath: str, newpath: str,newname: str):
        zipFile = zipfile.ZipFile(oldpath,'r')
        for file in zipFile.namelist():
            zipFile.extract(file,newpath)
        namelist = zipFile.namelist()
        print(namelist)
        zipFile.close()
        # 重命名
        os.rename(newpath+'/'+namelist[0],newpath+'/'+newname)
    
    # 下载文件
    @staticmethod
    def download_file(url:str,path: str,func=None):
        res = requests.get(url,stream=True)
        total_size = int(res.headers.get('content-length'))
        with open(path, 'wb') as dl:
            i = 0
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    dl.write(chunk)
                # 如果函数存在则给其百分比
                if func != None:
                    func(i/total_size)
                    i+=1