with import <nixpkgs> {};

let

  python-requirements = ps: with ps; let

    sphinx-autodoc-typehints = with ps; buildPythonPackage rec {
      pname = "sphinx-autodoc-typehints";
      version = "1.2.5";
      propagatedBuildInputs = [ setuptools_scm sphinx ];
      src = fetchPypi {
        inherit pname version;
        sha256 = "141azsvvnjrg5sbfkv7ixwd3l2fn8vj14hbdbii6886iwgs8pcyk";
      };
      doCheck = false;
    };

    treelib = with ps; buildPythonPackage rec {
      pname = "treelib";
      version = "1.3.5";
      src = fetchPypi {
        inherit pname version;
        sha256 = "0rxrmriiqy7k29h16400wyyrqzxg9v2jsxla8m5735aqs5nfnvhp";
      };
      doCheck = false;
    };

  in [
    ply
    alabaster
    Babel
    click
    docutils
    flask
    flask-api
    imagesize
    itsdangerous
    jinja2
    markupsafe
    pudb
    py
    pycrypto
    pygments
    pytest
    pytz
    requests
    six
    snowballstemmer
    sphinx
    #sphinx-autodoc-typehints
    treelib
    urwid
    werkzeug
    colorama
  ];

in buildEnv {
  name = "labchain-env";
  paths = [
    (python3.withPackages (ps: python-requirements ps))
  ];
}
