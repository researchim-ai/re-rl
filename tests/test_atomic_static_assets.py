"""Readers retain the previous complete asset until replacement succeeds."""
from PIL import Image, UnidentifiedImageError
import pytest
from scripts.atomic_files import save_task_image,write_text


def test_image_is_replaced_only_after_complete_write(tmp_path):
    path = tmp_path/'preview.png'
    Image.new('RGB',(3,4),'red').save(path)
    class Task:
        def save_image(self,temporary):
            with open(temporary,'wb') as output:
                output.write(b'partial')
            with Image.open(path) as previous:
                assert previous.size == (3,4)
                previous.verify()
            Image.new('RGB',(7,8),'blue').save(temporary)
    save_task_image(Task(),path)
    with Image.open(path) as picture: assert picture.size == (7,8)
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize('raises',[True,False])
def test_bad_generation_keeps_old_image_and_cleans_temporary(tmp_path,raises):
    path = tmp_path/'preview.png'
    Image.new('RGB',(3,4),'red').save(path)
    previous = path.read_bytes()
    class BadTask:
        def save_image(self,temporary):
            with open(temporary,'wb') as output: output.write(b'partial')
            if raises: raise RuntimeError('generation_failed')
    with pytest.raises((RuntimeError,UnidentifiedImageError)):
        save_task_image(BadTask(),path)
    assert path.read_bytes() == previous
    assert list(tmp_path.iterdir()) == [path]


def test_text_replacement_preserves_mode_and_existing_open_reader(tmp_path):
    path = tmp_path/'data.js'
    path.write_text('old')
    path.chmod(0o640)
    with path.open() as reader:
        write_text(path,'new')
        assert reader.read() == 'old'
    assert path.read_text() == 'new'
    assert path.stat().st_mode & 0o777 == 0o640
    assert list(tmp_path.iterdir()) == [path]
