from . import api, constants, attributes
from .types import Response, Dict


def response_to_json(response: Response | dict) -> dict:
    '''Convert response to json. Do nothing if response is already dictionary
    
    Parameters
    ----------
    response : (Response | dict)
        Response to convert
    
    Returns
    -------
        dict
    
    '''

    return response.json() if isinstance(response,
                                         Response) else response


def extract_user_data(login_response: Response | dict) -> dict:
    '''Extract user data from login response
    
    Parameters
    ----------
    login_response : (Response | dict)
        Response from the login request.
    
    Returns
    -------
        dict
    
    '''

    login_response = response_to_json(login_response)

    return login_response.get('user', {})


def extract_student_data(login_response: Response | dict) -> dict:
    '''Extract student data from login response
    
    Parameters
    ----------
    login_response : (Response | dict)
        This is the response we get from the login request.
    
    Returns
    -------
        dict
    
    '''

    user_data = extract_user_data(login_response)

    return user_data.get('student', {})


def extract_access_token(login_response: Response | dict) -> str:
    '''Extract student code from login response
    
    Parameters
    ----------
    login_response : (Response | dict)
        This is the response from the login request.
    
    Returns
    -------
        str
    
    '''

    return login_response.get('accesstoken', '')


def extract_std_code(login_response: Response | dict) -> str:
    '''Extract student code from login response
    
    Parameters
    ----------
    login_response : (Response | dict)
        The response of the login request.
    
    Returns
    -------
        str
    
    '''

    login_response = response_to_json(login_response)
    student_data = extract_student_data(login_response)
    return student_data.get('stdCode', '')


def extract_std_id(login_response: Response | dict) -> str:
    '''Extract student id from login response
    
    Parameters
    ----------
    login_response : (Response | dict)
        The response of the login request.
    
    Returns
    -------
        Student id.
        
    '''

    login_response = response_to_json(login_response)
    student_data = extract_student_data(login_response)
    return student_data.get('stdId', '')


def extract_schedule(schedule_response: Response | dict, as_dict:bool=False, full_result:bool=False) -> tuple | dict | list:
    '''Extract schedule (academic_year, semester) from schedule response
    
    Parameters
    ----------
    schedule_response : (Response | dict)
        The response from the schedule request.
    as_dict : (bool, optional)
        Whether to return the result as a dictionary or not. By default False
    full_result : (bool, optional)
        If True, return the full result (List[dict]), otherwise return the first item. By default False
    
    Returns
    -------
        tuple | dict | list
    
    '''

    schedule_response = response_to_json(schedule_response)
    result = schedule_response.get('results')
    
    if full_result:
        return result
    
    if isinstance(result, list):
        result = result[0]
        
    if as_dict:
        return result
    return result.get('academicYr'), result.get('semester')

def gen_request_headers(access_token: str = '') -> dict:
    """Generate request headers.

    Parameters
    ----------
    access_token : (str, optional)
        MyKU acces token, by default None

    Returns
    -------
        dict
    
    """

    header = {
        'app-key': constants.APP_KEY,
    }
    if access_token:
        header['x-access-token'] = access_token
    return header


def gen_login_request_params(username: str, password: str) -> dict:
    """Generate request parameters for posting login request.

    Parameters
    ----------
    username : (str)
        Nontri account username (b##########)
    password : (str)
        Nontri account password (Don't worry, your password is not saved)

    Returns
    -------
        dict
        
    Format:
    ```python
        {
            'url': https://myapi.ku.th/auth/login,
            'data': {
                'username': username,
                'password': password,
            },
            'headers': {
                'app-key': constants.APP_KEY
        }
    }
    ```
    
    """

    return {
        'url': api.LOGIN,
        'data': {
            'username': username,
            'password': password,
        },
        'headers': {
            'app-key': constants.APP_KEY
        }
    }


