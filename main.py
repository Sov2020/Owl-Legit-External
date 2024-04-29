version = "0.2.6.4"
title = f"[v{version}] Owl-Legit"

import win32gui, time, json, os, threading, psutil, win32process, win32api, win32con, random, requests, win32console, ctypes, sys, datetime, keyboard, webbrowser # type: ignore

from pymem import Pymem, process
from re import search

import dearpygui.dearpygui as dpg
import pyMeow as pm

user32 = ctypes.WinDLL("user32")
configFilePath = f"{os.environ['LOCALAPPDATA']}\\temp\\OwlLegit"
sys.setrecursionlimit(5000)

class configListener(dict):
    def __init__(self, initialDict):
        for k, v in initialDict.items():
            if isinstance(v, dict):
                initialDict[k] = configListener(v)

        super().__init__(initialDict)

    def __setitem__(self, item, value):
        if isinstance(value, dict):
            value = configListener(value)

        super().__setitem__(item, value)

        if hasattr(panosdiosClass, "config"):
            json.dump(panosdiosClass.config, open(configFilePath, "w", encoding="utf-8"), indent=4)

class Colors:
    white = pm.get_color("white")
    whiteWatermark = pm.get_color("#f5f5ff")
    black = pm.get_color("black")
    blackFade = pm.fade_color(black, 0.6)
    red = pm.get_color("#e03636")
    green = pm.get_color("#43e06d")

class Offsets:
    m_pBoneArray = 480

class Entity:
    def __init__(self, ptr, pawnPtr, proc):
        self.ptr = ptr
        self.pawnPtr = pawnPtr
        self.proc = proc
        self.pos2d = None
        self.headPos2d = None

    @property
    def name(self):
        return pm.r_string(self.proc, self.ptr + Offsets.m_iszPlayerName)

    @property
    def health(self):
        return pm.r_int(self.proc, self.pawnPtr + Offsets.m_iHealth)

    @property
    def team(self):
        return pm.r_int(self.proc, self.pawnPtr + Offsets.m_iTeamNum)

    @property
    def pos(self):
        return pm.r_vec3(self.proc, self.pawnPtr + Offsets.m_vOldOrigin)
    
    @property
    def isDormant(self):
        return pm.r_bool(self.proc, self.pawnPtr + Offsets.m_bDormant)

    def bonePos(self, bone):
        gameScene = pm.r_int64(self.proc, self.pawnPtr + Offsets.m_pGameSceneNode)
        boneArrayPtr = pm.r_int64(self.proc, gameScene + Offsets.m_pBoneArray)

        return pm.r_vec3(self.proc, boneArrayPtr + bone * 32)
    
    def wts(self, viewMatrix):
        try:
            a, self.pos2d = pm.world_to_screen_noexc(viewMatrix, self.pos, 1)
            b, self.headPos2d = pm.world_to_screen_noexc(viewMatrix, self.bonePos(6), 1)
            
            if not a or not b:
                return False

            return True
        except:
            return False

