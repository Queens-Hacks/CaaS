CaaS
====

Compilation as a Service. Instead of having to install node.js to compile LESS
files, or Ruby to compile SASS files, now you can just send those files to the
cloud and have it compile them for you!

Using the service
=================

CLI One-liner
-------------
    zip -r - folder | curl -X POST --data-binary @- http://less.precomp.ca --fail

This will take the contents of `folder`, compress them, and send them to the
LESS CaaS.

The response should be a zip file with the compiled css files.

Using the client
----------------

The client will automatically watch a directory and when anything changes,
use the CaaS to compile the changes, and unzip the result.

TODO: CONFIG

Responses
=========
On every request the client will recieve a string representing the bytes of a
zipfile.

Inside the zipfile will be 2 items:
- A folder named `data`. This is where the results of the compilation will be.
  Will be empty on errors.
- A file named `log.txt`. This file contains a log of any messages the
  compilation process produced. Useful for debugging.

The status code of the response is the same as usual, except for:
- 400 - This usually means the complation failed, see the log for more details.
- 200 - The compilation suceeded. The compiled files will be in the zip file.
