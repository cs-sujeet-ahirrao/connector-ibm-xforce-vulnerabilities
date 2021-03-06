""" 
Copyright start 
Copyright (C) 2008 - 2021 Fortinet Inc. 
All rights reserved. 
FORTINET CONFIDENTIAL & FORTINET PROPRIETARY SOURCE CODE 
Copyright end 
"""
import base64

import requests

from connectors.core.connector import get_logger, ConnectorError

logger = get_logger('ibm-xforce-vulnerabilities')


class IBMXFVulnerabilities(object):
    def __init__(self, config):
        self.server_url = config.get('server_url')
        if not self.server_url.startswith('https://'):
            self.server_url = 'https://' + self.server_url
        if not self.server_url.endswith('/'):
            self.server_url += '/'
        self.api_key = config.get('api_key')
        self.api_password = config.get('api_password')
        self.verify_ssl = config.get('verify_ssl')

    def make_request(self, endpoint=None, method='GET', data=None, params=None, files=None):
        try:
            url = self.server_url + endpoint
            b64_credential = base64.b64encode((self.api_key + ":" + self.api_password).encode('utf-8')).decode()
            headers = {'Authorization': "Basic " + b64_credential, 'Content-Type': 'application/json'}
            response = requests.request(method, url, params=params, files=files, data=data, headers=headers,
                                        verify=self.verify_ssl)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(response.text)
                raise ConnectorError({'status_code': response.status_code, 'message': response.reason})
        except requests.exceptions.SSLError:
            raise ConnectorError('SSL certificate validation failed')
        except requests.exceptions.ConnectTimeout:
            raise ConnectorError('The request timed out while trying to connect to the server')
        except requests.exceptions.ReadTimeout:
            raise ConnectorError('The server did not send any data in the allotted amount of time')
        except requests.exceptions.ConnectionError:
            raise ConnectorError('Invalid endpoint or credentials')
        except Exception as err:
            logger.exception(str(err))
            raise ConnectorError(str(err))


def get_recent_vulnerabilities(config, params):
    vuln = IBMXFVulnerabilities(config)
    param_dict = {k: v for k, v in params.items() if v is not None and v != '' and v != {} and v != []}
    endpoint = 'vulnerabilities/'
    return vuln.make_request(endpoint=endpoint, params=param_dict)


def get_updated_vulnerabilities(config, params):
    vuln = IBMXFVulnerabilities(config)
    param_dict = {k: v for k, v in params.items() if v is not None and v != '' and v != {} and v != []}
    endpoint = 'vulnerabilities/change'
    return vuln.make_request(endpoint=endpoint, params=param_dict)


def search_vulnerabilities(config, params):
    vuln = IBMXFVulnerabilities(config)
    param_dict = {k: v for k, v in params.items() if v is not None and v != '' and v != {} and v != []}
    endpoint = 'vulnerabilities/fulltext'
    return vuln.make_request(endpoint=endpoint, params=param_dict)


def search_vulnerabilities_xfid(config, params):
    vuln = IBMXFVulnerabilities(config)
    endpoint = 'vulnerabilities/' + str(params.get('xfid'))
    return vuln.make_request(endpoint=endpoint)


def search_vulnerabilities_stdcode(config, params):
    vuln = IBMXFVulnerabilities(config)
    endpoint = 'vulnerabilities/search/' + str(params.get('stdcode'))
    return vuln.make_request(endpoint=endpoint)


def search_vulnerabilities_ms_secid(config, params):
    vuln = IBMXFVulnerabilities(config)
    endpoint = 'vulnerabilities/msid/' + str(params.get('msid'))
    return vuln.make_request(endpoint=endpoint)


def _check_health(config):
    try:
        params = {}
        res = get_recent_vulnerabilities(config, params)
        if res:
            logger.info('connector available')
            return True
    except Exception as e:
        logger.exception('{}'.format(e))
        raise ConnectorError('{}'.format(e))


operations = {
    'get_recent_vulnerabilities': get_recent_vulnerabilities,
    'get_updated_vulnerabilities': get_updated_vulnerabilities,
    'search_vulnerabilities': search_vulnerabilities,
    'search_vulnerabilities_xfid': search_vulnerabilities_xfid,
    'search_vulnerabilities_stdcode': search_vulnerabilities_stdcode,
    'search_vulnerabilities_ms_secid': search_vulnerabilities_ms_secid
}
