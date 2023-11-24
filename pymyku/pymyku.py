from __future__ import annotations
from dataclasses import dataclass
from dataclass_wizard import JSONWizard
from requests import Session

from pymyku import __version__, consts, utils
from pymyku import api


@dataclass()
class Payload(JSONWizard):
    username: str
    usertype: str
    idcode: str
    stdid: str
    first_name_en: str
    first_name_th: str
    last_name_en: str
    last_name_th: str
    title_th: str
    role_id: str
    std_status_code: str
    iat: int
    exp: int


class PyMyKU:
    def __init__(self, username: str, password: str):
        self.__session: Session = Session()
        self.__access_token_payload: Payload

        self.__session.headers.update({
           "User-Agent": f"pymyku/{__version__}",
           "app-key": consts.APP_KEY,
        })


        hashed_username = utils.hash_credential(username)
        hashed_password = utils.hash_credential(password)

        self.__login_res = api.auth.login(self.__session, hashed_username, hashed_password)

        self.set_access_token(self.__login_res.accesstoken)

    def set_access_token(self, access_token: str) -> None:
        self.__access_token_payload = Payload.from_dict(
            utils.decode_access_token(access_token)
        )

        self.__session.headers.update({
            "x-access-token": access_token,
        })

    @property
    def session(self):
        return self.__session

    @property
    def access_token_payload(self):
        return self.__access_token_payload

    @property
    def user(self):
        return self.__login_res.user

    @property
    def student(self):
        return self.__login_res.user.student
    
    def get_schedule(self, std_status_code: str = '', campus_code: str = '', faculty_code: str = '', major_code: str = '', user_type: str = '') -> api.common.Getschedule:

        if std_status_code == '':
            std_status_code = self.student.student_status_code

        if campus_code == '':
            campus_code = self.student.campus_code

        if faculty_code == '':
            faculty_code = self.student.faculty_code

        if major_code == '':
            major_code = self.student.major_code

        if user_type == '':
            user_type = self.__login_res.user.user_type

        return api.common.getschedule(self.session, std_status_code, campus_code, faculty_code, major_code, user_type)
    
