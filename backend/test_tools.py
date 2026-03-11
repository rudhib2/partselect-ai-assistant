from tools.search_parts import search_parts
from tools.compatibility import check_compatibility
from tools.troubleshooting import get_troubleshooting_guide
from tools.install_guide import get_install_guide


def main():
    print("\n--- SEARCH PARTS TEST ---")
    print(search_parts("dishwasher rack wheel"))
    print(search_parts("ice maker"))
    print(search_parts("PS11752778"))

    print("\n--- COMPATIBILITY TEST ---")
    print(check_compatibility("PS11752778", "WDT780SAEM1"))
    print(check_compatibility("PS11752778", "WRF535SWHZ"))

    print("\n--- TROUBLESHOOTING TEST ---")
    print(get_troubleshooting_guide("refrigerator", "ice maker not working"))
    print(get_troubleshooting_guide("dishwasher", "dishwasher leaking"))

    print("\n--- INSTALL GUIDE TEST ---")
    print(get_install_guide("PS11752778"))
    print(get_install_guide("PS200001"))
    print(get_install_guide("PS99999999"))


if __name__ == "__main__":
    main()