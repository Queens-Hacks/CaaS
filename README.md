CaaS
====

Compilation as a Service. Instead of having to install node.js to compile LESS
files, or Ruby to compile SASS files, now you can just send those files to the
cloud and have it compile them for you!

Using the service
=================

CLI One-liner
-------------
    tar -cz folder | curl -sfF source=@- http://less.precomp.ca | tar zx

This will take the contents of `folder`, compress them, send them to the
LESS CaaS, then output the resulting compiled code.

The response will be the compiled css files alongside the LESS files.

Using the client
----------------

The client will automatically watch a directory and when anything changes,
use the CaaS to compile the changes, and write out the result.

TODO: CONFIG

Responses
=========
On every request the client will recieve a string representing the bytes of a
compressed file.

Inside the compressed file will be:
- A folder named `__precomp__`. This file contains a log of any messages the
  compilation process produced and other data. Useful for debugging.
- Compiled files. The results of the compilation will be in the root of the
  compressed file so when extracted, they go in the specified directory.
- If the compilation fails, the only file in the compressed archive will be
  the `__precomp__` folder.

The status code of the response is the same as usual, except for:
- 400 - This usually means the complation failed, see the log for more details.
- 200 - The compilation suceeded. The compiled files will be in the compressed file.
