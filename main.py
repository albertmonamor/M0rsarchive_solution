import os
import subprocess as sub
import requests as requests
from PIL import Image
from zipfile import is_zipfile, ZipFile

MORSE_API = "http://www.morsecode-api.de/{mode}?string={plain}"


class ReadMorseImage:

    # noinspection PyUnresolvedReferences
    def __init__(self, path_img):
        self.path_img = path_img
        self.img_stream = Image.open(path_img)
        self.px = self.img_stream.load()
        self.color_background = self.px[0, 0]  # 0x0 position
        self.__list_morse: str = ""

    def get_morse_from_img(self) -> str:
        """

        :return: str
        """
        count: int = 0
        for y in range(self.img_stream.size[1]):
            if y and self.__list_morse: self.__list_morse += " "
            for x in range(self.img_stream.size[0]):
                if self.color_background != self.px[x, y]:
                    count += 1
                elif count == 1 and self.color_background == self.px[x, y]:
                    self.__list_morse += "."
                    count = 0
                elif count == 3:
                    self.__list_morse += "-"
                    count = 0

        return self.__list_morse

    @staticmethod
    def get_decode_morse(morse_img: str) -> bytes:
        """

        :param morse_img: func get_morse_from_img
        :exception  if network or API server down
        :return: bytes
        """
        plain_decode = requests.get(url=MORSE_API.format(mode="decode", plain=morse_img))
        return plain_decode.json()['plaintext'].replace(" ", "").encode().lower()

    @property
    def get_encode_morse(self):
        return self.__list_morse

    def __exit__(self):
        self.img_stream.close()


def M0rsarchive(path):
    """

    :param path: path of zip file
    :return: pwd!
    """
    static_dir, basename = os.path.dirname(path), os.path.basename(path)
    img_name, zip_name = static_dir + "\\pwd.png", path
    counter, _range = 0, int(basename[basename.index("_") + 1:basename.index(".")])
    del basename
    while True:
        counter += 1
        # /* open zipfile */
        try:
            zip_read = ZipFile(zip_name)
        except PermissionError:
            flag = open(static_dir + '\\flag\\flag')
            print(f"\n flag from file: {flag.read()}")
            flag.close()
            exit(0x0)
        # /* get list-zip */
        # /* maybe length namelist is 1 */
        try:
            zipp, img = zip_read.namelist()
            members = zipp, img
        except ValueError:
            zipp, img = "flag", None  # end of challenge
            members = zip_read.namelist()

        # /* read password from img */
        read_pwd = ReadMorseImage(img_name)
        password = read_pwd.get_decode_morse(read_pwd.get_morse_from_img())
        zip_read.extractall(members=members, path=static_dir, pwd=password)
        # /* close io stream */
        zip_read.close()
        read_pwd.__exit__()

        # /* remove old file && move files from flag dir && rmdir flag */
        status = sub.Popen(f"del {zip_name} {img_name} && move {static_dir}\\flag\\* "
                           f"{static_dir} && rmdir /s /q {static_dir}\\flag",
                           stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        status.stderr.read()

        print(f"({(100 * counter) // _range}%-{counter} from {_range}) extract:"
              f" {os.path.basename(zipp)} and img. pwd: {password} (len {password.__len__()})"
              f". remove: {os.path.basename(zip_name)}")
        # update zip_name & counter */
        zip_name = static_dir + "\\" + os.path.basename(zipp)


M0rsarchive(r"<YOUR_PATH>\flag_999.zip")
