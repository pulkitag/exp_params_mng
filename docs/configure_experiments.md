# Setting up Experiments

The typical use case of the package is to document and run experiments with different set of parameters. 
I will describe typical usage with help of an example that is typical in training deep networks, but 
the same paradigm can be easily extended to different use cases. 

## Simple Experiments

Suppose our experiment only depends on one set of parameters say ```NetParams```. The following piece of code would suffice

```python
from exp_params_mng import params_object

''' We create the base class from which all other parameter classes in the
project will inherit from. The projectName property creates a collection in the database
by the name returned by projectName. 
class MyExampleObject(params_object.ParamsObject):
  @property
  def projectName(self):
     return 'example'
  
 
class NetParamsObject(params_object.ParamsObject):  
    
  def default_params(self):
    """ define the default parameters from which to 
    dParams = {}
    dParams['netName'] = 'alexnet'
    dParams['learningRate'] = 0.01
    return dParams
    
    
class ExperimentObject(params_
```

Suppose our experiment depends on three different parameter sets, params_A, params_B and params_C. 
