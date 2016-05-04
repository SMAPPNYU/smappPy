import imghdr
import urllib

class EmptyImageException(Exception):
    """Custom exception for case when image read from URL is 0 bytes/empty"""
    pass

class ImageFormatException(Exception):
    """Custom exception for case when image type not understood by imghdr"""
    pass


def save_web_image(url, filename):
    """Attempts to get image from url, stores it in file. Throws exceptions directly
    from urllib functions (urlretrieve)"""
    
    url_contents = urllib.urlopen(url).read()
    if len(url_contents) < 1:
        raise EmptyImageException("URL '{0}' returned empty file")
    
    img_type = imghdr.what(None, h=url_contents)
    if not img_type:
        raise ImageFormatException("imghdr failed to type image at {0}".format(url))
    filename += ".{0}".format(img_type)

    with open(filename, "wb") as handle:    
        handle.write(url_contents)
