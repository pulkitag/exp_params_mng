# Setting up Experiments

The typical use case of the package is to document and run experiments with different set of parameters. 
I will describe typical usage with help of an example that is typical in training deep networks, but 
the same paradigm can be easily extended to different use cases. 

## Simple Experiments

We want to run multiple experiments with different values of ```NetParams```. Essentially what we want is 
a path name for each set of parameters, so that we can store the experiment related stuff in paths that are
related to the parameters. We would do this in the following way: 
```python
from exp_params_mng import params_object

""" 
We create the base class from which all other parameter classes in the
project will inherit from. The projectName property creates a database in the 
server by the name projectName. All other parameter objects create collections
in this database. 
""" 
class MyExampleObject(params_object.ParamsObject):
  @property
  def projectName(self):
     return 'example'
  
 
class NetParams(MyExampleObject):  
  def default_params(self):
    """ 
    Define the default set of parameters 
    """
    dParams = {}
    dParams['netName'] = 'alexnet'
    dParams['learningRate'] = 0.01
    return dParams
    
    
class ExperimentParams(MyExampleObject):
  def __init__(self, netObj):
    #netObj: object of type NetParams
    self._netObj = netObj

  def default_params(self):
    dParams = {}
    dParams['netHash'] = self._netObj.hash_name()
    return dParams
    
  def get_paths(self):
    paths = {}
    paths['exp'] = self.hash_name()
```


