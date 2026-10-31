"""Replace generated static assets only after writing and validating a full file."""
import os
from pathlib import Path
import stat
import tempfile
from PIL import Image


def _replace(destination, writer):
    destination = Path(destination)
    destination.parent.mkdir(parents=True,exist_ok=True)
    fd,name = tempfile.mkstemp(prefix='.'+destination.stem+'-',suffix=destination.suffix,dir=destination.parent)
    os.close(fd)
    temporary = Path(name)
    try:
        writer(temporary)
        mode = stat.S_IMODE(destination.stat().st_mode) if destination.exists() else 0o644
        temporary.chmod(mode)
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def write_text(destination,text):
    _replace(destination,lambda path:path.write_text(text,encoding='utf-8'))


def save_task_image(task,destination):
    def write(path):
        task.save_image(str(path))
        with Image.open(path) as picture:
            picture.verify()
    _replace(destination,write)
