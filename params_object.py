import abc
import copy
import numpy as np
import datetime
import pymongo
import pickle
import os
from os import path as osp
import bson
##3rd party
from pyhelper_fns import path_utils
#Self imports
from exp_params_mng import db_config
try:
  EXP_CLIENT = db_config.EXP_CLIENT
  #print ('IMPORTING FROM db_config')
except:
  EXP_CLIENT = pymongo.MongoClient('localhost:27900')
  #print ('IMPORTING FROM DUNNO WHERE')

class ParamsObject(object):
  __metaclass__ = abc.ABCMeta
  _RESERVED_PARAM_NAMES_ = ['name', 'usertag']
  def __init__(self, usertag=None, userConfirm=True, **params):
    """
      usertag: a user specified tag to name the object
      userConfirm: whether a user needs to confirm some consistency check operations 
      params : a set of parameters defining the abstract object
    """
    self._params = self.default_params()
    #Assert that user specified params is a subset
    #of default parameters 
    userKeys    = params.keys()
    defaultKeys = self._params.keys()
    assert set(userKeys).issubset(set(defaultKeys))
    #Update the parameters by user parameters 
    self._params.update(params)
    assert len(set(self._RESERVED_PARAM_NAMES_).intersection(set(defaultKeys))) == 0
    self._params['usertag'] = usertag
    #Initial the database collection
    self._expDb  = EXP_CLIENT[self.projectName]
    self._dbColl = self._expDb[self.name]
    #Check consistency
    self.userConfirm = userConfirm
    self.check_params_consistency() 

  @property
  def dbColl(self):
    """
      the collection storing the parameters on the server
    """
    return self._dbColl

  @property
  def name(self):
    """
    name of the object
    the database file name depends on this
    """
    return type(self).__name__

  @abc.abstractproperty
  def projectName(self):
    """
    Returns the name of the project
    """

  @abc.abstractproperty
  def ignoreHashKeys(self):
    """
    Returns:
      list of keys that should be ignored when
      generating or loading the hash
    """ 
 
  @abc.abstractmethod
  def default_params(self):
    """
    Returns:
      a dict containing default params
    """

  @property
  def params(self):
    """
    If new parameters are added, they are set to 
    the default value
    """
    params = copy.deepcopy(self._params)
    params['name'] = self.name
    return params 

  @property
  def hashableParams(self):
    """
    Remove keys in params that have been specified in 
    """
    params = copy.deepcopy(self.params)
    for k in self.ignoreHashKeys:
      if k in params:
        del params[k]
    return params

  @property
  def defaultHashableParams(self):
    """
    default parameter values after the removing the
    keys specifed in ignoreHashKeys
    """
    params = copy.deepcopy(self.default_params())
    params['name'] = self.name
    params['usertag'] = self._params['usertag']
    for k in self.ignoreHashKeys:
      if k in params:
        del params[k]
    return params

  def params_no_reserved(self):
    """Returns the params after stripping the reserved names"""
    params = self.params
    for k in self._RESERVED_PARAM_NAMES_:
      del params[k] 
    return params

  def check_params_consistency(self):
    """
    mantain consistency of field names beween DB and default params
    it is possible a user can add a new param name
    we mantain the fact all entries have the same set
    of parameters for all entries
    """
    print ('Checking consistency')
    defParams = self.defaultHashableParams
    cursor    = self.dbColl.find()
    if cursor.count() == 0:
      return
    doc = cursor.next()
    #keys in the database
    dbKeys = set([str(k) for k in doc.keys()])
    #keys in the parameters
    prKeys = set(defParams.keys())
    prKeys.add('_id')
    isOld  =  dbKeys.issubset(prKeys) and prKeys.issubset(dbKeys) 
    if isOld:
      return
    if dbKeys.issubset(prKeys):
      print ('#### New default parameters found ... ####')
      #If new parameters are added
      newKeys = prKeys.difference(dbKeys)
      for k in newKeys:
        print ('Setting all entries in {0} DB with value {1} for key {2}'.\
               format(self.name, defParams[k], k))
        if self.userConfirm:
          try:
            #python2
            ip = raw_input('Proceed (Y/N):')
          except:
            #python3
            ip = input('Proceed (Y/N):')
        else: 
          ip = 'Y'
        assert ip == 'Y' or ip == 'N', 'Invalid Input, Enter Y/N'
        if ip == 'Y':
          docs = self.dbColl.find()
          for d in docs:
            newd = copy.deepcopy(d)
            newd.update({k: defParams[k]})
            self.dbColl.update(d, newd) 
          print ('Updated')
        else:
          print ('Not proceeding with update')
    else:
      print ('#### Some default parameters are deleted ... ####')
      newKeys = dbKeys.difference(prKeys)
      for k in newKeys:
        print ('For all entries in {0} DB, deleting key {1}'.\
               format(self.name, k))
        if self.userConfirm:
          try:
            #python2
            ip = raw_input('Proceed (Y/N):')
          except:
            #python3
            ip = input('Proceed (Y/N):')
        else: 
          ip = 'Y'
        assert ip == 'Y' or ip == 'N', 'Invalid Input, Enter Y/N'
        if ip == 'Y':
          docs = self.dbColl.find()
          for d in docs:
            newd = copy.deepcopy(d)
            del newd[k]
            self.dbColl.update(d, newd) 
          print ('Updated')
        else:
          print ('Not proceeding with update')

 
  def find_by_id(self, _id):
    """
    _id: the id by which the entry is to be found
    """
    if type(_id) is str:
      _id = bson.objectid.ObjectId(_id)
    assert type(_id) is bson.objectid.ObjectId  
    return self.dbColl.find({'_id': _id})

  def from_id(self, _id):
    """ 
    Return the entry by the _id
    """
    cur = self.find_by_id(_id)
    assert cur.count() == 1
    return cur.next()

  def delete_by_id(self, _id, userConfirm=True):
    cur = self.find_by_id(_id)
    for dat in cur:
      if userConfirm:
        print ('Deleting\n {0}'.format(dat))
        try:
          #python2
          ip = raw_input('Proceed .. (Y/N)')
        except:
          ip = input('Proceed .. (Y/N)')
        assert ip in ['Y', 'N']
        if ip == 'Y':
          self.dbColl.delete_one(dat)
          print ('Deleted')
        else:
          print ('Not Deleted') 
      else:
        self.dbColl.delete_one(dat)

  def get_all_ids(self):
    """
    Returns the ids of all the entries
    """
    cur = self.dbColl.find()
    ids = []
    for dat in cur:
      ids.append(str(dat['_id']))
    return ids
 
  def hash_name(self):
    cursor = self.dbColl.find(self.hashableParams)
    if cursor.count() == 0:
      self.dbColl.insert_one(self.hashableParams)
      cursor = self.dbColl.find(self.hashableParams)
    assert cursor.count() == 1, 'Duplicates found'
    hashName = str(cursor.next()['_id'])
    return hashName
