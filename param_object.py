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
##Self-Imports
EXP_CLIENT = experiment_session.EXP_CLIENT
EXP_DB     = EXP_CLIENT['experiment']

class ParamsObject(object):
  __metaclass__ = abc.ABCMeta
  _RESERVED_PARAM_NAMES_ = ['name', 'usertag']
  def __init__(self, usertag=None, **params):
    """
      usertag: a user specified tag to name the object
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
    self._dbColl = EXP_DB[self.name]
    #Check consistency
    self.check_params_consistency() 

  @property
  def params(self):
    """
    If new parameters are added, they are set to 
    the default value
    """
    params = copy.deepcopy(self._params)
    params['name'] = self.name
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
    defParams = self.params
    cursor    = self.dbColl.find()
    if cursor.count() == 0:
      return
    doc = cursor.next()
    #keys in the database
    dbKeys = set(doc.keys())
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
               format(self.name, self.params[k], k))
        ip = raw_input('Proceed (Y/N):')
        assert ip == 'Y' or ip == 'N', 'Invalid Input, Enter Y/N'
        if ip == 'Y':
          docs = self.dbColl.find()
          for d in docs:
            newd = copy.deepcopy(d)
            newd.update({k: self.params[k]})
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
        ip = raw_input('Proceed (Y/N):')
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
 
  def find_by_id(self, _id):
    """
    _id: the id by which the entry is to be found
    """
    if type(_id) is str:
      _id = bson.objectid.ObjectId(_id)
    assert type(_id) is bson.objectid.ObjectId  
    return self.dbColl.find({'_id': _id})

  def delete_by_id(self, _id):
    cur = self.find_by_id(_id)
    for dat in cur:
      print ('Deleting\n {0}'.format(dat))
      ip = raw_input('Proceed .. (Y/N)')
      assert ip in ['Y', 'N']
      if ip == 'Y':
        self.dbColl.delete_one(dat)
        print ('Deleted')
      else:
        print ('Not Deleted') 

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
    cursor = self.dbColl.find(self.params)
    if cursor.count() == 0:
      self.dbColl.insert_one(self.params)
      cursor = self.dbColl.find(self.params)
    assert cursor.count() == 1, 'Duplicates found'
    hashName = str(cursor.next()['_id'])
    return hashName


