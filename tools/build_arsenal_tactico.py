"""Genera los scripts de Arsenal Táctico a partir de una tabla: ítems, cargadores, partes, modelos,
traducciones y botín. Las armas parten de los bloques vanilla de 42.18 (scripts/generated/items/*.txt:
AssaultRifle, Pistol, L94_Rifle, 556Clip, 9mmClip, x4Scope, x8Scope, RedDot, GunLight) y solo cambian
lo propio de cada una. Los attachments de los modelos salen de art/<ID>/attachments.json
(tools/blender/gunkit.export). Uso: python3 tools/build_arsenal_tactico.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "Contents/mods/ArsenalTactico/42"
MEDIA = MOD / "media"
ART = ROOT / "art"

# --------------------------------------------------------------- bases vanilla (42.18)
RIFLE = """DisplayCategory = Weapon
ItemType = base:weapon
AimingPerkCritModifier = 6
AimingPerkHitChanceModifier = 4
AimingPerkMinAngleModifier = 0.01
AimingPerkRangeModifier = 0
AimReleaseSound = M16AimRelease
Aimingtime = 40
AmmoBox = Base.556Box
AmmoType = base:bullets_556
AttachmentType = Rifle
BreakSound = M16Break
BringToBearSound = M16BringToBear
ClickSound = M16Jam
ConditionLowerChanceOneIn = 200
ConditionMax = 10
CritDmgMultiplier = 4.0
CriticalChance = 20.0
DoorDamage = 5
DropSound = M16Drop
EjectAmmoSound = M16EjectAmmo
EjectAmmoStartSound = M16EjectAmmoStart
EjectAmmoStopSound = M16EjectAmmoStop
EquipSound = M16Equip
FireMode = Auto
FireModePossibilities = Auto/Single
CyclicRateMultiplier = 1.0
HitChance = 50
HitSound = BulletImpact
IdleAnim = Idle_Weapon2
ImpactSound = null
InsertAmmoSound = M16InsertAmmo
InsertAmmoStartSound = M16InsertAmmoStart
InsertAmmoStopSound = M16InsertAmmoStop
IsAimedFirearm = true
JamGunChance = 1
KnockBackOnNoDeath = true
KnockdownMod = 4.0
MaxAmmo = 30
MaxDamage = 1.6
MaxHitcount = 2
MaxRange = 30.0
MinSightRange = 2
MaxSightRange = 10.0
MetalValue = 45.0
MinAngle = 0.965
MinDamage = 1.0
MinRange = 0.61
MinimumSwingtime = 0.5
MultipleHitConditionAffected = false
MuzzleFlashModelKey = muzzle_flash_assault_rifle
NPCSoundBoost = 1.5
PiercingBullets = true
Projectilecount = 1
PushBackMod = 0.3
RackSound = M16Rack
Ranged = true
RecoilDelay = 15
Reloadtime = 25
RequiresEquippedBothHands = true
RunAnim = Run_Weapon2
ShellFallSound = M16CartridgeFall
SoundGain = 2.0
SoundRadius = 150
SoundVolume = 35
SplatBloodOnNoDeath = true
SplatNumber = 3
SplatSize = 3
StopPower = 2.0
SubCategory = Firearm
SwingAmountBeforeImpact = 0.0
SwingAnim = Rifle
SwingSound = M16Shoot
Swingtime = 0.5
ToHitModifier = 1.5
TwoHandWeapon = true
UnequipSound = M16UnEquip
UseEndurance = false
WeaponReloadType = boltaction
Tags = base:hasmetal;base:firearm"""

PISTOL = """DisplayCategory = Weapon
ItemType = base:weapon
AimingPerkCritModifier = 6
AimingPerkHitChanceModifier = 4
AimingPerkMinAngleModifier = 0.05
AimingPerkRangeModifier = 0
AimReleaseSound = M9AimRelease
Aimingtime = 25
AmmoBox = Base.Bullets9mmBox
AmmoType = base:bullets_9mm
AttachmentType = Holster
BreakSound = M9Break
BringToBearSound = M9BringToBear
ClickSound = M9Jam
ClipSize = 15
ConditionLowerChanceOneIn = 200
ConditionMax = 10
CritDmgMultiplier = 4.0
CriticalChance = 20.0
DoorDamage = 5
DropSound = M9Drop
EjectAmmoSound = M9EjectAmmo
EjectAmmoStartSound = M9EjectAmmoStart
EjectAmmoStopSound = M9EjectAmmoStop
EquipSound = M9Equip
HitChance = 50
HitSound = BulletImpact
ImpactSound = null
InsertAmmoSound = M9InsertAmmo
InsertAmmoStartSound = M9InsertAmmoStart
InsertAmmoStopSound = M9InsertAmmoStop
IsAimedFirearm = true
JamGunChance = 1
KnockBackOnNoDeath = true
KnockdownMod = 2.0
MaxAmmo = 15
MaxDamage = 1.0
MaxHitcount = 1
MaxRange = 15.0
MinSightRange = 2
MaxSightRange = 6.0
MetalValue = 30.0
MinAngle = 0.95
MinDamage = 0.6
MinRange = 0.61
MinimumSwingtime = 0.5
MultipleHitConditionAffected = false
MuzzleFlashModelKey = muzzle_flash_handgun
NPCSoundBoost = 1.5
Projectilecount = 1
PushBackMod = 0.3
RackSound = M9Rack
Ranged = true
RecoilDelay = 12
Reloadtime = 30
RunAnim = Run_Weapon2
ShellFallSound = M9CartridgeFall
SoundGain = 1.5
SoundRadius = 100
SoundVolume = 30
SplatBloodOnNoDeath = true
SplatNumber = 3
SplatSize = 3
StopPower = 5.0
SubCategory = Firearm
SwingAmountBeforeImpact = 0.0
SwingAnim = Handgun
SwingSound = M9Shoot
Swingtime = 0.5
ToHitModifier = 1.5
UnequipSound = M9UnEquip
UseEndurance = false
WeaponReloadType = handgun
Tags = base:hasmetal;base:firearm"""

LEVER = """DisplayCategory = Weapon
ItemType = base:weapon
AimingPerkCritModifier = 6
AimingPerkHitChanceModifier = 4
AimingPerkMinAngleModifier = 0.01
AimingPerkRangeModifier = 0
AimReleaseSound = L94AimRelease
Aimingtime = 40
AmmoBox = Base.3030Box
AmmoType = base:bullets_3030
AttachmentType = Rifle
BreakSound = L94Break
BringToBearSound = L94BringToBear
ClickSound = L94Jam
ConditionLowerChanceOneIn = 200
ConditionMax = 10
CritDmgMultiplier = 4.0
CriticalChance = 25.0
DoorDamage = 5
DropSound = L94Drop
EjectAmmoSound = L94EjectAmmo
EjectAmmoStartSound = L94EjectAmmoStart
EjectAmmoStopSound = L94EjectAmmoStop
EquipSound = L94Equip
FireMode = Single
HitChance = 50
HitSound = BulletImpact
IdleAnim = Idle_Weapon2
ImpactSound = null
InsertAmmoSound = L94InsertAmmo
InsertAmmoStartSound = L94InsertAmmoStart
InsertAmmoStopSound = L94InsertAmmoStop
IsAimedFirearm = true
JamGunChance = 1
KnockBackOnNoDeath = true
KnockdownMod = 2.0
MaxAmmo = 6
MaxDamage = 2.0
MaxHitcount = 1
MaxRange = 30.0
MinSightRange = 2
MaxSightRange = 10.0
MetalValue = 45.0
MinAngle = 0.95
MinDamage = 1.2
MinRange = 0.61
MinimumSwingtime = 0.5
MultipleHitConditionAffected = false
MuzzleFlashModelKey = muzzle_flash_hunting_rifle
NPCSoundBoost = 1.5
PiercingBullets = true
Projectilecount = 1
PushBackMod = 0.3
RackAfterShoot = true
RackSound = L94Rack
Ranged = true
RecoilDelay = 20
Reloadtime = 25
RequiresEquippedBothHands = true
RunAnim = Run_Weapon2
ShellFallSound = L94CartridgeFall
SoundGain = 2.0
SoundRadius = 160
SoundVolume = 200
SplatBloodOnNoDeath = true
SplatNumber = 3
SplatSize = 3
StopPower = 16.0
SubCategory = Firearm
SwingAmountBeforeImpact = 0.0
SwingAnim = Rifle
SwingSound = L94Shoot
Swingtime = 0.5
ToHitModifier = 1.5
TwoHandWeapon = true
UnequipSound = L94UnEquip
UseEndurance = false
WeaponReloadType = leveraction
Tags = base:hasmetal;base:firearm"""

MAG = """DisplayCategory = Ammo
ItemType = base:normal
Weight = 0.2
CanStack = false
StaticModel = GunMagazine
Tags = base:hasmetal;{tag}"""

SCOPE = """DisplayCategory = WeaponPart
ItemType = base:weaponpart
PartType = Scope
Tooltip = Tooltip_Scope
Tags = base:optics
MetalValue = 22.0
CanAttach = ItemCodeOnTest.hasScrewdriver
CanDetach = ItemCodeOnTest.hasScrewdriver"""

REDDOT = """DisplayCategory = WeaponPart
ItemType = base:weaponpart
PartType = Scope
Tooltip = Tooltip_RedDot
Tags = base:optics
MetalValue = 15.0
CanAttach = ItemCodeOnTest.hasScrewdriver
CanDetach = ItemCodeOnTest.hasScrewdriver"""

LIGHT = """DisplayCategory = WeaponPart
ItemType = base:weaponpart
PartType = Canon
MetalValue = 10.0
ActivatedItem = true
TorchCone = true
TorchDot = 0.66
SoundMap = Activate FlashlightOn
SoundMap = Deactivate FlashlightOff
primaryAnimMask = HoldingTorchRight
secondaryAnimMask = HoldingTorchLeft
DisappearOnUse = false
UseDelta = 0.001
Tags = base:flashlight;base:usesbattery
CanAttach = ItemCodeOnTest.hasScrewdriver
CanDetach = ItemCodeOnTest.hasScrewdriver"""

# --------------------------------------------------------------- variantes (sobre las bases vanilla)
P45 = {  # Pistol2 (M1911) de 42.18: .45
    "AimReleaseSound": "M1911AimRelease", "AmmoBox": "Base.Bullets45Box", "AmmoType": "base:bullets_45",
    "BreakSound": "M1911Break", "BringToBearSound": "M1911BringToBear", "ClickSound": "M1911Jam",
    "DropSound": "M1911Drop", "EjectAmmoSound": "M1911EjectAmmo", "EjectAmmoStartSound": "M1911EjectAmmoStart",
    "EjectAmmoStopSound": "M1911EjectAmmoStop", "EquipSound": "M1911Equip", "InsertAmmoSound": "M1911InsertAmmo",
    "InsertAmmoStartSound": "M1911InsertAmmoStart", "InsertAmmoStopSound": "M1911InsertAmmoStop",
    "MuzzleFlashModelKey": "muzzle_flash_handgun02", "RackSound": "M1911Rack", "ShellFallSound": "M1911CartridgeFall",
    "SwingSound": "M1911Shoot", "UnequipSound": "M1911UnEquip", "StopPower": "7.0", "MaxDamage": "1.2",
    "MinDamage": "0.9", "SoundRadius": "70", "SoundVolume": "50"}
R308 = {  # AssaultRifle2 (M14) de 42.18: .308
    "AimReleaseSound": "M14AimRelease", "AmmoBox": "Base.308Box", "AmmoType": "base:bullets_308",
    "BreakSound": "M14Break", "BringToBearSound": "M14BringToBear", "ClickSound": "M14Jam", "DropSound": "M14Drop",
    "EjectAmmoSound": "M14EjectAmmo", "EjectAmmoStartSound": "M14EjectAmmoStart",
    "EjectAmmoStopSound": "M14EjectAmmoStop", "EquipSound": "M14Equip", "InsertAmmoSound": "M14InsertAmmo",
    "InsertAmmoStartSound": "M14InsertAmmoStart", "InsertAmmoStopSound": "M14InsertAmmoStop",
    "MuzzleFlashModelKey": "muzzle_flash_assault_rifle02", "RackSound": "M14Rack", "ShellFallSound": "M14CartridgeFall",
    "SwingSound": "M14Shoot", "UnequipSound": "M14UnEquip", "CriticalChance": "30.0", "MaxDamage": "2.0",
    "MinDamage": "1.2", "MaxHitcount": "1", "SoundRadius": "170", "MaxRange": "38.0", "RecoilDelay": "20"}
SMG = {  # PDW compactas: base de pistola en automático, a dos manos
    "FireMode": "Auto", "FireModePossibilities": "Auto/Single", "TwoHandWeapon": "true",
    "RequiresEquippedBothHands": "true", "CyclicRateMultiplier": "1.0", "MaxHitcount": "1"}
AGL = {  # lanzagranadas de tambor: carga de a una (recarga de escopeta); la explosión la hace la Lua
    "AimReleaseSound": "JS2000ShotgunAimRelease", "AmmoBox": None, "AmmoType": "arsenaltactico:granada_40mm",
    "BreakSound": "JS2000ShotgunBreak", "BringToBearSound": "JS2000ShotgunBringToBear",
    "ClickSound": "JS2000ShotgunJam", "DropSound": "JS2000ShotgunDrop", "EjectAmmoSound": "JS2000ShotgunEjectAmmo",
    "EjectAmmoStartSound": "JS2000ShotgunEjectAmmoStart", "EjectAmmoStopSound": "JS2000ShotgunEjectAmmoStop",
    "EquipSound": "JS2000ShotgunEquip", "InsertAmmoSound": "JS2000ShotgunInsertAmmo",
    "InsertAmmoStartSound": "JS2000ShotgunInsertAmmoStart", "InsertAmmoStopSound": "JS2000ShotgunInsertAmmoStop",
    "RackSound": "JS2000ShotgunRack", "ShellFallSound": None, "SwingSound": "JS2000ShotgunShoot",
    "UnequipSound": "JS2000ShotgunUnEquip", "MuzzleFlashModelKey": "muzzle_flash_shotgun", "FireMode": "Single",
    "FireModePossibilities": None, "CyclicRateMultiplier": None, "PiercingBullets": None,
    "WeaponReloadType": "shotgun", "MaxAmmo": "6", "MaxDamage": "4.0", "MinDamage": "3.0", "MaxHitcount": "1",
    "KnockdownMod": "8.0", "StopPower": "20.0", "MaxRange": "24.0", "RecoilDelay": "45", "Reloadtime": "35",
    "SoundRadius": "120", "SoundVolume": "60", "Weight": "5.2", "Aimingtime": "45", "MetalValue": "50.0",
    "ConditionLowerChanceOneIn": "80"}
GRENADE = """DisplayCategory = Ammo
ItemType = base:normal
Weight = 0.23
MetalValue = 3.0
Tags = base:ammo"""
CHARGE = """DisplayCategory = Explosives
ItemType = base:weapon
Weight = 0.23
ExplosionPower = 80
ExplosionRange = 4
ExplosionSound = PipeBombExplode
FireStartingEnergy = 0
FireStartingChance = 0
MaxDamage = 0.0
MaxHitcount = 0
MaxRange = 1.0
MinDamage = 0.0
SwingAnim = Throw
ConditionMax = 1"""


def gun(base, extra, **over):
    return (base, dict(extra, **over))


# --------------------------------------------------------------- tabla del mod
RIFLES = ["AT_M4", "AT_MCX", "AT_AK101", "AT_Marlin336", "AT_MX4", "AT_AUGA5", "AT_AG203", "AT_Komodo",
          "AT_RPK101", "AT_PSR", "AT_CycloneAGL"]
PDWS = ["AT_FNSAR", "AT_QDX99"]
PISTOLS = ["AT_G19", "AT_GXP", "AT_MD34", "AT_GravRecon", "AT_VikorS1", "AT_FNPR"]
ALL_GUNS = RIFLES + PDWS + PISTOLS
OPTICS = ["AT_ACOG", "AT_LPVO", "AT_HoloSight", "AT_Thermal"]
OPTIC_GUNS = [g for g in RIFLES if g != "AT_PSR"] + PDWS     # la PSR trae su mira fija


def parts_lines(gun):
    lines = [f"ModelWeaponPart = Base.{p} {p} at_optic at_optic" for p in OPTICS if gun in OPTIC_GUNS]
    return lines + ["ModelWeaponPart = Base.AT_TacLight AT_TacLight at_light at_light"]


GUNS = {
    "AT_M4": (RIFLE, {"Weight": "3.3", "Aimingtime": "35", "MagazineType": "Base.AT_SkullMag", "RecoilDelay": "14",
                      "MetalValue": "40.0"}),
    "AT_MCX": (RIFLE, {"Weight": "3.0", "Aimingtime": "30", "MaxRange": "26.0", "MinDamage": "0.95",
                       "MaxDamage": "1.5", "RecoilDelay": "13", "SoundRadius": "140", "MagazineType": "Base.AT_LancerMag",
                       "MetalValue": "38.0"}),
    "AT_AK101": (RIFLE, {"Weight": "3.4", "Aimingtime": "38", "MaxRange": "28.0", "MaxDamage": "1.7",
                         "CriticalChance": "18.0", "RecoilDelay": "17", "MagazineType": "Base.AT_AKMag",
                         "MetalValue": "42.0"}),
    "AT_Marlin336": (LEVER, {"Weight": "3.3", "MaxRange": "32.0", "Aimingtime": "38", "MetalValue": "40.0"}),
    "AT_G19": (PISTOL, {"Weight": "0.9", "Aimingtime": "22", "MaxRange": "14.0", "RecoilDelay": "11",
                        "MagazineType": "Base.AT_G19Mag", "MetalValue": "22.0"}),
    # --- lámina conceptual
    "AT_GXP": (PISTOL, {"Weight": "1.0", "Aimingtime": "24", "MaxRange": "16.0", "MaxAmmo": "17", "ClipSize": "17",
                        "RecoilDelay": "10", "MagazineType": "Base.AT_GXPMag", "MetalValue": "24.0"}),
    "AT_MD34": gun(PISTOL, P45, Weight="1.2", Aimingtime="26", MaxAmmo="8", ClipSize="8", MaxRange="13.0",
                   MagazineType="Base.AT_MD34Mag", MetalValue="28.0"),
    "AT_GravRecon": (PISTOL, {"Weight": "1.0", "Aimingtime": "22", "MaxRange": "15.0", "MaxAmmo": "17",
                              "ClipSize": "17", "MagazineType": "Base.AT_GravMag", "MetalValue": "24.0"}),
    "AT_VikorS1": (PISTOL, {"Weight": "1.0", "Aimingtime": "24", "MaxRange": "14.0", "MaxAmmo": "18",
                            "ClipSize": "18", "MaxDamage": "1.05", "MagazineType": "Base.AT_VikorMag",
                            "MetalValue": "24.0"}),
    "AT_FNPR": gun(PISTOL, P45, Weight="1.6", Aimingtime="28", MaxAmmo="15", ClipSize="15", MaxRange="15.0",
                   SoundRadius="25", SoundVolume="12", MagazineType="Base.AT_FNPRMag", MetalValue="30.0"),
    "AT_FNSAR": gun(PISTOL, SMG, Weight="2.8", Aimingtime="30", MaxAmmo="50", ClipSize="50", MaxRange="18.0",
                    MinDamage="0.6", MaxDamage="1.0", RecoilDelay="7", SoundRadius="110",
                    MagazineType="Base.AT_SARMag", MetalValue="34.0"),
    "AT_QDX99": gun(PISTOL, SMG, Weight="2.6", Aimingtime="28", MaxAmmo="30", ClipSize="30", MaxRange="17.0",
                    MinDamage="0.6", MaxDamage="1.0", RecoilDelay="7", SoundRadius="110",
                    MagazineType="Base.AT_QDXMag", MetalValue="32.0"),
    "AT_MX4": (RIFLE, {"Weight": "3.0", "Aimingtime": "32", "MaxRange": "26.0", "MaxDamage": "1.5",
                       "RecoilDelay": "13", "MagazineType": "Base.AT_MX4Mag", "MetalValue": "38.0"}),
    "AT_AUGA5": (RIFLE, {"Weight": "3.6", "Aimingtime": "34", "MaxRange": "32.0", "RecoilDelay": "14",
                         "MagazineType": "Base.AT_AUGMag", "MetalValue": "40.0"}),
    "AT_AG203": gun(RIFLE, R308, Weight="4.0", Aimingtime="45", MaxAmmo="20", FireMode="Auto",
                    FireModePossibilities="Auto/Single", MagazineType="Base.AT_AG203Mag", MetalValue="45.0"),
    "AT_Komodo": gun(RIFLE, R308, Weight="3.8", Aimingtime="42", MaxAmmo="20", FireMode="Auto",
                     FireModePossibilities="Auto/Single", RecoilDelay="18", MagazineType="Base.AT_KomodoMag",
                     MetalValue="44.0"),
    "AT_RPK101": (RIFLE, {"Weight": "5.5", "Aimingtime": "50", "MaxAmmo": "75", "MaxRange": "32.0",
                          "MaxHitcount": "2", "RecoilDelay": "12", "Reloadtime": "40",
                          "MagazineType": "Base.AT_RPKDrum", "MetalValue": "55.0"}),
    "AT_PSR": gun(RIFLE, R308, Weight="4.4", Aimingtime="48", MaxAmmo="10", FireMode="Single",
                  FireModePossibilities=None, MaxDamage="2.6", MinDamage="1.8", MaxRange="45.0",
                  CriticalChance="40.0", SoundRadius="40", SoundVolume="15", MaxSightRange="16.0",
                  MinSightRange="5", MagazineType="Base.AT_PSRMag", MetalValue="48.0"),
    "AT_CycloneAGL": (RIFLE, AGL),
}

MAGS = {  # id: (arma, munición, capacidad, etiqueta)
    "AT_SkullMag": ("AT_M4", "base:bullets_556", 30, "base:riflemagazine"),
    "AT_LancerMag": ("AT_MCX", "base:bullets_556", 30, "base:riflemagazine"),
    "AT_AKMag": ("AT_AK101", "base:bullets_556", 30, "base:riflemagazine"),
    "AT_G19Mag": ("AT_G19", "base:bullets_9mm", 15, "base:pistolmagazine"),
    "AT_GXPMag": ("AT_GXP", "base:bullets_9mm", 17, "base:pistolmagazine"),
    "AT_MD34Mag": ("AT_MD34", "base:bullets_45", 8, "base:pistolmagazine"),
    "AT_GravMag": ("AT_GravRecon", "base:bullets_9mm", 17, "base:pistolmagazine"),
    "AT_VikorMag": ("AT_VikorS1", "base:bullets_9mm", 18, "base:pistolmagazine"),
    "AT_FNPRMag": ("AT_FNPR", "base:bullets_45", 15, "base:pistolmagazine"),
    "AT_SARMag": ("AT_FNSAR", "base:bullets_9mm", 50, "base:pistolmagazine"),
    "AT_QDXMag": ("AT_QDX99", "base:bullets_9mm", 30, "base:pistolmagazine"),
    "AT_MX4Mag": ("AT_MX4", "base:bullets_556", 30, "base:riflemagazine"),
    "AT_AUGMag": ("AT_AUGA5", "base:bullets_556", 30, "base:riflemagazine"),
    "AT_AG203Mag": ("AT_AG203", "base:bullets_308", 20, "base:riflemagazine"),
    "AT_KomodoMag": ("AT_Komodo", "base:bullets_308", 20, "base:riflemagazine"),
    "AT_RPKDrum": ("AT_RPK101", "base:bullets_556", 75, "base:riflemagazine"),
    "AT_PSRMag": ("AT_PSR", "base:bullets_308", 10, "base:riflemagazine"),
}

PARTS = {  # id: (base, propiedades)
    "AT_ACOG": (SCOPE, {"Weight": "0.45", "WeightModifier": "0.45", "AimingTimeModifier": "8",
                        "MaxSightRange": "16.0", "MinSightRange": "6"}),
    "AT_LPVO": (SCOPE, {"Weight": "0.6", "WeightModifier": "0.6", "AimingTimeModifier": "6",
                        "MaxSightRange": "14.0", "MinSightRange": "3"}),
    "AT_HoloSight": (REDDOT, {"Weight": "0.35", "WeightModifier": "0.2", "AimingTimeModifier": "-12",
                              "MaxSightRange": "10.0", "MinSightRange": "2"}),
    "AT_Thermal": (SCOPE, {"Weight": "0.9", "WeightModifier": "0.9", "AimingTimeModifier": "18",
                           "MaxSightRange": "22.0", "MinSightRange": "12"}),
    "AT_TacLight": (LIGHT, {"Weight": "0.2", "WeightModifier": "0.2", "AimingTimeModifier": "5",
                            "LightDistance": "18", "LightStrength": "1.5"}),
}
MOUNT = {p: OPTIC_GUNS for p in OPTICS}
MOUNT["AT_TacLight"] = ALL_GUNS
EXTRA = {  # ítems sueltos: granada de 40 mm (munición) y la carga que usa la Lua para la explosión
    "AT_Granada40": (GRENADE, {"Icon": "AT_Granada40", "WorldStaticModel": "AT_Granada40"}),
    "AT_Granada40Carga": (CHARGE, {"Icon": "AT_Granada40", "WorldStaticModel": "AT_Granada40"}),
}

NAMES = {  # id: (EN, ES)
    "AT_M4": ("M4 Carbine", "Carabina M4"),
    "AT_MCX": ("MX-C Compact Carbine", "Carabina compacta MX-C"),
    "AT_AK101": ("Folding AK-101", "AK-101 plegable"),
    "AT_Marlin336": ("336T Tactical Lever Carbine", "Carabina de palanca táctica 336T"),
    "AT_G19": ("G-19 Pistol", "Pistola G-19"),
    "AT_SkullMag": ("M4 Magazine (Skull)", "Cargador de M4 (calavera)"),
    "AT_LancerMag": ("MX-C Translucent Magazine", "Cargador translúcido de MX-C"),
    "AT_AKMag": ("AK-101 Magazine", "Cargador de AK-101"),
    "AT_G19Mag": ("G-19 Magazine", "Cargador de G-19"),
    "AT_ACOG": ("4x Combat Sight", "Mira de combate 4x"),
    "AT_LPVO": ("1-6x Variable Scope", "Mira variable 1-6x"),
    "AT_HoloSight": ("Holographic Sight", "Mira holográfica"),
    "AT_Thermal": ("Thermal Scope", "Mira térmica"),
    "AT_TacLight": ("Tactical Weapon Light", "Linterna táctica"),
    # --- lámina conceptual
    "AT_GXP": ("GXP Long-Slide Pistol", "Pistola GXP de corredera larga"),
    "AT_MD34": ("MD34 Diablo Pistol", "Pistola MD34 Diablo"),
    "AT_GravRecon": ("Grav Recon Pistol", "Pistola Grav Recon"),
    "AT_VikorS1": ("Vikor-S1 Pistol", "Pistola Vikor-S1"),
    "AT_FNPR": ("FNP-R Suppressed Pistol", "Pistola FNP-R con supresor"),
    "AT_FNSAR": ("FN SAR Personal Defense Weapon", "Arma compacta FN SAR"),
    "AT_QDX99": ("QDX-99 Compact SMG", "Subfusil compacto QDX-99"),
    "AT_MX4": ("MX-4 Carbine", "Carabina MX-4"),
    "AT_AUGA5": ("AUG A5 Bullpup Rifle", "Fusil bullpup AUG A5"),
    "AT_AG203": ("AG-203 Battle Rifle", "Fusil de combate AG-203"),
    "AT_Komodo": ("Komodo 6.8 Rifle", "Fusil Komodo 6.8"),
    "AT_CycloneAGL": ("Cyclone-AGL Grenade Launcher", "Lanzagranadas Cyclone-AGL"),
    "AT_RPK101": ("RPK-101 Uragan Light Machine Gun", "Ametralladora ligera RPK-101 Uragan"),
    "AT_PSR": ("PSR Suppressed Sniper Rifle", "Fusil de precisión PSR con supresor"),
    "AT_GXPMag": ("GXP Magazine", "Cargador de GXP"),
    "AT_MD34Mag": ("MD34 Magazine", "Cargador de MD34"),
    "AT_GravMag": ("Grav Recon Magazine", "Cargador de Grav Recon"),
    "AT_VikorMag": ("Vikor-S1 Magazine", "Cargador de Vikor-S1"),
    "AT_FNPRMag": ("FNP-R Magazine", "Cargador de FNP-R"),
    "AT_SARMag": ("FN SAR 50-round Magazine", "Cargador de 50 de FN SAR"),
    "AT_QDXMag": ("QDX-99 Magazine", "Cargador de QDX-99"),
    "AT_MX4Mag": ("MX-4 Magazine", "Cargador de MX-4"),
    "AT_AUGMag": ("AUG Magazine", "Cargador de AUG"),
    "AT_AG203Mag": ("AG-203 Magazine", "Cargador de AG-203"),
    "AT_KomodoMag": ("Komodo Magazine", "Cargador de Komodo"),
    "AT_RPKDrum": ("RPK-101 75-round Drum", "Tambor de 75 de RPK-101"),
    "AT_PSRMag": ("PSR Magazine", "Cargador de PSR"),
    "AT_Granada40": ("40mm Grenade", "Granada de 40 mm"),
    "AT_Granada40Carga": ("40mm Grenade Charge", "Carga de granada de 40 mm"),
}

LOOT = {  # contenedor (ProceduralDistributions de 42.18): {ítem: peso}
    "FirearmWeapons_Mid": {"AT_M4": 1, "AT_MCX": 0.5, "AT_AK101": 0.5, "AT_G19": 2, "AT_Marlin336": 1,
                           "AT_GXP": 1, "AT_GravRecon": 1, "AT_VikorS1": 1, "AT_MD34": 0.7, "AT_MX4": 0.5},
    "FirearmWeapons_Late": {"AT_M4": 1, "AT_MCX": 0.5, "AT_AK101": 0.5, "AT_G19": 2, "AT_Marlin336": 1,
                            "AT_TacLight": 0.5, "AT_HoloSight": 0.5, "AT_AUGA5": 0.5, "AT_Komodo": 0.4,
                            "AT_AG203": 0.4, "AT_FNSAR": 0.3, "AT_QDX99": 0.3},
    "GunStoreGuns": {"AT_G19": 2, "AT_Marlin336": 1, "AT_GXP": 1, "AT_MD34": 1},
    "GunStorePistols": {"AT_G19": 4, "AT_TacLight": 1, "AT_GXP": 2, "AT_GravRecon": 2, "AT_VikorS1": 2,
                        "AT_MD34": 1.5, "AT_FNPR": 0.5},
    "GunStoreRifles": {"AT_Marlin336": 2, "AT_MCX": 0.5, "AT_LPVO": 1, "AT_MX4": 0.7, "AT_AUGA5": 0.5,
                       "AT_Komodo": 0.4},
    "GunStoreAccessories": {"AT_ACOG": 1, "AT_LPVO": 1, "AT_HoloSight": 2, "AT_Thermal": 0.3, "AT_TacLight": 2},
    "GunStoreMagsAmmo": {"AT_SkullMag": 1, "AT_LancerMag": 1, "AT_AKMag": 1, "AT_G19Mag": 2, "AT_GXPMag": 1,
                         "AT_GravMag": 1, "AT_VikorMag": 1, "AT_MD34Mag": 1, "AT_MX4Mag": 0.7, "AT_AUGMag": 0.5,
                         "AT_KomodoMag": 0.4},
    "PawnShopGunsSpecial": {"AT_M4": 1, "AT_MCX": 1, "AT_AK101": 1, "AT_Thermal": 0.3, "AT_FNPR": 0.5,
                            "AT_QDX99": 0.5, "AT_AG203": 0.5},
    "PoliceStorageGuns": {"AT_G19": 4, "AT_TacLight": 1, "AT_GXP": 2, "AT_GravRecon": 2, "AT_MX4": 1},
    "PoliceStorageAmmunition": {"AT_G19Mag": 4, "AT_GXPMag": 2, "AT_GravMag": 2, "AT_MX4Mag": 1},
    "SWATStorageGuns": {"AT_M4": 4, "AT_MCX": 3, "AT_G19": 4, "AT_TacLight": 3, "AT_HoloSight": 2, "AT_ACOG": 2,
                        "AT_FNSAR": 2, "AT_QDX99": 1, "AT_AUGA5": 1, "AT_PSR": 0.5, "AT_FNPR": 1},
    "SWATStorageAmmunition": {"AT_SkullMag": 4, "AT_LancerMag": 3, "AT_G19Mag": 4, "AT_SARMag": 2, "AT_QDXMag": 1,
                              "AT_AUGMag": 1, "AT_PSRMag": 0.5, "AT_FNPRMag": 1},
    "ArmyStorageGuns": {"AT_M4": 4, "AT_ACOG": 2, "AT_Thermal": 0.5, "AT_RPK101": 1, "AT_Komodo": 1,
                        "AT_AG203": 1, "AT_PSR": 0.5, "AT_CycloneAGL": 0.4},
    "ArmyStorageAmmunition": {"AT_SkullMag": 4, "AT_RPKDrum": 1, "AT_KomodoMag": 1, "AT_AG203Mag": 1,
                              "AT_PSRMag": 0.5, "AT_Granada40": 2},
    "DrugLabGuns": {"AT_AK101": 2, "AT_G19": 2, "AT_AKMag": 2, "AT_VikorS1": 1, "AT_QDX99": 0.5},
    "DrugShackWeapons": {"AT_AK101": 1, "AT_G19": 1, "AT_VikorS1": 1},
    "Hunter": {"AT_Marlin336": 2},
    "HuntingLockers": {"AT_Marlin336": 2, "AT_LPVO": 1, "AT_PSR": 0.2},
}


# --------------------------------------------------------------- generadores
def block(kind, name, base, over, extra=()):
    props = []
    seen = set()
    for line in base.split("\n"):
        k = line.split("=", 1)[0].strip()
        seen.add(k)
        if k in over:
            if over[k] is None:        # None borra la propiedad heredada de la base vanilla
                continue
            line = f"{k} = {over[k]}"
        props.append(line)
    for k, v in over.items():
        if k not in seen and v is not None:
            props.append(f"{k} = {v}")
    props += list(extra)
    body = "\n".join(f"        {p}," for p in props)
    return f"    {kind} {name}\n    {{\n{body}\n    }}\n"


def items():
    out = ["/*\n    Arsenal Tactico - armas, cargadores y partes. Generado por tools/build_arsenal_tactico.py:\n"
           "    editar la tabla de ese script, no este archivo. Bases: bloques vanilla de 42.18.\n*/\n"
           "module Base\n{\n"]
    for gid, (base, over) in GUNS.items():
        o = dict(over, Icon=gid, WeaponSprite=gid)
        if base is PISTOL:
            o.setdefault("ClipSize", "15")
        out.append(block("item", gid, base, o, parts_lines(gid)))
    for mid, (gun, ammo, cap, tag) in MAGS.items():
        out.append(block("item", mid, MAG.format(tag=tag), {"Icon": mid, "AmmoType": ammo, "GunType": f"Base.{gun}",
                                                            "MaxAmmo": str(cap), "WorldStaticModel": mid}))
    for pid, (base, over) in PARTS.items():
        o = dict(over, Icon=pid, MountOn=";".join(f"Base.{g}" for g in MOUNT[pid]), WorldStaticModel=pid,
                 StaticModel=pid)
        out.append(block("item", pid, base, o))
    for eid, (base, over) in EXTRA.items():
        out.append(block("item", eid, base, over))
    out.append("}\n")
    return "\n".join(out)


def att(name, off, rot=(0, 0, 0), scale=None):
    s = f"        attachment {name}\n        {{\n            offset = {off[0]:.4f} {off[1]:.4f} {off[2]:.4f},\n" \
        f"            rotate = {rot[0]:.4f} {rot[1]:.4f} {rot[2]:.4f},\n"
    if scale:
        s += f"            scale = {scale},\n"
    return s + "        }\n"


def models():
    out = ["/*\n    Arsenal Tactico - modelos. Generado por tools/build_arsenal_tactico.py desde\n"
           "    art/<ID>/attachments.json (tools/blender/gunkit.py). Convencion vanilla: rifles con el largo\n"
           "    sobre +Y y arriba +Z (M16_Rifle); pistolas arriba -Z (M9_Pistol). Las partes se montan en\n"
           "    at_optic / at_light (en pistolas rotate 180 0 -180, como el scope de Handgun03).\n*/\n"
           "module Base\n{\n"]
    for mid in list(GUNS) + list(MAGS) + list(PARTS) + ["AT_Granada40"]:
        data = json.loads((ART / mid / "attachments.json").read_text())
        a = data["attachments"]
        hand = data["kind"] == "handgun"
        s = f"    model {mid}\n    {{\n        mesh = weapons/ArsenalTactico/{mid},\n" \
            f"        texture = weapons/ArsenalTactico/{mid},\n"
        if mid in GUNS:
            s += att("muzzle", a["muzzle"], (-90, 0, 0) if hand else (-90, 0, -180))
            flip = (180, 0, -180) if hand else (0, 0, 0)
            for k in ("at_optic", "at_light"):
                if k in a:
                    s += att(k, a[k], flip)
            if hand:
                s += att("world", (-0.009, 0.062, 0.0))
                s += att("Bip01_Prop2", (-0.0338, 0.0424, 0.0), (90.0008, 1.1964, -90.0396))
            else:
                s += att("world", (0.02, round(data["center"][1], 4), 0.0), (180, 0, 180))
        else:
            s += att("world", (0.0, 0.0, 0.0))
        out.append(s + "    }\n")
    out.append("}\n")
    return "\n".join(out)


def translations():
    for lang, i in (("EN", 0), ("ES", 1)):
        d = MEDIA / "lua/shared/Translate" / lang
        d.mkdir(parents=True, exist_ok=True)
        data = {f"Base.{k}": v[i] for k, v in NAMES.items()}
        (d / "ItemName.json").write_text(json.dumps(data, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")


def distributions():
    lines = ["-- Arsenal Táctico: botín. Generado por tools/build_arsenal_tactico.py (editar la tabla LOOT).",
             "-- Tolera contenedores que no existan (versiones del juego / otros mods).",
             "local LOOT = {"]
    for cont, items_ in LOOT.items():
        lines.append(f"    {cont} = {{ " + ", ".join(f'"Base.{k}", {v}' for k, v in items_.items()) + " },")
    lines += ["}", "",
              "local function addLoot()",
              "    local dist = ProceduralDistributions and ProceduralDistributions.list",
              "    if not dist then return end",
              "    for name, entries in pairs(LOOT) do",
              "        local cont = dist[name]",
              "        if cont and cont.items then",
              "            for i = 1, #entries do table.insert(cont.items, entries[i]) end",
              "        end",
              "    end",
              "end", "",
              "Events.OnPreDistributionMerge.Add(addLoot)", ""]
    d = MEDIA / "lua/server"
    d.mkdir(parents=True, exist_ok=True)
    (d / "ArsenalTactico_Distributions.lua").write_text("\n".join(lines), encoding="utf-8")


def main():
    (MEDIA / "scripts").mkdir(parents=True, exist_ok=True)
    (MEDIA / "scripts/ArsenalTactico_items.txt").write_text(items(), encoding="utf-8")
    (MEDIA / "scripts/ArsenalTactico_models.txt").write_text(models(), encoding="utf-8")
    translations()
    distributions()
    info = MOD / "mod.info"
    info.write_text("name=Arsenal Tactico\nid=ArsenalTactico\nauthor=francoppo04\n"
                    "description=19 armas de fuego (pistolas, PDW, carabinas, fusiles, ametralladora ligera, fusil "
                    "de precision y lanzagranadas con granadas que explotan) con miras, linterna y cargadores "
                    "propios. Balance vanilla.\nposter=poster.png\n", encoding="utf-8")
    (MOD.parent / "common").mkdir(exist_ok=True)
    (MOD.parent / "common" / ".gitkeep").touch()
    print("[build] scripts, traducciones, botín y mod.info generados")


if __name__ == "__main__":
    main()
