DATA_DIR = "./data"

ENDPOINT = "object.files.data.gouv.fr"
BUCKET = "meteofrance-drias"

RCM_DIRECTORY_TEMPLATE = "SocleM-Climat-2025/RCM/%(project)s/%(domain)s/%(gcm)s/%(member)s/%(rcm)s/%(experiment)s/%(timestep)s/%(variable)s/version-hackathon-102025"
RCM_FILENAME_TEMPLATE = "%(variable)s_%(region)s_%(gcm)s_%(experiment)s_%(member)s_%(institute)s_%(rcm)s_%(version)s_%(bias_adjustment)s_%(timestep)s_%(date_beg)s-%(date_end)s.nc"

CPCRM_DIRECTORY_TEMPLATE = "SocleM-Climat-2025/CPCRCM/%(project)s/%(domain)s/%(gcm)s/%(member)s/%(rcm)s/%(experiment)s/%(timestep)s/%(variable)s/version-hackathon-102025"
CPCRM_FILENAME_TEMPLATE = "%(variable)s_%(region)s_%(gcm)s_%(experiment)s_%(member)s_%(institute)s_%(rcm)s_%(version)s_%(bias_adjustment)s_%(timestep)s_%(date_beg)s-%(date_end)s.nc"