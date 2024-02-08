
class CCRType(object):
    GLOBAL = "global"
    APP = "app"
    SELFMOD = "selfmod"


# default-on modules
CORE = [

    ]

# internal rules
INTERNAL = [
    "GrammarActivatorRule", "HooksActivationRule", "TransformersActivationRule",
    "ManualGrammarReloadRule"
]

# default companion rules
COMPANION_STARTER = {

}
