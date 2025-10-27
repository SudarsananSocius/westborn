from . import wizard
from . import models
from . import controllers


def post_init_hook(env):
    env['ir.config_parameter'].sudo().set_param('module_loyalty', True)
    