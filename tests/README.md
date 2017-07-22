PreRequisites
===

1. cd to the cloned `reynolds` repo directory. (github:dmsurti/reynolds)

2. Now install the reynolds package in blender python:

   ```
   <path-to-blender-python> setup.py install
   ```                         

   Check your blender installation or blender docs for location it's python
   executable.

   For eg: on Mac, the blender python is:

   `/Applications/blender/blender.app/Contents/Resources/2.78/python/bin/python3.5m`


3. cd to the cloned `reynolds-blender` repo directory.

4. Install `pip` in the blender python:

   ```
   <path-to-blender-python> get-pip.py
   ```                         

   A copy of `get-pip.py` ships with this repo.

5. Install the dependencies using pip:

   ```
   <path-to-blender-pip> install -r requirements.txt
   ```
   
6. Copy the addon package to your blender installation:

   ```
   cp -R reynolds_blender ~/Library/Application\ Support/Blender/2.78/scripts/addons
   ```

Now you are ready to run the tests.

How to run the tests locally
===

1. cd to your cloned repo dir.

2. Copy the addon package again to your blender installation (if you have
   updated the addon source code). for eg, on a Mac:

   ```
   cp -R reynolds_blender ~/Library/Application\ Support/Blender/2.78/scripts/addons
   ```

3. Run the tests: `python tests/run_tests.py`.


Tests on Travis
---

The travis configuration installs blender, installs reynolds in blender with
other dependencies, copies the addon package and runs tests.
 