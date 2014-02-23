CaaS
====

Compilation as a Service. Instead of having to install node.js to compile LESS
files, or Ruby to compile SASS files, now you can just send those files to the
cloud and have it compile them for you!

Using the service
=================

CLI One-liner
-------------
    tar -cz folder | curl -sfF data=@- http://precomp.ca/sass | tar zxf - -C output_folder/

This will take the contents of `folder`, compress them, send them to the
LESS CaaS, then output the resulting compiled code to `output_folder`.

The response will be the compiled css files alongside the SASS files.

Using the client
----------------
The client will automatically watch a directory and when anything changes,
use the CaaS to compile the changes, and write out the result.

Config
------
The client is configured using YAML.

Example config:

```yaml
make_css:
  type: "less"
  input: "project/less"
  output: "project/css"
  interval: 1
  extras:
    targets: ["main.less", "styles.less"]
    logging: off

compile_haml:
  type: "haml"
  input: "project/haml"
  output: "project/html"
  interval: 1

compile_c:
  type: "gccmake"
  input: "helloworld" # Has a makefile and a hello.c file
  output: "helloworld/bin"
  interval: 5
  extras:
    targets: ['hello.out']
```

Things to keep in mind:
- Indentation is important. Use tabs or spaces to indent, but not both.
- `make_css`, `compile_haml`, and `compile_c` are the names of the watch jobs.
- `type` is the type of compilation to perform.
- The `input` parameter can be a file or a directory.
- The `output` parameter is _always_ treated as a folder.
  If you only want to output a single file, use the parent directory instead of the filename.
- `interval` is how long to wait (in seconds) between checking the filesystem for changes.
- C programs must have a makefile in the project directory

Key/value pairs under the `extras` parameter are all optional and differ based on the type of compilation being done.
- `logging` - Setting this to `off` will disable the generation of the `__precomp__` directory in the output
- Type-specific `targets` overrides:
  - SAAS and SCSS will by default compile everything in the directory.
    Use `targets` to specify which files to compile
  - LESS will by default attempt to compile `styles.less`
    Use `targets` to specify other LESS files.
  - C compilations will parse the makefile to guess which files to return after compilation.
    Use `targets` to specify which files to return after compilation.


Responses
=========
On every request the client will recieve a string representing the bytes of a
compressed file.

Inside the compressed file will be:
- Compiled files. The results of the compilation will be in the root of the
  compressed file so when extracted, they go in the specified directory.
- Unless logging has been turned off with the `logging` extra (see above),
  a folder named `__precomp__` will be generated. This folder contains a log
  of any messages the compilation process produced and other data.
  Useful for debugging.

The status code of the response is the same as usual, except for:
- 400 - This usually means the complation failed, see the log and `warning`
  HTTP header for more details.
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
