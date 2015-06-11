"""
Copyright 2015 Juergen Edelbluth

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


import unittest
import os
import sys


if __name__ == '__main__':
    file = os.path.abspath(__file__)
    path = os.path.dirname(file)
    src = os.path.abspath(os.path.join(path, '../src/'))
    assert os.path.exists(src), 'Source dir does not exist'
    assert os.path.isdir(src), 'Source dir is invalid'
    sys.path.insert(0, src)
    tests = unittest.TestLoader().discover('.', pattern='test_*.py')
    unittest.TextTestRunner(verbosity=2).run(tests)
