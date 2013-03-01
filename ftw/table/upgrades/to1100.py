from ftw.upgrade import UpgradeStep


class UpdateTableStyles(UpgradeStep):

    def __call__(self):
        self.setup_install_profile(
            'profile-ftw.table.upgrades:1100')