def gen_request_params_f(function: callable, **kwargs) -> Dict[str, any]:
    """Generate request parameters requied for the given function.
    
    Passing only `login_response`, `schedule_response` or `client` is also acceptable for some request parameters.

    Parameters
    ----------
    function : (callable)
        Request function from pymyku.request module.

    Returns
    -------
        Dict[str, any]

    """

    name = function.__name__

    if kwargs.get('client'):
        client = kwargs['client']
        kwargs['login_response'] = client.get(
            attributes.FetchedResponses.LOGIN_RESPONSE)
        kwargs['schedule_response'] = client.get(
            attributes.FetchedResponses.SCHEDULE_RESPONSE)

    if kwargs.get('login_response'):
        login_response = kwargs.get('login_response')
        login_response = response_to_json(login_response)

        user_data = extract_user_data(login_response)

        student_data = user_data['student']

        if not kwargs.get('access_token'):
            kwargs['access_token'] = extract_access_token(login_response)

        kwargs['user_type'] = user_data['userType']

        for key, value in constants.STUDENT_PARAM_DICT.items():
            if not kwargs.get(key):
                kwargs[key] = student_data.get(value)

    if kwargs.get('schedule_response'):
        schedule_response = kwargs.get('schedule_response')
        schedule_response = response_to_json(schedule_response)

        schedule = extract_schedule(schedule_response)

        if not kwargs.get('academic_year'):
            kwargs['academic_year'] = schedule['academicYr']

        if not kwargs.get('semester'):
            kwargs['semester'] = schedule['semester']

    headers = gen_request_headers(kwargs.get('access_token'))

    if name == 'logout':

        return {
            'url': api.LOGOUT,
            'headers': headers,
        }

    elif name == 'get_schedule':

        return {
            'url': api.SCHEDULE,
            'headers': headers,
            'params': {
                'stdStatusCode': kwargs.get('student_status_code'),
                'campusCode': kwargs.get('campus_code'),
                'facultyCode': kwargs.get('faculty_code'),
                'majorCode': kwargs.get('major_code'),
                'userType': kwargs.get('user_type')
            }
        }

    elif name == 'get_group_course':

        return {
            'url': api.GROUP_COURSE,
            'headers': headers,
            'params': {
                "academicYear": kwargs.get('academic_year'),
                "semester": kwargs.get('semester'),
                "stdId": kwargs.get('std_id')
            }
        }
    elif name == 'get_check_grades':
        return {
            'url': api.CHECK_GRADES,
            'headers': headers,
            'params': {
                'stdCode': kwargs.get('std_code')
            }
        }

    elif name == 'get_gpax':
        return {
            'url': api.GPAX,
            'headers': headers,
            'params': {
                'stdId': kwargs.get('std_id')
            }
        }

    elif name == 'get_announce':
        return {
            'url': api.ANNOUCE,
            'headers': headers,
            'params': {
                'stdId': kwargs.get('std_id'),
                'academicYear': kwargs.get('academic_year'),
                'semester': kwargs.get('semester')
            }
        }
    elif name == 'search_enroll':
        return {
            'url': api.SEARCH_ENROLL,
            'headers': headers,
            'data': {
                'stdid': kwargs.get('std_id'),
                'academicYear': str(kwargs.get('academic_year')),
                'semester': str(kwargs.get('semester')),
            }
        }
    elif name == 'get_student_personal':
        return {
            'url': api.STUDENT_PERSONAL,
            'headers': headers,
            'params': {
                'stdId': kwargs.get('std_id')
            }
        }
    elif name == 'get_student_education':
        return {
            'url': api.STUDENT_EDUCATION,
            'headers': headers,
            'params': {
                'stdId': kwargs.get('std_id')
            }
        }
    elif name == 'get_student_address':
        return {
            'url': api.STUDENT_ADDRESS,
            'headers': headers,
            'params': {
                'stdId': kwargs.get('std_id')
            }
        }
    elif name == 'search_subject':
        return {
            'url': api.SEARCH_SUBJECT,
            'headers': headers,
            'params': {
                'query': kwargs.get('query'),
            }
        }
    elif name == 'search_subject_open':
        return {
            'url': api.SEARCH_SUBJECT_OPEN,
            'headers': headers,
            'params': {
                'query': kwargs.get('query'),
                'section': kwargs.get('section'),
                'campusCode': kwargs.get('campus_code'),
                'academicYear': kwargs.get('academic_year'),
                'semester': kwargs.get('semester')
            }
        }
    elif name == 'search_section_detail':
        return {
            'url': api.SEARCH_SECTION_DETAIL,
            'headers': headers,
            'params': {
                'sectionId': kwargs.get('section_id')
            }
        }
