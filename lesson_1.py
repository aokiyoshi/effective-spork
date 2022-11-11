import locale
import platform
from ipaddress import IPv4Address, ip_address
from subprocess import PIPE, Popen
from typing import Dict, List

from tabulate import tabulate

ENCODING = locale.getpreferredencoding()


def host_ping(ip_addr_list: List[IPv4Address | str]) -> List[str]:

    # Определяем параметр для пинга
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Запускаем процессы
    handles = [Popen(['ping', param, '5', f'{addr}'],
                     stdout=PIPE, stderr=PIPE) for addr in ip_addr_list]

    # Собираем результаты с процессов и возвращаем в виде списка
    return [
        handle.wait() == 0 and 'TTL' in handle.stdout.read().decode(ENCODING)
        for handle in handles
    ]


def host_range_ping(first_addr: IPv4Address, quantity: int) -> List[Dict]:

    # Определяем список адресов, должны быть типа IPv4Address
    ip_range = [first_addr + num for num in range(quantity)]

    # Проходим по списку, который вернула функция host_ping,
    # если истина то из ip_range выбираем адресс с тем же индексом,
    # а пото записываем ввиде словаря
    return [
        {'Reachable': f'{ip_range[idx]}'} if res else
        {'Unreachable': f'{ip_range[idx]}'}
        for idx, res in enumerate(host_ping(ip_range))
    ]


def host_range_ping_tab() -> None:

    # Ввод первого адреса
    first_addr = ''
    while not first_addr:
        # Пытаемся пока не дождемся валидный адрес от пользователя
        try:
            first_addr = ip_address(input('Введите первый ip-адрес: '))
        except ValueError:
            print('Введите корректный IPv4 адрес')

    # Ввод диапазона
    quantity = None
    last_octet = (int(f'{first_addr}'.split('.')[-1]))
    while quantity is None:
        try:
            quantity = int(input('Сколько адресов?: '))
        except ValueError:
            print('Введите число')
            continue
        if last_octet + quantity > 254:
            print('Диапазон адресов превышаешает максимально число! Диапазон уменьшен.')
            quantity = 254 - last_octet

    # Печатаем с помощью tabulate
    print(
        tabulate(
            host_range_ping(first_addr, quantity), headers='keys'
        )
    )

if __name__ == "__main__":
    host_range_ping_tab()
