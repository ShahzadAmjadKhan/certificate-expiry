import datetime
import OpenSSL
from paramiko import SSHClient, AutoAddPolicy


def pluralise(singular, count):
    return '{} {}{}'.format(count, singular, '' if count == 1 else 's')


def format_host_port(host, port):
    return host + ('' if port == DEFAULT_SSH_PORT else ':{}'.format(port))


def format_time_remaining(time_remaining):
    day_count = time_remaining.days

    if day_count >= WARN_IF_DAYS_LESS_THAN:
        return pluralise('day', day_count)

    else:
        seconds_per_minute = 60
        seconds_per_hour = seconds_per_minute * 60
        seconds_unaccounted_for = time_remaining.seconds

        hours = int(seconds_unaccounted_for / seconds_per_hour)
        seconds_unaccounted_for -= hours * seconds_per_hour

        minutes = int(seconds_unaccounted_for / seconds_per_minute)

        return '{} {} {}'.format(
            pluralise('day', day_count),
            pluralise('hour', hours),
            pluralise('min', minutes)
        )


def get_certificate_expiry_date_time(certificate):
    x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, certificate)
    expiry_date = datetime.datetime.strptime(x509.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%S%z')
    return datetime.datetime.strptime(expiry_date.strftime('%b %d %H:%M:%S %Y %Z'), r'%b %d %H:%M:%S %Y %Z')


def get_certificate_from_server(host, port, user_name, certificate_file ):
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    host = host + '.redmath.org'
    ssh.connect(hostname=host, port=port, username=user_name)

    sftp_client = ssh.open_sftp()
    remote_file = sftp_client.open(certificate_file)
    certificate = ''
    try:
        for line in remote_file:
            certificate += line
    finally:
        remote_file.close()

    return certificate


def determine_remaining_days(host, port, expiry_time):
    time_remaining = expiry_time - datetime.datetime.utcnow()
    time_remaining_txt = format_time_remaining(time_remaining)
    days_remaining = time_remaining.days

    print('{} {:<5} expires in {}'.format(
        format_host_port(host, port),
        'WARN' if days_remaining < WARN_IF_DAYS_LESS_THAN else 'OK',
        time_remaining_txt))

    return days_remaining

class server:
    def __init__(self, host, port, user_name, cert_path):
        self.host = host
        self.port = port
        self.user_name = user_name
        self.cert_path = cert_path

DEFAULT_SSH_PORT = 22
WARN_IF_DAYS_LESS_THAN = 60


if __name__ == '__main__':

    servers = []
    servers.append(server('dev-fts-l01',22,'shahzad','/etc/ssl/certs/IdenTrust_Commercial_Root_CA_1.pem'))
    servers.append(server('dev-fts-l05',22,'redmath','/etc/ssl/certs/DigiCert_Assured_ID_Root_CA.pem'))
    servers.append(server('dev-fts-l06',22,'redmath','/etc/ssl/certs/QuoVadis_Root_CA_1_G3.pem'))

    for server in servers:
        certificate = get_certificate_from_server(server.host, server.port, server.user_name, server.cert_path)
        expiry_time = get_certificate_expiry_date_time(certificate)
        remaining_days = determine_remaining_days(server.host, server.port, expiry_time)

    # if(remaining_days < WARN_IF_DAYS_LESS_THAN):
    #     # send_email()
