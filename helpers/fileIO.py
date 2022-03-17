from pathlib import PureWindowsPath, Path, PurePath, PurePosixPath
import pickle
import yaml
import jsons
import shutil
import csv
import re

from yaml import load, dump

try:
  from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
  from yaml import Loader, Dumper

# Import rich & logging
import logging as log
from rich import print
from rich.logging import RichHandler

log.basicConfig(
    level="DEBUG",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)


def saveFile(file, data):
  """Helps save data to a multitude of files types.

    Supported file types are: ["json", "yaml", "yml, "dat" (as pickle), "pickle"]

    Keyword Arguments:
        file {Path} -- Name of the file (include ext) (default: {None})
        data -- Data you want to write to the file (default: {None})
    """
  try:
    if PureWindowsPath(file).suffix in [".json"]:
      write_data = jsons.dumps(data, indent=4)
      write_type = "w"
    elif PureWindowsPath(file).suffix in [".dat", ".pickle"]:
      write_data = pickle.dumps(data)
      write_type = "wb"
    elif PureWindowsPath(file).suffix in [".yaml", ".yml"]:
      write_data = yaml.dump(data)
      write_type = "w"

    with open(file, write_type) as stream:
      stream.write(write_data)
  except TypeError as e:
    log.error(f"TypeError: {e}")


def readFile(file):
  """A simple way to read different kind of files based on their extensions. It will convert the data back to Python usable.

    Supported file types are: ["json", "yaml", "yml, "dat" (as pickle), "pickle", "csv"]

    Keyword Arguments:
        file {Path} -- A file to read.

    Returns:
        Python data based on what is available on file.
    """
  try:
    if PureWindowsPath(file).suffix in [".json"]:
      with open(file, "r") as stream:
        file_data = jsons.loads(stream.read())
    elif PureWindowsPath(file).suffix in [".dat", ".pickle"]:
      with open(file, "rb") as stream:
        file_data = pickle.load(stream)
    elif PureWindowsPath(file).suffix in [".yaml", ".yml"]:
      with open(file, "r") as stream:
        file_data = yaml.load(stream, Loader=Loader)
    elif PureWindowsPath(file).suffix in [".csv"]:
      with open(file, newline='') as stream:
        file_data = parse_csv(stream)
    return file_data
  except Exception as e:
    log.error(e)


def makeFolder(path: Path()):
  # create the folder if it doesn't exist
  if not path.exists():
    path.mkdir(parents=True)
    log.info(f"MKDIR: {path}")
    return True
  else:
    log.warning(f"MKDIR: folder already exists.\n{path}")
    return False


def makeFile(path: Path()):
  # create the file if it doesn't exist
  if not path.exists():
    path.touch()
    log.info(f"MKFILE: {path}")
    return True
  else:
    log.warning(f"MKFILE: file already exists.\n{path}")
    return False


def copyFile(path: Path(), original_file: Path(), force: bool = False):
  # create the file if it doesn't exist
  if not path.exists() or force == True:
    shutil.copy2(original_file, path)
    log.info(f"CP FILE:\n\tfrom: {original_file}\n\tto: {path}")
    return True
  else:
    log.warning(f"CP FILE: file already exists.\n{path}")
    return False


def copyFolder(path: Path(), original_file: Path(), force: bool = False):
  # create the folder if it doesn't exist
  if not path.exists() or force == True:
    shutil.copytree(original_file, path)
    log.info(f"CP DIR:\n\tfrom: {original_file}\n\tto: {path}")
    return True
  else:
    log.warning(f"CP DIR: directory already exists.\n{path}")
    return False


def parse_csv(stream):
  reader = csv.DictReader(stream)

  # Set new dictionary
  proj_dict = {}
  episode_dict={}
  shot_list=[]

  for row in reader:
      for k, v in row.items():
          if k.lower() == 'shot':
              results = re.match(r"(\w{3})_(\d{3})_(\d{3})_(\d{3})", v)
              shot_list.append(results.group(4))
              episode_dict[results.group(3)] = shot_list
              proj_dict[results.group(2)] = episode_dict
              short_project_name = results.group(1)
              
  return proj_dict