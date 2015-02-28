"""

api.* ( see :doc:`api_general` )

models.* ( see the code )

constants.* ( see the code )


utils.* several utility functions:

.. automodule:: todoapp1.backend1.utils
    :members:

"""

import models
import api
import utils
import todoapp1.settings.constants as constants

__all__= [
    "api"
    "constants"
    "models"
    "utils"
]
