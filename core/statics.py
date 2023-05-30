SELLER = 'S'
PURCHER = 'P'
PURCHERANDSALLER = 'PS'
PHARMACYMANAGER = 'PM'
MANAGER = 'M'

ROLE_CHOICES = [
    (SELLER,'Seller'),
    (PURCHER,'Purcher'),
    (PURCHERANDSALLER,'Purcher And Seller'),
    (PHARMACYMANAGER,'PharmacyManager'),
    (MANAGER,'Manager'),
    ]

LIQUIDS = 'LIQ'
TABLETS = 'TAB'
CAPSULES = 'CAP'
DROPS = 'DRO'
INJECTIONS = 'INJ'
SUPPOSITORIES = 'SUP'
INHALERS = 'INH'
TOPICALS = 'TOP'

TYPE_CHOICES = [
    (LIQUIDS,'Liquids'),
    (TABLETS, 'Tablets'),
    (CAPSULES, 'Capsules'),
    (DROPS, 'Drops'),
    (INJECTIONS, 'Injections'),
    (SUPPOSITORIES, 'Suppositories'),
    (INHALERS, 'Inhalers'),
    (TOPICALS, 'Topicals')
]


DAY_CHOICES = [
    (1,'Saturday'),
    (2, 'Sunday'),
    (3, 'Monday'),
    (4, 'Tuesday'),
    (5, 'Wednesday'),
    (6, 'Thursday'),
    (7, 'Friday'),
]

EXPIRY_NOT = "E"
AMOUNT_NOT = "A"

NOTIFICATION_CHOICES = [
    (EXPIRY_NOT,'Expiry notification'),
    (AMOUNT_NOT,'Amount notification'),
]


roles_map = {
            'S':"saller",
            'P':"purcher",
            'PM':"pharmacy_manager",
            'M':"manager",
            }