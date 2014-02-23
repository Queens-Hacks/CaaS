CaaS
====

Compilation as a Service. Instead of having to install node.js to compile LESS
files, or Ruby to compile SASS files, now you can just send those files to the
cloud and have it compile them for you!

Using the service
=================

CLI One-liner
-------------
    tar -cz folder | curl -sfF data=@- http://less.precomp.ca | tar zx

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


Setting up the server
=====================

 1. [Create an application on github](https://github.com/settings/applications/new)
    * Pick anything for all the fields excep the last one
    * set `Authorization callback URL` to `http://localhost:5000/authorized`/
 2. Create a database at [MongoHQ](https://www.mongohq.com/home) or any online mongo as a service or run mongo locally.
 3. Create and activate a Python 3.3+ virtualenv. See [virtualenv.org](http://www.virtualenv.org/en/latest/).
 4. Install requirements with `$ pip install -r requirements-server.txt`.
 5. Configure the app. You can either create a `config.py` file, or export the variables to the environment. You must set these variables:

Variable            | Description
--------------------|------------
`SECRET_KEY`        | Must be something, but for local development it can be anything
`DEBUG`             | You'll probably want this to be `True` for local development
`GITHUB_CLIENT_ID`  | GitHub gives you this after registering your application on GitHub
`GITHUB_CLIENT_SECRET` | Same deal
`MONGO_URI`         | Whatever you got from MongoHQ or wherever.

After these steps, you should be able to just

```bash
(venv) $ python manage.py runserver
```

and play around at [localhost:5000](http://localhost:5000)
