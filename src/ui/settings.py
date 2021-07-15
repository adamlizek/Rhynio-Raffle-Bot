from src.actions.lapstone import lapstone_enter_raffle, lapstone_collect_tokens, lapstone_email_confirmation, lapstone_generate_abck
from src.actions.premier import premier_account_gen, premier_enter_raffle
from src.actions.naked_new import naked_account_gen as new_naked_account_gen
from src.actions.naked_new import naked_enter_raffle as new_naked_enter_raffle
from src.actions.naked_new import naked_collect_tokens as new_naked_collect_tokens
from src.actions.naked_new import naked_email_confirmation as new_naked_email_confirmations
from src.actions.dtlr import dtlr_enter_raffle, dtlr_collect_tokens, dtlr_confirm_entries
from src.actions.basket4ballers import b4b_enter_raffle
from src.actions.bodega import bodega_enter_raffle
from src.actions.undefeated import undefeated_enter_raffle
from src.actions.dsm import dsm_enter_raffle
from src.actions.dsml import dsml_enter_raffle
from src.actions.sjs import sjs_account_gen, sjs_enter_raffle
from src.actions.atmos import atmos_enter_raffle, atmos_confirm_entries, atmos_collect_tokens

# ==================================================
# ===== HARDCODED LISTS / CORRESPONDING ACTION =====
# ==================================================
SITES = {
    0: 'ATMOS',
    1: 'BASKET4BALLERS',
    2: 'BODEGA',
    3: 'DSM',
    4: 'DSML',
    5: 'DTLR',
    6: 'LAPSTONE',
    7: 'NAKED',
    8: 'PREMIER',
    9: 'SJS',
    10: 'UNDEFEATED',
}

MODES = {
    0: 'ACCOUNT GENERATION',
    1: 'ENTER RAFFLE',
    2: 'COLLECT TOKENS',
    3: 'CONFIRM ENTRIES',
}

ACTIONS = {
    'ATMOS': {
        'ACCOUNT GENERATION': 'DNE',
        'ENTER RAFFLE': atmos_enter_raffle,
        'COLLECT TOKENS': atmos_collect_tokens,
        'CONFIRM ENTRIES': atmos_confirm_entries
    },
    'BASKET4BALLERS': {
        'ACCOUNT GENERATION': 'DNE',
        'ENTER RAFFLE': b4b_enter_raffle,
        'COLLECT TOKENS': 'DNE',
        'CONFIRM ENTRIES': 'DNE'
    },
    'BODEGA': {
        'ACCOUNT GENERATION': 'DNE',
        'ENTER RAFFLE': bodega_enter_raffle,
        'COLLECT TOKENS': 'DNE',
        'CONFIRM ENTRIES': 'DNE'
    },
    'DSM': {
        'ACCOUNT GENERATION': 'DNE',
        'ENTER RAFFLE': dsm_enter_raffle,
        'COLLECT TOKENS': 'DNE',
        'CONFIRM ENTRIES': 'DNE'
    },
    'DSML': {
        'ACCOUNT GENERATION': 'DNE',
        'ENTER RAFFLE': dsml_enter_raffle,
        'COLLECT TOKENS': 'DNE',
        'CONFIRM ENTRIES': 'DNE'
    },
    'DTLR': {
        'ACCOUNT GENERATION': 'DNE',
        'ENTER RAFFLE': dtlr_enter_raffle,
        'COLLECT TOKENS': dtlr_collect_tokens,
        'CONFIRM ENTRIES': dtlr_confirm_entries
    },
    'LAPSTONE': {
        'ACCOUNT GENERATION': lapstone_generate_abck,
        'ENTER RAFFLE': lapstone_enter_raffle,
        'COLLECT TOKENS': lapstone_collect_tokens,
        'CONFIRM ENTRIES': lapstone_email_confirmation
    },
    'PREMIER': {
        'ACCOUNT GENERATION': premier_account_gen,
        'ENTER RAFFLE': premier_enter_raffle,
        'COLLECT TOKENS': 'DNE',
        'CONFIRM ENTRIES': 'DNE'
    },
    'NAKED': {
        'ACCOUNT GENERATION': new_naked_account_gen,
        'ENTER RAFFLE': new_naked_enter_raffle,
        'COLLECT TOKENS': new_naked_collect_tokens,
        'CONFIRM ENTRIES': new_naked_email_confirmations
    },
    'SJS': {
        'ACCOUNT GENERATION': sjs_account_gen,
        'ENTER RAFFLE': sjs_enter_raffle,
        'COLLECT TOKENS': 'DNE',
        'CONFIRM ENTRIES': 'DNE'
    },
    'UNDEFEATED': {
        'ACCOUNT GENERATION': 'DNE',
        'ENTER RAFFLE': undefeated_enter_raffle,
        'COLLECT TOKENS': 'DNE',
        'CONFIRM ENTRIES': 'DNE'
    }
}


# ======================
# ===== TASK SETUP =====
# ======================
selected_site = SITES[0]
selected_mode = MODES[0]
selected_action = ACTIONS[selected_site][selected_mode]

