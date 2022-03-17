#!/usr/bin/env python3
# Python 3

# import os, pathlib
#from importlib.resources import path
from collections import defaultdict
from pathlib import *
from helpers import *


class FileManagement():
  def __init__(
      self, project_file: str, shotfolder_structure: str, *args, **kwargs
  ):
    self.project = readFile(project_file)
    self.project['project_path'] = Path(project['project_path'])
    self.project['comps_path'] = project['project_path'] / project['comps_path']
    self.project['footage_path'
                ] = project['project_path'] / project['footage_path']

    self.shotfolder_structure = readFile(shotfolder_structure)


def listShotsFolders(path, filetypes=[".mov"], exclude=[".converted"]):
  """ looks at folders and finds if they have files inside, if they do it will
  be recorded """
  f = defaultdict(list)
  # Recursively look through the folders in the given path
  # and look for one of the given filetype
  for filetype in filetypes:
    for i in Path(path).rglob("*" + filetype):
      f[i.parent].append(i)  # Once found a file store it in a list

  for e in exclude:
    for i in Path(path).rglob(e):
      del f[i.parent]

  return removeRedudantPath(f)
  # -------------------------------------------------------------------------


def removeRedudantPath(dictionary):
  """ removes path from found files based on the dictionary key """
  for k, v in dictionary.items():
    if type(v) == list:
      new_v = []
      for i in v:
        new_v.append(str(i.relative_to(k)))
    dictionary[k] = new_v
  return dictionary


def findUniqueFolders(data):
  """This thing takes one of those crazy dictionaries with folders paths as
  keys and value and just compresses it down to just the name of the
  unique folders."""

  temp_lists = []
  unique_items = []
  common_items = []
  new_data = {}
  for k in data.keys():
    temp_lists.append(k.as_posix().split("/"))
  for temp_list in temp_lists:
    if temp_list != temp_lists[0]:
      for item in temp_list:
        if item in temp_lists[0] and item not in common_items:
          common_items.append(item)
  for temp_list in temp_lists:
    for item in temp_list:
      if item not in common_items:
        unique_items.append(item)

  # replace the keys with the unique items found
  for k, v in data.items():
    for u in unique_items:
      if u in str(k):
        print(u, k)
        new_data[u] = v

  return {"common": common_items, "unique": unique_items, 'data': new_data}


def findShotNumber(file):
  """ given a path with a 3 digit shot it will return just the number """
  shot_number = file.stem.split(" ")[1]
  try:
    if "-" in shot_number:
      shot_number = int(shot_number.split("-")[0].lstrip("0"))
    else:
      shot_number = int(shot_number.lstrip("0"))
  except ValueError:
    shot_number = 0
  return shot_number
  # -------------------------------------------------------------------------


def recursiveStructure(
    structure: dict, folder: Path(), project: dict, shot_number: int, sequence
):
  """ this calls a function to create folders recursively """
  # keys = [k for k in structure]
  for key, value in structure.items():
    log.debug(f"KEY: {key} - VALUE: {value}")
    if value is None:
      # This is an empty folder.
      makeStructure('folder', key, folder, project, shot_number, sequence)
    else:
      # If the key name contains "act" is a call to action
      if "act" in key:
        makeStructure(
            value['action'], value, folder, project, shot_number, sequence
        )
      else:
        # If it's not an action, it is a folder with more stuff to do in it
        new_folder = makeStructure(
            "folder", key, folder, project, shot_number, sequence
        )
        recursiveStructure(value, new_folder, project, shot_number, sequence)
  # -------------------------------------------------------------------------


def makeStructure(
    action: str, item, folder, project: dict, shot_number, sequence
):
  episode_number = f"{int(project['episode_number']):03d}"
  shot_number = f"{int(shot_number):03d}"
  if type(sequence) == int:
    sequence = f"{int(sequence):03d}"

  log.debug("makeStructure: received")
  log.debug(f"action {action}\nitem {item}")
  # check if the item is a dictionary, then extract name
  if type(item) == dict:
    try:
      name = item['name']
    except:
      name = ""
  else:
    name = item
  # get a complete name if it contains "variables"
  if "$" in name:
    name = parseName(name, project, shot_number, sequence)
  # The core of the function
  if action == "folder":
    item = Path.joinpath(folder, name)
    makeFolder(item)
    return item
  elif action == "file":
    item = Path.joinpath(folder, name)
    makeFile(item)
    return item
  elif action == "copy file":
    if item['from'] != None:
      new_item = Path.joinpath(folder, name)
      copyFile(new_item, item['from'])
    return new_item
  elif action == "copy folder":
    if item['from'] != None:
      copyFolder(folder, item['from'])
    return folder

  # -------------------------------------------------------------------------


def parseName(name: str, project_data: dict, shot_number, sequence):
  """Given a string containing:
        $project_name$
        $short_projects$
        $episode$
        $shot$
    It will replace those variables with the correct project information.

    Arguments:
        name {str} -- the string to parse
        project_data {dict} -- dictionary containing 'project_name', 'episode_number'
        shot_number {int} -- shot number

    Returns:
        str -- parsed name
    """
  short_project = project_data['short_project_name'].upper()
  episode_number = f"{int(project_data['episode_number']):03d}"
  if type(shot_number) == int:
    shot_number = f"{int(shot_number):03d}"
  if type(sequence) == int:
    sequence = f"{int(sequence):03d}"

  if "$project_name$" in name:
    name = name.replace("$project_name$", project_data['project_name'])
  if "$short_project$" in name:
    name = name.replace("$short_project$", short_project)
  if "$episode$" in name:
    name = name.replace("$episode$", episode_number)
  if "$shot$" in name:
    name = name.replace("$shot$", shot_number)
  if "$sequence$" in name:
    name = name.replace("$sequence$", sequence)
  return name


# ---------------------------------  EXECUTE  ---------------------------------

if __name__ == '__main__':
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

  log.debug("Hey I'm running as a file!")

  project = readFile("setup_project.yml")
  project['project_path'] = Path(project['project_path'])
  project['comps_path'] = project['project_path'] / project['comps_path']
  project['footage_path'] = project['project_path'] / project['footage_path']

  shotfolder_structure = readFile("setup_shotfolder.yml")

  for i in project['shot_number']:
    recursiveStructure(
        shotfolder_structure, project['comps_path'], project, i,
        project['sequence']
    )

  log.debug(shotfolder_structure)
