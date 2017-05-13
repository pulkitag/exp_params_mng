from . import params_object

class DummyParams(params_object.ParamsObject):
  @property
  def projectName(self):
    return 'Dummy'

  @property
  def ignoreHashKeys(self):
    return []

  def default_params(self):
    params = {}
    params['a'] = 1
    params['b'] = 2
    return params
