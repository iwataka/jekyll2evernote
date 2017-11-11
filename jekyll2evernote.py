#!/usr/bin/env python

import os
import string
import evernote.edam.type.ttypes  as Types
import evernote.edam.error.ttypes as ErrorTypes

from geeknote.geeknote import *
from geeknote.editor import Editor

def main(argv):
    if len(argv) != 3:
        print "Usage: ./jekyll2evernote [/path/to/_posts] [notebook]"
        return

    post_dir = argv[1]
    notebook_title = argv[2]

    geeknote = GeekNote()
    authToken = geeknote.authToken
    noteStore = geeknote.getNoteStore()

    notebook = None
    for nb in noteStore.listNotebooks(authToken):
        if nb.name == notebook_title:
            notebook = nb

    if notebook == None:
        nb = Types.Notebook()
        nb.name = notebook_title
        notebook = noteStore.createNotebook(authToken, nb)

    create_notes(post_dir, notebook, noteStore, authToken)

def create_notes(dir, notebook, noteStore, authToken):
    for fname in os.listdir(dir):
        fullpath = os.path.join(dir, fname)
        if os.path.isfile(fullpath):
            create_note(dir, fname, notebook, noteStore, authToken)
        elif os.path.isdir(fullpath):
            create_notes(fullpath, notebook, noteStore, authToken)

def create_note(dir, fname, notebook, noteStore, authToken):
        date = re.search("([0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2})", fname).group(1)
        basename, ext = os.path.splitext(fname)
        title = to_title(basename[(len(date) + 1):])

        fullpath = os.path.join(os.getcwd(), dir, fname)
        with open(fullpath) as f:
            content = f.read()

        note = Types.Note()
        note.title = title
        note.created = None
        note.content = to_ENML(content)
        note.notebookGuid = notebook.guid

        try:
            noteStore.createNote(authToken, note)
        except ErrorTypes.EDAMUserException as e:
            print "Unable to create note: {0}".format(note.title)

def to_title(basename):
    segs = string.split(basename, "-")
    segs = [x[0].upper() + x[1:] for x in segs]
    return string.join(segs, " ")

def to_ENML(content):
    return Editor.textToENML(content, False, "markdown")

if __name__ == "__main__":
    main(sys.argv)
