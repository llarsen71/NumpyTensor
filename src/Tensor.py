
def IndexPool(name=None,size=None, idx_type=None, desc=None):
  """
  name     - Name of the new index. If None is passed in, a new index name is
             created.
  size     - The size of the index. This is only optional if the name is
             already created.
  idx_type - Type of the index. This should be either UPPER_INDEX or
             LOWER_INDEX. Default is LOWER_INDEX.
  desc     - Index description. This is a string to help indicate what the
             index represents.
  """
  return _Index.index_pool(name,size,idx_type,desc)

class _Index:

  LOWER_INDEX = "LOWER"
  UPPER_INDEX = "UPPER"

  __default_name__ = "a"

  __indices__ = {}

  def __init__(self,name,size,idx_type=None,desc=None):
    # Add an index namespace so that you can have indices with the same name
    # with different attributes?
    if idx_type is None or type not in (LOWER_INDEX,UPPER_INDEX):
      if name[0].isupper():
        idx_type = _Index.UPPER_INDEX
      else:
        idx_type = _Index.LOWER_INDEX
    self.name = name
    self.size = size
    self.type = idx_type

  @staticmethod
  def index_pool(name=None, size=None, idx_type=None, desc=None):
    """
    name     - Name of the new index. If None is passed in, a new index name is
               created.
    size     - The size of the index. This is only optional if the name is
               already created.
    idx_type - Type of the index. This should be either UPPER_INDEX or
               LOWER_INDEX. Default is LOWER_INDEX.
    desc     - Index description. This is a string to help indicate what the
               index represents.
    """
    if name is None and size is None:
      #TODO: decide what kind of exception to raise.
      raise Exception("Name and size cannot both be None")
    if name is None:
      # Get an unused index name.
      while _Index.__default_name__ in _Index.__indices__:
        lastchr = _Index.__default_name__[-1]
        if ord(lastchr) >= ord('z'):
          _Index.__default_name__ = _Index.__default_name__ + 'a'
          continue
        nextchr = chr(ord(lastchr)+1)
        _Index.__default_name__ = _Index.__default_name__[0:-1] + nextchr
      name = _Index.__default_name__
    if name in _Index.__indices__:
      index = _Index.__indices__[name]
      if size is not None and index.size != size:
        # TODO: Decide the type of exception
        raise Exception("Index sizes don't match")
      return index
    if size is None:
      #TODO: decide what kind of exception to raise.
      raise Exception("The index size must be passed in if the index is new")
    # Store the newly created index.
    index = _Index(name,size,idx_type,desc)
    _Index.__indices__[name] = index
    return index

  def in_list(self,indexes):
    for item in indexes:
      if self.is_match(item): return True
    return False

  def is_match(self,other):
    if self == other: return True
    if self.name.lower() == other.name.lower():
      return True
    return False

class Tensor:

  def __init__(self,*indexes, **kwargs):
    """
    Create a Tensor. The size of the Tensor is either determined by the indexes
    that are passed in, or by an array that is passed in.

    index1, index2, ... - (optional) The indexes that define the array. If an
        array is passed in, the index sizes must match the array dimension.
    array - (keyword,optional) An array object that this Tensor wraps.

    Note that indexes and array can't both be blank. If an array is passed in
        without indexes, default indexes are created.
    """
    array_size = 0
    # Get the indexes and determine the dimension of the array.
    if 'array' in kwargs:
      # Check that the array matches the size indicated by the indexes.
      # If no indexes are created, make new ones.
      self.array = kwargs['array']
      array_size = len(self.array.shape)
      shape = self.array.shape
      if indexes is None or len(indexes) == 0:
        # Create new indexes.
        indexes = []
        for size in shape:
          indexes.append(IndexPool(size=shape))
      elif len(indexes) != len(shape):
        # TODO: figure out what kind of exception to send
        raise Exception("Indexes and array don't match")
      else:
        indexes2 = []
        for i,index in enumerate(indexes):
          if isinstance(index,_Index):
            if index.size() != shape[i]:
              raise Exception("The dimension of the index and the array don't agree")
            indexes2.append(index)
          else:
            indexes2.append(IndexPool(name,shape[i]))
        indexes = indexes2
    else:
      import numpy
      shape = []
      for index in indexes:
        if not isinstance(index,_Index):
          raise Exception("Index objects must be pased in if array is not passed in")
        shape.append(index.size)
      self.array = numpy.zeros(shape)
    dim = len(shape)
    self.indexes = [None]*dim
    for i,index in enumerate(indexes):
      self.set_index(index,i)

  def set_index(self,index,dim):
    if isinstance(index,_Index):
      self.indexes[dim] = index

  def __getattr__(self,name):
    """
    Make this a decorator for the array member. Forward all unhandled calls to
    the array.
    """
    return getattr(self.array,name)

  def __common_indexes__(self,other):
    indexes = []
    for index in other.indexes:
      if index.in_list(self.indexes):
        indexes.append(index)
    return indexes

  def __mul__(self,other):
    if not isinstance(other,Tensor):
      return self.array*other
    # Get indexes that are the same
    indexes = self.__common_indexes__(other)

    # Set the dimensions so that they align for multiplication
    # Multiply, then sum any contracted dimensions
    pass
