"""Desktop entry point: python -m atlas_ultimate_crm"""
import sys


def main() -> None:
    from atlas_ultimate_crm.bootstrap import Bootstrap
    bootstrap = Bootstrap()
    bootstrap.initialize()

    from PySide6.QtWidgets import QApplication
    from atlas_ultimate_crm.ui.app import CRMApplication

    app = QApplication(sys.argv)
    crm_app = CRMApplication(bootstrap)
    crm_app.run()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
