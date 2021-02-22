Scripts to download newspaper data for Chronicling America from Library of Congress

download_txt.py can be used to download text files directly, but is very slow

Better is download the ocr tar files, which contain both .txt and .xml, and then only extract the .txt
To do this, run make_ocr_download_script.py, which will produce a bash script to download files using wget.
--first and --last can be used to break this up into pieces
Then run make_ocr_untar_script.py, which will create a bash script to untar the .txt files from all the downloaded files
You can then delete the .tar.bz2 files

Finally, run download_jsons.py to download the meta-data files for each downloaded paper

