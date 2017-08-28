import sys
sys.stdin = open('/dev/tty')
from safely_exp.utils import auth_utils

import unittest

from exp_params_mng import params_object

class DummyObject(params_object.ParamsObject):
  @property
  def ignoreHashKeys(self):
    return ['d']
  
  @property
  def projectName(self):
    return 'haptics'

  def default_params(self):
    dParams = {}
    dParams['a'] = 0
    dParams['b'] = 'zz'
    dParams['c'] = 2
    dParams['d'] = 3.
    return dParams
  

#To test when a new default parameter is added
class DummyObject2(params_object.ParamsObject):
  @property
  def name(self):
    return 'DummyObject'

  @property
  def projectName(self):
    return 'haptics' 

  @property
  def ignoreHashKeys(self):
    return ['d']
  
  def default_params(self):
    dParams = {}
    dParams['a'] = 0
    dParams['b'] = 'zz'
    dParams['c'] = 2
    dParams['d'] = 3.
    dParams['e'] = 4
    return dParams


#Place a default parameter in ignoreHashKeys    
class DummyObject3(params_object.ParamsObject):
  @property
  def name(self):
    return 'DummyObject'
  
  @property
  def ignoreHashKeys(self):
    return ['d', 'c']
  
  @property
  def projectName(self):
    return 'haptics'

  def default_params(self):
    dParams = {}
    dParams['a'] = 0
    dParams['b'] = 'zz'
    dParams['c'] = 2
    dParams['d'] = 3.
    return dParams


class ExperimentObjectTests(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    obj = DummyObject(userConfirm=False)
    for i in obj.get_all_ids():
      obj.delete_by_id(i, userConfirm=False)
        
  def tearDown(cls):
    """
    Delete all entries made during testing
    """
    obj = DummyObject(userConfirm=False)
    for i in obj.get_all_ids():
      obj.delete_by_id(i, userConfirm=False)      
    
  def test_ignore_hash(self):
    #The key 'd' should be ignored
    obj1 = DummyObject(a=0, d='5')
    hashName1 = obj1.hash_name()
    obj2 = DummyObject(a=0, d='6')
    hashName2 = obj2.hash_name()
    self.assertEqual(hashName1, hashName2)
    self.assertEqual(len(obj2.get_all_ids()), 1)
    self.assertEqual(obj1.params['d'], '5')
    self.assertEqual(obj2.params['d'], '6')
    obj3 = DummyObject(a=1, d='6')
    hashName3 = obj3.hash_name()
    self.assertEqual(len(obj2.get_all_ids()), 2)
    self.assertNotEqual(hashName2, hashName3)
    
  def test_add_default_param(self):
    obj1 = DummyObject(a=2, userConfirm=False)
    hashName1 = obj1.hash_name()
    #Default value is used
    objDef      = DummyObject(userConfirm=False)
    hashNameDef = objDef.hash_name()
    #Create something with new defaults
    obj2 = DummyObject2(userConfirm=False)
    hashName2 = obj2.hash_name()
    #import IPython; IPython.embed()
    self.assertEqual(len(obj2.get_all_ids()), 2)
    self.assertEqual(obj2.params['e'], 4)
    for i in obj1.get_all_ids():
      obj1.delete_by_id(i, userConfirm=False)
    
  def test_add_default_param_value(self):
    """
    Tests that added default parameter gets
    added with the default value and not the user
    specified value
    """
    obj1 = DummyObject(a=2, userConfirm=False)
    hashName1 = obj1.hash_name()
    #Default value is used
    objDef      = DummyObject(userConfirm=False)
    hashNameDef = objDef.hash_name()
    #Create something with new defaults
    obj2 = DummyObject2(userConfirm=False, e=5)
    hashName2 = obj2.hash_name()
    #import IPython; IPython.embed()
    self.assertEqual(len(obj2.get_all_ids()), 3)
    #Get obj1 again
    obj  = DummyObject2(userConfirm=False)
    objParams1 = obj.from_id(hashName1)
    objParamsDef = obj.from_id(hashNameDef)
    self.assertEqual(objParams1['e'], 4)
    self.assertEqual(objParamsDef['e'], 4)
    self.assertEqual(obj2.params['e'], 5)
    for i in obj1.get_all_ids():
      obj1.delete_by_id(i, userConfirm=False)
  
  def test_default_to_ignore(self):
    """
    Test what happens when a default key
    is moved to ignoreHashKeys
    """
    obj1 = DummyObject(c=2, userConfirm=False)
    hashName1 = obj1.hash_name()
    obj2 = DummyObject(c=3, userConfirm=False)
    hashName1 = obj2.hash_name()
    #Object after putting c in ignoreHashKeys
    flag = 0
    try:
      objDef      = DummyObject3(userConfirm=False)
      hashNameDef = objDef.hash_name()
      #If this line is executed there is an error
      self.assertEqual(0,1)
    except params_object.CustomError:
      flag = 1
    self.assertEqual(flag,1)
    
      
if __name__ == '__main__':
  unittest.main()
