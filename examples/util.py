import shlex
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lauterbach.trace32.pystart import PowerView


def show_configuration(powerview: "PowerView") -> None:
    startup_script = ""
    if powerview.startup_script:
        tmp = []
        tmp.append("-s")
        tmp.append(str(powerview.startup_script))
        if isinstance(powerview.startup_parameter, str):
            tmp.extend(shlex.split(powerview.startup_parameter))
        else:
            tmp.extend(powerview.startup_parameter)
        startup_script = " ".join(tmp)

    print("#", powerview.executable, startup_script)
    print("|", powerview.get_configuration_string().replace("\n", "\n| "))
    print()
