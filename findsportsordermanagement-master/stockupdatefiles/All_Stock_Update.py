AllStockUpdate = True

if not (AllStockUpdate):
    XTM = True
    SPELEAN = False
    REEF = False
    DROPSHIPZONE = False
    COLUMBIA = False
    JETPILOT = False
    PHOENIX = False
    OCEANEARTH = False
    ROJO = False
    ROSBERT = False
    ZENIMPORT = False
    LIIVE = False
    HGB = False
else:
    XTM = True
    SPELEAN = True
    REEF = True
    DROPSHIPZONE = True
    COLUMBIA = True
    JETPILOT = True
    PHOENIX = True
    OCEANEARTH = True
    ROJO = True
    ROSBERT = True
    ZENIMPORT = True
    LIIVE = True
    HGB = True

###PENDING
# CAPEBYRON
# COMPANION
# BOLLE
# WHITEROOM
# ABSOLUTE


if (XTM):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("XTM Stock update started")
            import XTM_STOCKUPDATE

            print("XTM Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1

if (SPELEAN):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("SPELEAN Stock update started")
            import SPELEAN_STOCKUPDATE

            print("SPELEAN Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (REEF):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("REEF Stock update started")
            import REEF_STOCKUPDATE

            print("REEF Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (DROPSHIPZONE):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("DROPSHIPZONE Stock update started")
            import Dropshipzone

            print("DROPSHIPZONE Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (COLUMBIA):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("COLUMBIA Stock update started")
            import COLUMBIA_STOCKUPDATE

            print("COLUMBIA Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (JETPILOT):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("JETPILOT Stock update started")
            import JETPILOT_STOCKUPDATE

            print("JETPILOT Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1

if (PHOENIX):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("PHOENIX Stock update started")
            import PHOENIX_STOCKUPDATE

            print("PHOENIX Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (OCEANEARTH):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("OCEANEARTH Stock update started")
            import OCEANEARTH_STOCKUPDATE

            print("OCEANEARTH Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (ROJO):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("ROJO Stock update started")
            import ROJO_STOCKUPDATE

            print("ROJO Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (ROSBERT):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("ROSBERT Stock update started")
            import ROSBERT_STOCKUPDATE

            print("ROSBERT Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (ZENIMPORT):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("ZENIMPORT Stock update started")
            import ZenImport_Stock

            print("ZENIMPORT Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
if (LIIVE):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("LIIVE Stock update started")
            import Liive

            print("LIIVE Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1

if (HGB):
    error_found = True
    max_count = 0
    while (error_found == True and max_count <= 5):
        try:
            print("HGB Stock update started")
            import HGB_STOCKUPDATE

            print("HGB Stock update completed")
            error_found = False
        except:
            print("Error!")
            error_found = True
            max_count += 1
