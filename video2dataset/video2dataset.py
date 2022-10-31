"""Create dataset from video links and metadata."""


from .reader import Reader
from .writer import FileWriter
from .downloader import handle_url


def video2dataset(
  src,
  dest="",
  output_format="webdataset",
  metadata_columns="",
):
  """
  create video dataset from video links

  src:
    str: path to table of data with video links and metdata
  dest:
    str: where to save dataset to
  output_format:
    str: webdataset, files
  metadata_columns:
    str: a comma separated list of metadata column names to look for in src
  """
  if isinstance(metadata_columns, str):
      metadata_columns = [metadata_columns] if metadata_columns != "" else []
  metadata_columns = list(metadata_columns) if isinstance(metadata_columns, tuple) else metadata_columns
  reader = Reader(src, metadata_columns)
  vids, ids, meta = reader.get_data()

  if output_format == "files":
    writer = FileWriter(dest)
  else:
    print("Not implemented yet.")
    return -1

  for i in range(len(vids)):
    vid = vids[i]
    vid_id = ids[i]
    vid_meta = {}
    for k in meta:
      vid_meta[k] = meta[k][i].as_py()

    load_vid, file, dst_name = handle_url(vid)
    with open(load_vid, "rb") as vid_file:
      vid_bytes = vid_file.read()
    video = vid_bytes

    writer.write(video, vid_id, vid_meta)

    if file is not None:  # for python files that need to be closed
      file.close()