class panosdios:
    def __init__(self):
        self.config = {
            "version": version,
            "esp": {
                "enabled": True,
                "bind": 0,
                "box": True,
                "showvisible":False,
                "boxBackground": False,
                "boxRounding": 0.1,
                "skeleton": True,
                "ShowHead": False,
                "snapline": False,
                "onlyEnemies": True,
                "name": False,
                "health": True,
                "color": {"r": 0.303, "g": 0.669, "b": 0.232, "a": 0.8}
            },
            "FOV": {
                "enabled": False, #detected
                "FOVnum": 90,
            },
            "triggerBot": {
                "enabled": False,
                "bind": 0,
                "onlyEnemies": True,
                "delay": 0.1,
            },
            "misc": {
                "GranadePoz": False, #detected
                "noFlash": False, #detected
                "watermark": True,
                "BombHelper": False
            },
            "bhopio": {
                "bhop": False
            },
            "settings": {
                "saveSettings": False,
                "streamProof": False
            }     
        }

        if os.path.isfile(configFilePath):
            try:
                config = json.loads(open(configFilePath, encoding="utf-8").read())

                isConfigOk = True
                for key in self.config:
                    if not key in config or len(self.config[key]) != len(config[key]):
                        isConfigOk = False

                        break

                if isConfigOk:
                    if not config["settings"]["saveSettings"]:
                        self.config["settings"]["saveSettings"] = False
                    else:
                        if config["version"] == version:
                            self.config = config
            except:
                pass

        self.config = configListener(self.config)

        self.guiWindowHandle = None
        self.overlayWindowHandle = None

        self.overlayThreadExists = False
        self.localTeam = None

        self.espColor = pm.new_color_float(self.config["esp"]["color"]["r"], self.config["esp"]["color"]["g"], self.config["esp"]["color"]["b"], self.config["esp"]["color"]["a"])
        self.espBackGroundColor = pm.fade_color(self.espColor, 0.1)

        self.run()

    def isCsOpened(self):
        while True:
            if not pm.process_running(self.proc):
                os._exit(0)

            time.sleep(3)

    def windowListener(self):
        while True:
            try:
                self.focusedProcess = psutil.Process(win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[-1]).name()
            except:
                self.focusedProcess = ""

            time.sleep(0.5)

    def run(self):
        print("Waiting for CS2...")

        while True:
            time.sleep(1)

            try:
                self.proc = pm.open_process("cs2.exe")
                self.mod = pm.get_module(self.proc, "client.dll")["base"]

                break
            except:
                pass

        print("Starting Owl-Legit!")

        os.system("cls")

        print('''        
░█████╗░░██╗░░░░░░░██╗██╗░░░░░░░░░░░██╗░░░░░███████╗░██████╗░██╗████████╗
██╔══██╗░██║░░██╗░░██║██║░░░░░░░░░░░██║░░░░░██╔════╝██╔════╝░██║╚══██╔══╝
██║░░██║░╚██╗████╗██╔╝██║░░░░░█████╗██║░░░░░█████╗░░██║░░██╗░██║░░░██║░░░
██║░░██║░░████╔═████║░██║░░░░░╚════╝██║░░░░░██╔══╝░░██║░░╚██╗██║░░░██║░░░
╚█████╔╝░░╚██╔╝░╚██╔╝░███████╗░░░░░░███████╗███████╗╚██████╔╝██║░░░██║░░░
░╚════╝░░░░╚═╝░░░╚═╝░░╚══════╝░░░░░░╚══════╝╚══════╝░╚═════╝░╚═╝░░░╚═╝░░░
made by Sov with ♥
              
TG: @owllegit
YT: @sov2020
        ''')

        webbrowser.open("https://www.youtube.com/channel/UCdSmstLR9Jg9Nmz1_ntXzyg")
        webbrowser.open("https://t.me/OwlLegit")

        try:
            offsetsName = ["dwViewMatrix", "dwEntityList", "dwLocalPlayerController", "dwLocalPlayerPawn", "dwPlantedC4"]
            offsets = requests.get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json").json()
            [setattr(Offsets, k, offsets["client.dll"][k]) for k in offsetsName]

            clientDllName = {
                "m_iDesiredFOV":"CBasePlayerController",
                "m_iIDEntIndex": "C_CSPlayerPawnBase",
                "m_hPlayerPawn": "CCSPlayerController",
                "m_fFlags": "C_BaseEntity",
                "m_iszPlayerName": "CBasePlayerController",
                "m_iHealth": "C_BaseEntity",
                "m_iTeamNum": "C_BaseEntity",
                "m_vOldOrigin": "C_BasePlayerPawn",
                "m_pGameSceneNode": "C_BaseEntity",
                "m_bDormant": "CGameSceneNode",
                "m_nBombSite":"C_PlantedC4",
                "m_bBeingDefused":"C_PlantedC4",
                "m_bBombDefused":"C_PlantedC4",
                #"m_bSpotted":"EntitySpottedState_t",
                #"m_entitySpottedState":"C_CSPlayerPawnBase"
            }
            clientDll = requests.get("https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client.dll.json").json()
            [setattr(Offsets, k, clientDll["client.dll"]["classes"][clientDllName[k]]["fields"][k]) for k in clientDllName]
        except Exception as e:
            print(e)
            input("Can't retrieve offsets. Press any key to exit!")

            os._exit(0)

        threading.Thread(target=self.isCsOpened, daemon=True).start()
        threading.Thread(target=self.windowListener, daemon=True).start()
        threading.Thread(target=self.espBindListener, daemon=True).start()

        if self.config["esp"]["enabled"] or self.config["misc"]["watermark"]:
            threading.Thread(target=self.esp, daemon=True).start()

        if self.config["triggerBot"]["enabled"]:
            threading.Thread(target=self.triggerBot, daemon=True).start()

        if self.config["misc"]["GranadePoz"]:
            threading.Thread(target=self.GranadePoz, daemon=True).start()
            
        if self.config["misc"]["noFlash"]:
            self.noFlash()

    def espBindListener(self):
        while not hasattr(self, "focusedProcess"):
            time.sleep(0.1)
        
        while True:
            if self.focusedProcess != "cs2.exe":
                time.sleep(1)

                continue

            time.sleep(0.001)

            bind = self.config["esp"]["bind"]

            if win32api.GetAsyncKeyState(bind) == 0: continue

            self.config["esp"]["enabled"] = not self.config["esp"]["enabled"]

            if self.config["esp"]["enabled"] and not self.overlayThreadExists:
                threading.Thread(target=self.esp, daemon=True).start()
            
            while True:
                try:
                    dpg.set_value(checkboxToggleEsp, not dpg.get_value(checkboxToggleEsp))

                    break
                except:
                    time.sleep(1)

                    pass

            while win32api.GetAsyncKeyState(bind) != 0:
                time.sleep(0.001)

    def getEntities(self):
        entList = pm.r_int64(self.proc, self.mod + Offsets.dwEntityList)
        local = pm.r_int64(self.proc, self.mod + Offsets.dwLocalPlayerController)
        
        for i in range(1, 65):
            try:
                entryPtr = pm.r_int64(self.proc, entList + (8 * (i & 0x7FFF) >> 9) + 16)
                controllerPtr = pm.r_int64(self.proc, entryPtr + 120 * (i & 0x1FF))
                
                if controllerPtr == local:
                    self.localTeam = pm.r_int(self.proc, local + Offsets.m_iTeamNum)

                    continue

                controllerPawnPtr = pm.r_int64(self.proc, controllerPtr + Offsets.m_hPlayerPawn)
                listEntryPtr = pm.r_int64(self.proc, entList + 0x8 * ((controllerPawnPtr & 0x7FFF) >> 9) + 16)
                pawnPtr = pm.r_int64(self.proc, listEntryPtr + 120 * (controllerPawnPtr & 0x1FF))
            except:
                continue

            yield Entity(controllerPtr, pawnPtr, self.proc)

    def esp(self):
        global bombplanted
        global bombdefuse
        global bombdefusecanorno

        bombplanted = "IF YOU SEE IT \nRESTART FUNCTION"
        bombdefuse = ""
        bombdefusecanorno = "IF YOU SEE IT \nRESTART FUNCTION"

        self.overlayThreadExists = True

        while not hasattr(self, "focusedProcess"):
            time.sleep(0.1)

        pm.overlay_init("Counter-Strike 2", fps=120, title="".join(random.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(8)), trackTarget=True)
        
        self.overlayWindowHandle = pm.get_window_handle()
        if self.config["settings"]["streamProof"]:
            user32.SetWindowDisplayAffinity(self.overlayWindowHandle, 0x00000011)
        else:
            user32.SetWindowDisplayAffinity(self.overlayWindowHandle, 0x00000000)

        while pm.overlay_loop():
            pm.begin_drawing()

            if self.focusedProcess != "cs2.exe":
                pm.end_drawing()

                time.sleep(1)

                continue
            
            #show bomb helper
            if self.config["misc"]["BombHelper"]:
                    
                BombHelperText = f"Bomb Helper"

                bp = bombplanted
                bd = bombdefuse
                bdcon = bombdefusecanorno

                pm.draw_rectangle_rounded(5, 50, 210, 135, 0.2, 4, Colors.blackFade)
                pm.draw_rectangle_rounded_lines(5, 50, 210, 135, 0.2, 4, self.espBackGroundColor, 2)
                pm.draw_text(BombHelperText, 47.5, 51, 20, Colors.whiteWatermark)
                pm.draw_text(bp, 15, 75, 20, Colors.whiteWatermark)
                pm.draw_text(bd, 15, 125, 20, Colors.whiteWatermark)
                pm.draw_text(bdcon, 40, 75, 20, Colors.whiteWatermark)

            #watermark + modulemark
            if self.config["misc"]["watermark"]:
                watermark = f"OwlLegit | {pm.get_fps()} fps"
                modulemark = "Modules Active"

                xPos = -(-(185 - pm.measure_text(watermark, 20)) // 2)+1
                ry = 30    

                pm.draw_rectangle_rounded(5, 5, 180, 30, 0.2, 4, Colors.blackFade)
                pm.draw_rectangle_rounded_lines(5, 5, 180, 30, 0.2, 4, self.espBackGroundColor, 2)
                pm.draw_text(watermark, xPos, 11, 20, Colors.whiteWatermark)

                pm.draw_rectangle_rounded(1735, 5, 180, ry, 0.2, 4, Colors.blackFade)
                pm.draw_rectangle_rounded_lines(1735, 5, 180, 30, 0.2, 4, self.espBackGroundColor, 2)
                pm.draw_text(modulemark, 1750, 11, 20, Colors.whiteWatermark)

                if self.config["esp"]["enabled"]:
                    espmark = f"ESP"

                    pm.draw_rectangle_rounded(1735, 50, 180, 30, 0.2, 4, Colors.blackFade)
                    pm.draw_rectangle_rounded_lines(1735, 50, 180, 30, 0.2, 4, self.espBackGroundColor, 2)
                    pm.draw_text(espmark, 1810, 56, 20, Colors.whiteWatermark)
                    

                if self.config["triggerBot"]["enabled"]:
                    espmark = f"Trigger Bot"

                    pm.draw_rectangle_rounded(1735, 100, 180, 30, 0.2, 4, Colors.blackFade)
                    pm.draw_rectangle_rounded_lines(1735, 100, 180, 30, 0.2, 4, self.espBackGroundColor, 2)
                    pm.draw_text(espmark, 1760, 106, 20, Colors.whiteWatermark)

                if self.config["misc"]["GranadePoz"]:
                    espmark = f"Granade Preview"

                    pm.draw_rectangle_rounded(1735, 150, 180, 30, 0.2, 4, Colors.blackFade)
                    pm.draw_rectangle_rounded_lines(1735, 150, 180, 30, 0.2, 4, self.espBackGroundColor, 2)
                    pm.draw_text(espmark, 1740, 156, 20, Colors.whiteWatermark)

                if self.config["misc"]["noFlash"]:
                    espmark = f"No Flash"

                    pm.draw_rectangle_rounded(1735, 200, 180, 30, 0.2, 4, Colors.blackFade)
                    pm.draw_rectangle_rounded_lines(1735, 200, 180, 30, 0.2, 4, self.espBackGroundColor, 2)
                    pm.draw_text(espmark, 1780, 206, 20, Colors.whiteWatermark)

                if self.config["bhopio"]["bhop"]:
                    espmark = f"Bunny Hop"

                    pm.draw_rectangle_rounded(1735, 250, 180, 30, 0.2, 4, Colors.blackFade)
                    pm.draw_rectangle_rounded_lines(1735, 250, 180, 30, 0.2, 4, self.espBackGroundColor, 2)
                    pm.draw_text(espmark, 1775, 256, 20, Colors.whiteWatermark)
            
            if not self.config["esp"]["enabled"] and not self.config["misc"]["watermark"]:
                pm.end_drawing()
                pm.overlay_close()

                break
            elif not self.config["esp"]["enabled"]:
                pm.end_drawing()

                time.sleep(0.001)

                continue

            viewMatrix = pm.r_floats(self.proc, self.mod + Offsets.dwViewMatrix, 16)

            for ent in self.getEntities():
                try:
                    if (ent.isDormant or (self.config["esp"]["onlyEnemies"] and self.localTeam == ent.team) or ent.health == 0):
                        continue
                except:
                    pass
                    
                if self.config["esp"]["snapline"]:
                    try:
                        bounds, pos = pm.world_to_screen_noexc(viewMatrix, ent.bonePos(6), 1)

                        posx = pos["x"]
                        posy = pos["y"]

                        if not bounds:
                            posx = pm.get_screen_width() - posx
                            posy = pm.get_screen_height()

                        width = pm.get_screen_width() / 2
                        height = pm.get_screen_height() - 50

                        pm.draw_line(
                            width,
                            height,
                            posx,
                            posy,
                            self.espColor,
                        )
                    except:
                        pass

                if ent.wts(viewMatrix):
                    head = ent.pos2d["y"] - ent.headPos2d["y"]
                    width = head / 2
                    center = width / 2
                    xStart = ent.headPos2d["x"] - center
                    yStart = ent.headPos2d["y"] - center / 2

                    #m_entitySpottedState = 0x1698

                    #player = pm.r_int64(self.proc, self.mod + Offsets.dwLocalPlayerPawn)
                    #entityspotted = pm.r_bool(self.proc, player + (m_entitySpottedState + Offsets.m_bSpotted))

                    if self.config["esp"]["box"]:
                        #if self.config["esp"]["showvisible"]:
                            #if entityspotted == False:
                            #    pm.draw_rectangle_rounded_lines(
                            #        xStart,
                            #        yStart,
                            #        width,
                            #        head + center / 2,
                            #        self.config["esp"]["boxRounding"],
                            #        1,
                            #        pm.get_color("red"),
                            #        1.2,
                            #    )
                            #elif entityspotted == True:
                            #    pm.draw_rectangle_rounded_lines(
                            #        xStart,
                            #        yStart,
                            #        width,
                            #        head + center / 2,
                            #        self.config["esp"]["boxRounding"],
                            #        1,
                            #        self.espColor,
                            #        1.2,
                            #    )
                        #else:
                            pm.draw_rectangle_rounded_lines(
                                    xStart,
                                    yStart,
                                    width,
                                    head + center / 2,
                                    self.config["esp"]["boxRounding"],
                                    1,
                                    self.espColor,
                                    1.2,
                                )

                    if self.config["esp"]["boxBackground"]:
                        pm.draw_rectangle_rounded(
                            xStart,
                            yStart,
                            width,
                            head + center / 2,
                            self.config["esp"]["boxRounding"],
                            1,
                            self.espBackGroundColor,
                        )

                    if self.config["esp"]["ShowHead"]:
                        pm.draw_circle_sector_lines(
                            ent.headPos2d["x"],
                            ent.headPos2d["y"],
                            center / 3,
                            0,
                            360,
                            0,
                            Colors.white,
                        )

                    if self.config["esp"]["skeleton"]:
                        try:
                            cou = pm.world_to_screen(viewMatrix, ent.bonePos(5), 1)
                            shoulderR = pm.world_to_screen(viewMatrix, ent.bonePos(8), 1)
                            shoulderL = pm.world_to_screen(viewMatrix, ent.bonePos(13), 1)
                            brasR = pm.world_to_screen(viewMatrix, ent.bonePos(9), 1)
                            brasL = pm.world_to_screen(viewMatrix, ent.bonePos(14), 1)
                            handR = pm.world_to_screen(viewMatrix, ent.bonePos(11), 1)
                            handL = pm.world_to_screen(viewMatrix, ent.bonePos(16), 1)
                            waist = pm.world_to_screen(viewMatrix, ent.bonePos(0), 1)
                            kneesR = pm.world_to_screen(viewMatrix, ent.bonePos(23), 1)
                            kneesL = pm.world_to_screen(viewMatrix, ent.bonePos(26), 1)
                            feetR = pm.world_to_screen(viewMatrix, ent.bonePos(24), 1)
                            feetL = pm.world_to_screen(viewMatrix, ent.bonePos(27), 1)

                            pm.draw_line(cou["x"], cou["y"], shoulderR["x"], shoulderR["y"], Colors.white, 1)
                            pm.draw_line(cou["x"], cou["y"], shoulderL["x"], shoulderL["y"], Colors.white, 1)
                            pm.draw_line(brasL["x"], brasL["y"], shoulderL["x"], shoulderL["y"], Colors.white, 1)
                            pm.draw_line(brasR["x"], brasR["y"], shoulderR["x"], shoulderR["y"], Colors.white, 1)
                            pm.draw_line(brasR["x"], brasR["y"], handR["x"], handR["y"], Colors.white, 1)
                            pm.draw_line(brasL["x"], brasL["y"], handL["x"], handL["y"], Colors.white, 1)
                            pm.draw_line(cou["x"], cou["y"], waist["x"], waist["y"], Colors.white, 1)
                            pm.draw_line(kneesR["x"], kneesR["y"], waist["x"], waist["y"], Colors.white, 1)
                            pm.draw_line(kneesL["x"], kneesL["y"], waist["x"], waist["y"], Colors.white, 1)
                            pm.draw_line(kneesL["x"], kneesL["y"], feetL["x"], feetL["y"], Colors.white, 1)
                            pm.draw_line(kneesR["x"], kneesR["y"], feetR["x"], feetR["y"], Colors.white, 1)
                        except:
                            pass

                    if self.config["esp"]["health"]:
                        pm.draw_rectangle_rounded(
                            ent.headPos2d["x"] - center - 10,
                            ent.headPos2d["y"] - center / 2 + (head * 0 / 100),
                            3,
                            head + center / 2 - (head * 0 / 100),
                            self.config["esp"]["boxRounding"],
                            1,
                            self.espBackGroundColor,
                        )
                        pm.draw_text(f"{ent.health} HP", ent.headPos2d["x"] - center - 65, ent.headPos2d["y"] - center / 2 + (head * 0 / 100), 15, pm.get_color("white"))

                        pm.draw_rectangle_rounded(
                            ent.headPos2d["x"] - center - 10,
                            ent.headPos2d["y"] - center / 2 + (head * (100 - ent.health) / 100),
                            3,
                            head + center / 2 - (head * (100 - ent.health) / 100),
                            self.config["esp"]["boxRounding"],
                            1,
                            Colors.green,
                        )

                    if self.config["esp"]["name"]:
                        pm.draw_text(
                            ent.name,
                            ent.headPos2d["x"] - pm.measure_text(ent.name, 15) // 2,
                            ent.headPos2d["y"] - center / 2 - 15,
                            15,
                            Colors.white,
                        )

            pm.end_drawing()

        self.overlayThreadExists = False

    def triggerBot(self):
        while not hasattr(self, "focusedProcess"):
            time.sleep(0.1)

        while True:
            time.sleep(0.001)

            if not self.config["triggerBot"]["enabled"]: break

            if self.focusedProcess != "cs2.exe":
                time.sleep(1)
                
                continue

            if win32api.GetAsyncKeyState(self.config["triggerBot"]["bind"]) == 0: continue

            try:
                player = pm.r_int64(self.proc, self.mod + Offsets.dwLocalPlayerPawn)
                entityId = pm.r_int(self.proc, player + Offsets.m_iIDEntIndex)

                if entityId > 0:
                    entList = pm.r_int64(self.proc, self.mod + Offsets.dwEntityList)
                    entEntry = pm.r_int64(self.proc, entList + 0x8 * (entityId >> 9) + 0x10)
                    entity = pm.r_int64(self.proc, entEntry + 120 * (entityId & 0x1FF))

                    entityTeam = pm.r_int(self.proc, entity + Offsets.m_iTeamNum)
                    playerTeam = pm.r_int(self.proc, player + Offsets.m_iTeamNum)


                    if self.config["triggerBot"]["onlyEnemies"] and playerTeam == entityTeam: continue

                    entityHp = pm.r_int(self.proc, entity + Offsets.m_iHealth)

                    if entityHp > 0:
                        time.sleep(self.config["triggerBot"]["delay"])
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                        time.sleep(0.01)
                        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            except:
                pass
    

    def FOV(self):
        pm = Pymem('cs2.exe')
        value = int(self.config["FOV"]["FOVnum"])
        client = process.module_from_name(pm.process_handle, 'client.dll')
        #fov-resise
        dwLocalplayerController = pm.read_longlong(client.lpBaseOfDll + Offsets.dwLocalPlayerController) #главный оффсет для достпуа к второстепенным!
        #m_iDesiredFOV для работы этой хуеты
        pm.write_int(dwLocalplayerController + Offsets.m_iDesiredFOV, value) #второстепенный оффсет который прибавляется к главному, после запятой значение которое мы можем менять.

    def bhopio(self):
    #    pass
        pm = Pymem("cs2.exe")
        client = process.module_from_name(pm.process_handle, "client.dll")

        onGround = 65665
        onGround_with_ctrl = 65667

        LocalPlayer= pm.read_longlong(client.lpBaseOfDll + Offsets.dwLocalPlayerPawn)

        if self.config["bhopio"]["bhop"]:
                while True:
                    if not self.config["bhopio"]["bhop"]: break
                    ingroundcheck = pm.read_int(LocalPlayer + Offsets.m_fFlags)

                    #if space pressed we can do it
                    if keyboard.is_pressed("space"):
                        if ingroundcheck == onGround or ingroundcheck == onGround_with_ctrl:
                            keyboard.press_and_release("space")
                            time.sleep(0.03)

    def GranadePoz(self):
        #return
        patch = b'\x0f\x85'
        location = rb'\x0f\x84....\x8b\x05....\x48\x89\x74\x24.\xbe' 
        # 0f 84 ? ? ? ? 8b 05 ? ? ? ? 48 89 74 24 ? be

        pm = Pymem('cs2.exe') 

        client = process.module_from_name(pm.process_handle, 'client.dll')
        clientBytes = pm.read_bytes(client.lpBaseOfDll, client.SizeOfImage) 

        address = client.lpBaseOfDll + search(location, clientBytes).start()
        pm.write_bytes(address, patch, len(patch))
                
    #def noFlash(self):
    #    try:
    #        (flashAddress,) = pm.aob_scan_module(self.proc, pm.get_module(self.proc, "client.dll")["name"], "0f 83 ?? ?? ?? ?? 48 8b 1d ?? ?? ?? ?? 40 38 73")
    #    except:
    #        (flashAddress,) = pm.aob_scan_module(self.proc, pm.get_module(self.proc, "client.dll")["name"], "0f 82 ?? ?? ?? ?? 48 8b 1d ?? ?? ?? ?? 40 38 73")
    #    
    #    if self.config["misc"]["noFlash"]:
    #        pm.w_bytes(self.proc, flashAddress, b"\x0f\x82")
    #    else:
    #        pm.w_bytes(self.proc, flashAddress, b"\x0f\x83")

    def BombHelp(self):
        #dwPlantedC4 = 26376856
        #m_nBombSite = 3804
        #m_bBeingDefused = 3860
        #m_bBombDefused = 3884

        global bombplanted
        global bombdefuse
        global bombdefusecanorno

        bombplanted = "IF YOU SEE IT \nRESTART FUNCTION"
        bombdefuse = ""
        bombdefusecanorno = ""

        if self.config["misc"]["BombHelper"]:

            game_handle = Pymem("cs2.exe")
            client_dll = process.module_from_name(game_handle.process_handle, "client.dll").lpBaseOfDll
            then = None
            bomb_exploded = False

            while True:
                try:
                    cplantedc4 = game_handle.read_ulonglong(client_dll + Offsets.dwPlantedC4)
                    cplantedc4 = game_handle.read_ulonglong(cplantedc4)
                    planted = game_handle.read_bool(client_dll + Offsets.dwPlantedC4 - 0x8)
                    if planted:
                        if then == None:
                            then = datetime.datetime.now()
                        if int(40 - (datetime.datetime.now() - then).total_seconds()) < 0:
                            bomb_exploded = True
                        site = game_handle.read_int(cplantedc4 + Offsets.m_nBombSite)
                        beingdefused = game_handle.read_bool(cplantedc4 + Offsets.m_bBeingDefused)
                        defused = game_handle.read_bool(cplantedc4 + Offsets.m_bBombDefused)
                        if site > 0:
                            site = "B"
                        else:
                            site = "A"
                        if not bomb_exploded:
                            if int(40 - (datetime.datetime.now() - then).total_seconds()) < 5:
                                bombplanted = (f"Bomb cannot be defused!\nTime Left: {int(40 - (datetime.datetime.now() - then).total_seconds())}s")
                            elif int(40 - (datetime.datetime.now() - then).total_seconds()) < 10:
                                bombplanted = (f"Bomb can be defused with kit!\nTime Left: {int(40 - (datetime.datetime.now() - then).total_seconds())}s")
                            elif not defused:
                                bombplanted = (f"Bomb planted on: {site}\nDefusing: {beingdefused}\nTime Left: {int(40 - (datetime.datetime.now() - then).total_seconds())}s")
                            else:
                                then = None
                                bombdefuse = ("Bomb Defused!")
                        else:
                            bombdefuse = ("Bomb Exploded!")
                    else:
                        then = None
                        bomb_exploded = False
                        bombplanted = ("Bomb not planted!")

                    time.sleep(1)
                    bombplanted = ""
                    bombdefuse = ""
                    bombdefusecanorno = ""

                except KeyboardInterrupt:
                    break
                except:
                    break

                if not self.config["misc"]["BombHelper"]: 
                    break
                if self.config["misc"]["BombHelper"]:
                    continue
        else:
            pass

if __name__ == "__main__":
    if os.name != "nt":
        input("Owl-Legit is only working on Windows.")

        os._exit(0)

    panosdiosClass = panosdios()

    #win32gui.ShowWindow(win32console.GetConsoleWindow(), win32con.SW_HIDE)

    uiWidth = 800
    uiHeight = 500

    dpg.create_context()

    def toggleEsp(id, value):
        panosdiosClass.config["esp"]["enabled"] = value

        if value and not panosdiosClass.overlayThreadExists:
            threading.Thread(target=panosdiosClass.esp, daemon=True).start()
    
    waitingForKeyEsp = False
    def statusBindEsp(id):
        global waitingForKeyEsp

        if not waitingForKeyEsp:
            with dpg.handler_registry(tag="Esp Bind Handler"):
                dpg.add_key_press_handler(callback=setBindEsp)

            dpg.set_item_label(buttonBindEsp, "...")

            waitingForKeyEsp = True

    def setBindEsp(id, value):
        global waitingForKeyEsp

        if waitingForKeyEsp:
            panosdiosClass.config["esp"]["bind"] = value

            dpg.set_item_label(buttonBindEsp, f"Bind: {chr(value)}")
            dpg.delete_item("Esp Bind Handler")

            waitingForKeyEsp = False

    def toggleEspBox(id, value):
        panosdiosClass.config["esp"]["box"] = value

    def toggleEspBoxBackground(id, value):
        panosdiosClass.config["esp"]["boxBackground"] = value

    def toggleEspShowVsible(id, value):
        panosdiosClass.config["esp"]["showvisible"] = value

    def toggleEspSkeleton(id, value):
        panosdiosClass.config["esp"]["skeleton"] = value

    def toggleEspShowHead(id, value):
        panosdiosClass.config["esp"]["ShowHead"] = value

    def toggleEspSnapline(id, value):
        panosdiosClass.config["esp"]["snapline"] = value

    def toggleEspOnlyEnemies(id, value):
        panosdiosClass.config["esp"]["onlyEnemies"] = value

    def toggleEspName(id, value):
        panosdiosClass.config["esp"]["name"] = value

    def toggleEspHealth(id, value):
        panosdiosClass.config["esp"]["health"] = value

    def setEspColor(id, value):
        panosdiosClass.config["esp"]["color"] = {"r": value[0], "g": value[1], "b": value[2], "a": value[3]}

        panosdiosClass.espColor = pm.new_color_float(value[0], value[1], value[2], value[3])
        panosdiosClass.espBackGroundColor = pm.fade_color(panosdiosClass.espColor, 0.3)

    def setEspBoxRounding(id, value):
        panosdiosClass.config["esp"]["boxRounding"] = value

    def toggleTriggerBot(id, value):
        panosdiosClass.config["triggerBot"]["enabled"] = value

        if value:
            threading.Thread(target=panosdiosClass.triggerBot, daemon=True).start()
    
    waitingForKeyTriggerBot = False
    def statusBindTriggerBot(id):
        global waitingForKeyTriggerBot

        if not waitingForKeyTriggerBot:
            with dpg.handler_registry(tag="TriggerBot Bind Handler"):
                dpg.add_key_press_handler(callback=setBindTriggerBot)

            dpg.set_item_label(buttonBindTriggerBot, "...")

            waitingForKeyTriggerBot = True

    def setBindTriggerBot(id, value):
        global waitingForKeyTriggerBot

        if waitingForKeyTriggerBot:
            panosdiosClass.config["triggerBot"]["bind"] = value

            dpg.set_item_label(buttonBindTriggerBot, f"Bind: {chr(value)}")
            dpg.delete_item("TriggerBot Bind Handler")

            waitingForKeyTriggerBot = False

    def toggleTriggerBotOnlyEnemies(id, value):
        panosdiosClass.config["triggerBot"]["onlyEnemies"] = value

    def toggleFOVchange(id, value):
        panosdiosClass.config["FOV"]["enabled"] = value

        if value:
            threading.Thread(target=panosdiosClass.FOV, daemon=True).start() 

    def sliderTriggerBotDelay(id, value):
        panosdiosClass.config["triggerBot"]["delay"] = value

    def sliderFOVchange(id, value):
        panosdiosClass.config["FOV"]["FOVnum"] = value

    def toggleBunnyHop(id, value):
        panosdiosClass.config["misc"]["GranadePoz"] = value       

        if value:
            threading.Thread(target=panosdiosClass.GranadePoz, daemon=True).start()

    def togglebhopio(id, value):
        panosdiosClass.config["bhopio"]["bhop"] = value

        if value:
            threading.Thread(target=panosdiosClass.bhopio, daemon=True).start()
            
    def toggleNoFlash(id, value):
        panosdiosClass.config["misc"]["noFlash"] = value       

        panosdiosClass.noFlash()

    def ToggleBombHelper(id, value):
        panosdiosClass.config["misc"]["BombHelper"] = value 

        if value:
            threading.Thread(target=panosdiosClass.BombHelp, daemon=True).start()

    def toggleWatermark(id, value):
        panosdiosClass.config["misc"]["watermark"] = value    

        if value and not panosdiosClass.overlayThreadExists:
            threading.Thread(target=panosdiosClass.esp, daemon=True).start()

    def toggleSaveSettings(id, value):
        panosdiosClass.config["settings"]["saveSettings"] = value

    def toggleStreamProof(id, value):
        panosdiosClass.config["settings"]["streamProof"] = value   

        if value:
            user32.SetWindowDisplayAffinity(panosdiosClass.guiWindowHandle, 0x00000011)
            user32.SetWindowDisplayAffinity(panosdiosClass.overlayWindowHandle, 0x00000011)
        else:
            user32.SetWindowDisplayAffinity(panosdiosClass.guiWindowHandle, 0x00000000)
            user32.SetWindowDisplayAffinity(panosdiosClass.overlayWindowHandle, 0x00000000)

    def toggleAlwaysOnTop(id, value):
        if value:
            win32gui.SetWindowPos(panosdiosClass.guiWindowHandle, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        else:
            win32gui.SetWindowPos(panosdiosClass.guiWindowHandle, win32con.HWND_NOTOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

    def PANIC(id, value):
        os._exit(os.EX_OK)
            
    #mainwindow
    with dpg.window(label=title, width=uiWidth, height=uiHeight, no_collapse=True, no_move=True, no_resize=True, on_close=lambda: os._exit(0)) as window:
        #maintabbar
        with dpg.tab_bar():
            #esp
            with dpg.tab(label="ESP"):
                dpg.add_spacer(width=75)

                with dpg.group(horizontal=True):
                    checkboxToggleEsp = dpg.add_checkbox(label="Toggle", default_value=panosdiosClass.config["esp"]["enabled"], callback=toggleEsp)
                    buttonBindEsp = dpg.add_button(label="Click to Bind", callback=statusBindEsp)

                    bind = panosdiosClass.config["esp"]["bind"]
                    if bind != 0:
                        dpg.set_item_label(buttonBindEsp, f"Bind: {chr(bind)}")

                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                with dpg.group(horizontal=True):
                    checkboxEspBox= dpg.add_checkbox(label="Box", default_value=panosdiosClass.config["esp"]["box"], callback=toggleEspBox)
                    #checkboxEspBoxVisible= dpg.add_checkbox(label="Show visible", default_value=panosdiosClass.config["esp"]["showvisible"], callback=toggleEspShowVsible)
                    checkboxEspBackground = dpg.add_checkbox(label="Background", default_value=panosdiosClass.config["esp"]["boxBackground"], callback=toggleEspBoxBackground)

                with dpg.group(horizontal=True):
                    checkboxEspSkeleton= dpg.add_checkbox(label="Skeleton", default_value=panosdiosClass.config["esp"]["skeleton"], callback=toggleEspSkeleton)
                    checkboxEspSkeleton= dpg.add_checkbox(label="Show Head", default_value=panosdiosClass.config["esp"]["ShowHead"], callback=toggleEspShowHead)

                checkboxEspSnapline= dpg.add_checkbox(label="Snapline", default_value=panosdiosClass.config["esp"]["snapline"], callback=toggleEspSnapline)
                checkboxEspOnlyEnemies = dpg.add_checkbox(label="Only Enemies", default_value=panosdiosClass.config["esp"]["onlyEnemies"], callback=toggleEspOnlyEnemies)
                checkboxEspName = dpg.add_checkbox(label="Show Name", default_value=panosdiosClass.config["esp"]["name"], callback=toggleEspName)
                checkboxEspHealth = dpg.add_checkbox(label="Show Health", default_value=panosdiosClass.config["esp"]["health"], callback=toggleEspHealth)

                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                colorPickerEsp = dpg.add_color_picker(label="Global Color", default_value=(panosdiosClass.config["esp"]["color"]["r"]*255, panosdiosClass.config["esp"]["color"]["g"]*255, panosdiosClass.config["esp"]["color"]["b"]*255, panosdiosClass.config["esp"]["color"]["a"]*255), width=150, no_inputs=True, callback=setEspColor)
                sliderEspBoxRounding = dpg.add_slider_float(label="Box Rounding", default_value=panosdiosClass.config["esp"]["boxRounding"], min_value=0, max_value=1, clamped=True, format="%.1f", callback=setEspBoxRounding, width=250)
            
            #triggerbot
            with dpg.tab(label="TriggerBot"):
                dpg.add_spacer(width=75)

                with dpg.group(horizontal=True):
                    checkboxToggleTriggerBot = dpg.add_checkbox(label="Toggle", default_value=panosdiosClass.config["triggerBot"]["enabled"], callback=toggleTriggerBot)
                    buttonBindTriggerBot = dpg.add_button(label="Click to Bind", callback=statusBindTriggerBot)
                    bind = panosdiosClass.config["triggerBot"]["bind"]
                    if bind != 0:
                        dpg.set_item_label(buttonBindTriggerBot, f"Bind: {chr(bind)}")   

                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                checkboxTriggerBotOnlyEnemies = dpg.add_checkbox(label="Only Enemies", default_value=panosdiosClass.config["triggerBot"]["onlyEnemies"], callback=toggleTriggerBotOnlyEnemies)
                
                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                sliderDelayTriggerBot = dpg.add_slider_float(label="Shot Delay", default_value=panosdiosClass.config["triggerBot"]["delay"], max_value=1, callback=sliderTriggerBotDelay, width=250, clamped=True, format="%.1f")
            
            #misc
            with dpg.tab(label="Misc"):
                dpg.add_spacer(width=75)

                checkboxBombBot = dpg.add_checkbox(label="Bomb Helper", default_value=panosdiosClass.config["misc"]["BombHelper"], callback = ToggleBombHelper)
                checkboxWatermark = dpg.add_checkbox(label="Watermark", default_value=panosdiosClass.config["misc"]["watermark"], callback=toggleWatermark)

                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                with dpg.group(horizontal=True):
                    checkboxbhopio = dpg.add_checkbox(label="Bunny Hop", default_value=panosdiosClass.config["bhopio"]["bhop"], callback=togglebhopio)
                    dpg.add_text(default_value="/ press and hold SPACE!*")
                
                dpg.add_spacer(width=75)

                dpg.add_text(default_value='''*in order for bunny hop to work,\nyou must enter the following commands\ninto the console (to open the console, press ~):\nalias bhpa "+jump;-jump"\nbind space bhpa\nbind app bhpa''')
            
            #all detected function
            with dpg.tab(label="Detected"):
                dpg.add_spacer(width=75)
                
                #with dpg.group(horizontal=True):
                #    checkboxNoFlash = dpg.add_checkbox(label="NoFlash", default_value=panosdiosClass.config["misc"]["noFlash"], callback=toggleNoFlash)
                #    dpg.add_text(default_value="/ DETECTED*")

                with dpg.group(horizontal=True):
                    checkboxGranadePoz = dpg.add_checkbox(label="Granade Preview", default_value=panosdiosClass.config["misc"]["GranadePoz"], callback=toggleBunnyHop)
                    dpg.add_text(default_value="/ DETECTED*")

                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                with dpg.group(horizontal=True):
                    checkboxToggleTriggerBot = dpg.add_checkbox(label="Toggle", default_value=panosdiosClass.config["FOV"]["enabled"], callback=toggleFOVchange)
                    dpg.add_text(default_value="/ DETECTED*")

                sliderfov = dpg.add_slider_float(label="Shot Delay", default_value=panosdiosClass.config["FOV"]["FOVnum"],min_value= 50, max_value=170, callback=sliderFOVchange, width=250, clamped=True, format="%.1f")

                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                dpg.add_text(default_value='''*if you used these functions accidentally, THEN RESTART THE GAME IMMEDIATELY!!!''')
            #settings
            with dpg.tab(label="Settings"):
                dpg.add_spacer(width=75)

                checkboxSaveSettings = dpg.add_checkbox(label="Save Settings", default_value=panosdiosClass.config["settings"]["saveSettings"], callback=toggleSaveSettings)

                dpg.add_spacer(width=75)

                checkboxStreamProof = dpg.add_checkbox(label="Stream Proof", default_value=panosdiosClass.config["settings"]["streamProof"], callback=toggleStreamProof)
                checkboxAlwaysOnTop = dpg.add_checkbox(label="Always On Top", callback=toggleAlwaysOnTop)

                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                buttonPANIC = dpg.add_button(label="PANIC", callback=PANIC)

                dpg.add_spacer(width=75)
                dpg.add_separator()
                dpg.add_spacer(width=75)

                MadeByText = dpg.add_text(default_value="Made by Sov")
                WithText = dpg.add_text(default_value="-with love")
                SpaceText = dpg.add_text(default_value="")
                YouTubeText = dpg.add_text(default_value="YouTube @sov2020")
                SpaceText2 = dpg.add_text(default_value="")
                SpaceText3 = dpg.add_text(default_value="-------------------------------------------------------------------------")
                WhereCFGText = dpg.add_text(default_value="Ur config locate: C:\\users\\urusername\\AppData\\Local\\temp\\owllegit")
                SpaceText4 = dpg.add_text(default_value="-------------------------------------------------------------------------")

    def dragViewport(sender, appData, userData):
        if dpg.get_mouse_pos(local=False)[1] <= 40:
            dragDeltas = appData
            viewportPos = dpg.get_viewport_pos()
            newX = viewportPos[0] + dragDeltas[1]
            newY = max(viewportPos[1] + dragDeltas[2], 0)

            dpg.set_viewport_pos([newX, newY])

    with dpg.handler_registry():
        dpg.add_mouse_drag_handler(button=0, threshold=0.0, callback=dragViewport)

    with dpg.theme() as globalTheme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (21, 19, 21, 255))

            #title
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, (21, 19, 21, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, (77, 171, 59, 255))

            #checkmark
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, (255, 255, 255, 255))
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (34, 33, 34, 255))

            #text
            dpg.add_theme_color(dpg.mvThemeCol_Text, (225, 225, 225, 255))

            #tab
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, (77, 171, 59, 255))
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (34, 33, 34, 255))

            #slider
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, (77, 171, 59, 255))
            dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, (77, 171, 59, 255))

            #tab
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, (34, 33, 34, 255))

            #allhovered
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (34, 33, 34, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (34, 33, 34, 255))

            dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 3)

    dpg.bind_theme(globalTheme)

    dpg.create_viewport(title=title, width=uiWidth, height=uiHeight, decorated=False, resizable=False)
    dpg.show_viewport()
    
    panosdiosClass.guiWindowHandle = win32gui.FindWindow(title, None)
    if panosdiosClass.config["settings"]["streamProof"]:
        user32.SetWindowDisplayAffinity(panosdiosClass.guiWindowHandle, 0x00000011)

    
    #debug
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    dpg.setup_dearpygui()
    dpg.start_dearpygui()