import sys
from lib.parser import readint, readintoffset, readtextoffset, remove2MSB, identifytype, get_actual_value_str

#Note: All the pointers pushed to the stack have their pointers updated when recompiling (their position doesn't really matter)
#However all the code locations matter and need to be precisely updated to their new location, we do that by setting labels


def init_command_names_dicts():

    global commands_dict
    global reverse_commands_dict

    commands_dict= {(0, 0x00) : "Cmd_system_00",
    (0, 0x01) : "Cmd_system_01",
    (0, 0x02) : "Cmd_system_02",
    (0, 0x03) : "Cmd_system_03",
    (0, 0x04) : "Cmd_system_04",
    (0, 0x05) : "Cmd_system_05",
    (0, 0x06) : "Cmd_system_06",
    (0, 0x07) : "Cmd_system_07",
    (0, 0x08) : "Cmd_system_08",
    (0, 0x09) : "Cmd_system_09",
    (0, 0x0A) : "Cmd_system_0A",
    (0, 0x0B) : "Cmd_system_0B",
    (0, 0x0C) : "Cmd_system_0C",
    (0, 0x0D) : "Cmd_system_0D",
    (0, 0x0E) : "Cmd_system_0E",
    (0, 0x0F) : "Cmd_system_0F",
    (0, 0x10) : "Cmd_system_10",
    (0, 0x11) : "Cmd_system_11",
    (0, 0x12) : "Cmd_system_12",
    (0, 0x13) : "Cmd_system_13",
    (0, 0x14) : "Cmd_system_14",
    (0, 0x15) : "Cmd_system_15",
    (0, 0x16) : "Cmd_system_16",
    (0, 0x17) : "Cmd_system_17",
    (0, 0x18) : "Cmd_system_18",
    (0, 0x19) : "Cmd_system_19",
    (0, 0x1A) : "Cmd_system_1A",
    (0, 0x1B) : "Cmd_system_1B",
    (0, 0x1C) : "Cmd_system_1C",
    (0, 0x1D) : "Cmd_system_1D",
    (0, 0x1E) : "Cmd_system_1E",
    (0, 0x1F) : "Cmd_system_1F",
    (1, 0x00)  : "Cmd_characters_00",
    (1, 0x01)  : "Cmd_characters_01",
    (1, 0x02)  : "Cmd_characters_02",
    (1, 0x03)  : "Cmd_characters_03",
    (1, 0x04)  : "Cmd_characters_04",
    (1, 0x05)  : "Cmd_characters_05",
    (1, 0x06)  : "Cmd_characters_06",
    (1, 0x07)  : "Cmd_characters_07",
    (1, 0x08)  : "Cmd_characters_08",
    (1, 0x09)  : "Cmd_characters_09",
    (1, 0x0A)  : "Cmd_characters_0A",
    (1, 0x0B)  : "Cmd_characters_0B",
    (1, 0x0C)  : "Cmd_characters_0C",
    (1, 0x0D)  : "Cmd_characters_0D",
    (1, 0x0E)  : "Cmd_characters_0E",
    (1, 0x0F)  : "Cmd_characters_0F",
    (1, 0x10)  : "Cmd_characters_10",
    (1, 0x11)  : "Cmd_characters_11",
    (1, 0x12)  : "Cmd_characters_12",
    (1, 0x13)  : "Cmd_characters_13",
    (1, 0x14)  : "Cmd_characters_14",
    (1, 0x15)  : "Cmd_characters_15",
    (1, 0x16)  : "Cmd_characters_16",
    (1, 0x17)  : "Cmd_characters_17",
    (1, 0x18)  : "Cmd_characters_18",
    (1, 0x19)  : "Cmd_characters_19",
    (1, 0x1A)  : "Cmd_characters_1A",
    (1, 0x1B)  : "Cmd_characters_1B",
    (1, 0x1C)  : "Cmd_characters_1C",
    (1, 0x1D)  : "Cmd_characters_1D",
    (1, 0x1E)  : "Cmd_characters_1E",
    (1, 0x1F)  : "Cmd_characters_1F",
    (1, 0x20)  : "Cmd_characters_20",
    (1, 0x21)  : "Cmd_characters_21",
    (1, 0x22)  : "Cmd_characters_22",
    (1, 0x23)  : "Cmd_characters_23",
    (1, 0x24)  : "Cmd_characters_24",
    (1, 0x25)  : "Cmd_characters_25",
    (1, 0x26)  : "Cmd_characters_26",
    (1, 0x27)  : "Cmd_characters_27",
    (1, 0x28)  : "Cmd_characters_28",
    (1, 0x29)  : "Cmd_characters_29",
    (1, 0x2A)  : "Cmd_characters_2A",
    (1, 0x2B)  : "Cmd_characters_2B",
    (1, 0x2C)  : "Cmd_characters_2C",
    (1, 0x2D)  : "Cmd_characters_2D",
    (1, 0x2E)  : "Cmd_characters_2E",
    (1, 0x2F)  : "SetAnimation",
    (1, 0x30)  : "Cmd_characters_30",
    (1, 0x31)  : "Cmd_characters_31",
    (1, 0x32)  : "Cmd_characters_32",
    (1, 0x33)  : "Cmd_characters_33",
    (1, 0x34)  : "Cmd_characters_34",
    (1, 0x35)  : "Cmd_characters_35",
    (1, 0x36)  : "Cmd_characters_36",
    (1, 0x37)  : "Cmd_characters_37",
    (1, 0x38)  : "Cmd_characters_38",
    (1, 0x39)  : "Cmd_characters_39",
    (1, 0x3A)  : "Cmd_characters_3A",
    (1, 0x3B)  : "Cmd_characters_3B",
    (1, 0x3C)  : "Cmd_characters_3C",
    (1, 0x3D)  : "Cmd_characters_3D",
    (1, 0x3E)  : "Cmd_characters_3E",
    (1, 0x3F)  : "Cmd_characters_3F",
    (1, 0x40)  : "Cmd_characters_40",
    (1, 0x41)  : "Cmd_characters_41",
    (1, 0x42)  : "Cmd_characters_42",
    (1, 0x43)  : "Cmd_characters_43",
    (1, 0x44)  : "Cmd_characters_44",
    (1, 0x45)  : "Cmd_characters_45",
    (1, 0x46)  : "Cmd_characters_46",
    (1, 0x47)  : "Cmd_characters_47",
    (1, 0x48)  : "Cmd_characters_48",
    (1, 0x49)  : "Cmd_characters_49",
    (1, 0x4A)  : "Cmd_characters_4A",
    (1, 0x4B)  : "Cmd_characters_4B",
    (1, 0x4C)  : "Cmd_characters_4C",
    (1, 0x4D)  : "Cmd_characters_4D",
    (1, 0x4E)  : "Cmd_characters_4E",
    (1, 0x4F)  : "Cmd_characters_4F",
    (1, 0x50)  : "Cmd_characters_50",
    (1, 0x51)  : "Cmd_characters_51",
    (1, 0x52)  : "Cmd_characters_52",
    (1, 0x53)  : "Cmd_characters_53",
    (1, 0x54)  : "Cmd_characters_54",
    (1, 0x55)  : "Cmd_characters_55",
    (1, 0x56)  : "Cmd_characters_56",
    (1, 0x57)  : "Cmd_characters_57",
    (1, 0x58)  : "Cmd_characters_58",
    (1, 0x59)  : "Cmd_characters_59",
    (1, 0x5A)  : "Cmd_characters_5A",
    (1, 0x5B)  : "Cmd_characters_5B",
    (1, 0x5C)  : "Cmd_characters_5C",
    (1, 0x5D)  : "Cmd_characters_5D",
    (1, 0x5E)  : "Cmd_characters_5E",
    (1, 0x5F)  : "Cmd_characters_5F",
    (1, 0x60)  : "Cmd_characters_60",
    (1, 0x61)  : "Cmd_characters_61",
    (1, 0x62)  : "Cmd_characters_62",
    (1, 0x63)  : "Cmd_characters_63",
    (1, 0x64)  : "Cmd_characters_64",
    (1, 0x65)  : "Cmd_characters_65",
    (1, 0x66)  : "Cmd_characters_66",
    (1, 0x67)  : "Cmd_characters_67",
    (1, 0x68)  : "Cmd_characters_68",
    (1, 0x69)  : "Cmd_characters_69",
    (1, 0x6A)  : "Cmd_characters_6A",
    (1, 0x6B)  : "Cmd_characters_6B",
    (1, 0x6C)  : "Cmd_characters_6C",
    (1, 0x6D)  : "Cmd_characters_6D",
    (1, 0x6E)  : "Cmd_characters_6E",
    (1, 0x6F)  : "Cmd_characters_6F",
    (1, 0x70)  : "Cmd_characters_70",
    (1, 0x71)  : "Cmd_characters_71",
    (1, 0x72)  : "Cmd_characters_72",
    (1, 0x73)  : "Cmd_characters_73",
    (1, 0x74)  : "Cmd_characters_74",
    (1, 0x75)  : "Cmd_characters_75",
    (1, 0x76)  : "Cmd_characters_76",
    (1, 0x77)  : "Cmd_characters_77",
    (1, 0x78)  : "Cmd_characters_78",
    (1, 0x79)  : "Cmd_characters_79",
    (1, 0x7A)  : "Cmd_characters_7A",
    (1, 0x7B)  : "Cmd_characters_7B",
    (1, 0x7C)  : "Cmd_characters_7C",
    (1, 0x7D)  : "Cmd_characters_7D",
    (1, 0x7E)  : "Cmd_characters_7E",
    (1, 0x7F)  : "Cmd_characters_7F",
    (1, 0x80)  : "Cmd_characters_80",
    (1, 0x81)  : "Cmd_characters_81",
    (1, 0x82)  : "Cmd_characters_82",
    (1, 0x83)  : "Cmd_characters_83",
    (1, 0x84)  : "Cmd_characters_84",
    (1, 0x85)  : "Cmd_characters_85",
    (1, 0x86)  : "Cmd_characters_86",
    (1, 0x87)  : "Cmd_characters_87",
    (1, 0x88)  : "Cmd_characters_88",
    (1, 0x89)  : "Cmd_characters_89",
    (1, 0x8A)  : "Cmd_characters_8A",
    (1, 0x8B)  : "Cmd_characters_8B",
    (1, 0x8C)  : "Cmd_characters_8C",
    (1, 0x8D)  : "Cmd_characters_8D",
    (1, 0x8E)  : "Cmd_characters_8E",
    (1, 0x8F)  : "Cmd_characters_8F",
    (1, 0x90)  : "Cmd_characters_90",
    (1, 0x91)  : "Cmd_characters_91",
    (1, 0x92)  : "Cmd_characters_92",
    (1, 0x93)  : "Cmd_characters_93",
    (1, 0x94)  : "Cmd_characters_94",
    (1, 0x95)  : "Cmd_characters_95",
    (1, 0x96)  : "Cmd_characters_96",
    (1, 0x97)  : "Cmd_characters_97",
    (1, 0x98)  : "Cmd_characters_98",
    (1, 0x99)  : "Cmd_characters_99",
    (1, 0x9A)  : "Cmd_characters_9A",
    (1, 0x9B)  : "Cmd_characters_9B",
    (1, 0x9C)  : "Cmd_characters_9C",
    (1, 0x9D)  : "Cmd_characters_9D",
    (1, 0x9E)  : "Cmd_characters_9E",
    (1, 0x9F)  : "Cmd_characters_9F",
    (1, 0xA0)  : "Cmd_characters_A0",
    (1, 0xA1)  : "Cmd_characters_A1",
    (1, 0xA2)  : "Cmd_characters_A2",
    (1, 0xA3)  : "Cmd_characters_A3",
    (1, 0xA4)  : "Cmd_characters_A4",
    (1, 0xA5)  : "Cmd_characters_A5",
    (1, 0xA6)  : "Cmd_characters_A6",
    (1, 0xA7)  : "Cmd_characters_A7",
    (1, 0xA8)  : "Cmd_characters_A8",
    (1, 0xA9)  : "Cmd_characters_A9",
    (1, 0xAA)  : "Cmd_characters_AA",
    (1, 0xAB)  : "Cmd_characters_AB",
    (1, 0xAC)  : "Cmd_characters_AC",
    (1, 0xAD)  : "Cmd_characters_AD",
    (1, 0xAE)  : "Cmd_characters_AE",
    (1, 0xAF)  : "Cmd_characters_AF",
    (1, 0xB0)  : "Cmd_characters_B0",
    (1, 0xB1)  : "Cmd_characters_B1",
    (1, 0xB2)  : "Cmd_characters_B2",
    (1, 0xB3)  : "Cmd_characters_B3",
    (1, 0xB4)  : "Cmd_characters_B4",
	(1, 0xB5)  : "Cmd_characters_B5",
    (1, 0xB6)  : "Cmd_characters_B6",
	(1, 0xB7)  : "Cmd_characters_B7",
    (1, 0xB8)  : "Cmd_characters_B8",
    (1, 0xB9)  : "Cmd_characters_B9",
    (2, 0x00)  : "Cmd_camera_00",
    (2, 0x01)  : "Cmd_camera_01",
    (2, 0x02)  : "Cmd_camera_02",
    (2, 0x03)  : "Cmd_camera_03",
    (2, 0x04)  : "Cmd_camera_04",
    (2, 0x05)  : "Cmd_camera_05",
    (2, 0x06)  : "Cmd_camera_06",
    (2, 0x07)  : "Cmd_camera_07",
    (2, 0x08)  : "Cmd_camera_08",
    (2, 0x09)  : "Cmd_camera_09",
    (2, 0x0A)  : "Cmd_camera_0A",
    (2, 0x0B)  : "Cmd_camera_0B",
    (2, 0x0C)  : "Cmd_camera_0C",
    (2, 0x0D)  : "Cmd_camera_0D",
    (2, 0x0E)  : "Cmd_camera_0E",
    (2, 0x0F)  : "Cmd_camera_0F",
    (2, 0x10)  : "Cmd_camera_10",
    (2, 0x11)  : "Cmd_camera_11",
    (2, 0x12)  : "Cmd_camera_12",
    (2, 0x13)  : "Cmd_camera_13",
    (2, 0x14)  : "Cmd_camera_14",
    (2, 0x15)  : "Cmd_camera_15",
    (2, 0x16)  : "Cmd_camera_16",
    (2, 0x17)  : "Cmd_camera_17",
    (2, 0x18)  : "Cmd_camera_18",
    (2, 0x19)  : "Cmd_camera_19",
    (2, 0x1A)  : "Cmd_camera_1A",
    (2, 0x1B)  : "Cmd_camera_1B",
    (2, 0x1C)  : "Cmd_camera_1C",
    (2, 0x1D)  : "Cmd_camera_1D",
    (2, 0x1E)  : "Cmd_camera_1E",
    (2, 0x1F)  : "Cmd_camera_1F",
    (2, 0x20)  : "Cmd_camera_20",
    (2, 0x21)  : "Cmd_camera_21",
    (2, 0x22)  : "Cmd_camera_22",

    (3, 0x00)  : "Cmd_event_00",
    (3, 0x01) : "Cmd_event_01",
    (3, 0x02) : "Cmd_event_02",
    (3, 0x03) : "Cmd_event_03",
    (3, 0x04) : "Cmd_event_04",
    (3, 0x05) : "Cmd_event_05",
    (3, 0x06) : "Cmd_event_06",
    (3, 0x07) : "Cmd_event_07",
    (3, 0x08) : "Cmd_event_08",
    (3, 0x09) : "Cmd_event_09",
    (3, 0x0A) : "Cmd_event_0A",
    (3, 0x0B) : "Cmd_event_0B",
    (3, 0x0C) : "Cmd_event_0C",
    (3, 0x0D) : "Cmd_event_0D",
    (3, 0x0E) : "Cmd_event_0E",
    (3, 0x0F) : "Cmd_event_0F",
    (3, 0x10) : "Cmd_event_10",
    (3, 0x11) : "Cmd_event_11",
    (3, 0x12) : "Cmd_event_12",
    (3, 0x13) : "Cmd_event_13",
    (3, 0x14) : "Cmd_event_14",
    (3, 0x15) : "Cmd_event_15",
    (3, 0x16) : "Cmd_event_16",
    (3, 0x17) : "Cmd_event_17",
    (3, 0x18) : "Cmd_event_18",
    (3, 0x19) : "Cmd_event_19",
    (3, 0x1A) : "Cmd_event_1A",
    (3, 0x1B) : "Cmd_event_1B",
    (3, 0x1C) : "Cmd_event_1C",
    (3, 0x1D) : "Cmd_event_1D",
    (3, 0x1E) : "Cmd_event_1E",
    (3, 0x1F) : "Cmd_event_1F",
    (3, 0x20) : "Cmd_event_20",
    (3, 0x21) : "Cmd_event_21",
    (3, 0x22) : "Cmd_event_22",
    (3, 0x23) : "Cmd_event_23",
    (3, 0x24) : "Cmd_event_24",
    (3, 0x25) : "Cmd_event_25",
    (3, 0x26) : "Cmd_event_26",
    (3, 0x27) : "Cmd_event_27",
    (3, 0x28) : "Cmd_event_28",
    (3, 0x29) : "Cmd_event_29",
    (3, 0x2A) : "Cmd_event_2A",
    (3, 0x2B) : "Cmd_event_2B",
    (4, 0x00)  : "Cmd_unknown_1_00",
    (4, 0x01)  : "Cmd_unknown_1_event_01",
    (4, 0x02)  : "Cmd_unknown_1_event_02",

    (5, 0x00) : "Cmd_text_00",
    (5, 0x01) : "Cmd_text_01",
    (5, 0x02) : "Cmd_text_02",
    (5, 0x03) : "Cmd_text_03",
    (5, 0x04) : "Cmd_text_04",
    (5, 0x05) : "Cmd_text_05",
    (5, 0x06) : "Cmd_text_06",
    (5, 0x07) : "Cmd_text_07",
    (5, 0x08) : "Cmd_text_08",
    (5, 0x09) : "Cmd_text_09",
    (5, 0x0A) : "Cmd_text_0A",
    (5, 0x0B) : "Cmd_text_0B",
    (5, 0x0C) : "Cmd_text_0C",
    (5, 0x0D) : "Cmd_text_0D",
    (5, 0x0E) : "Cmd_text_0E",
    (5, 0x0F) : "Cmd_text_0F",
    (5, 0x10) : "Cmd_text_10",
    (5, 0x11) : "Cmd_text_11",
    (5, 0x12) : "Cmd_text_12",
        (6, 0x00)  : "Cmd_sound_00",
        (6, 0x01)  : "Cmd_sound_01",
        (6, 0x02)  : "Cmd_sound_02",
        (6, 0x03)  : "Cmd_sound_03",
        (6, 0x04)  : "Cmd_sound_04",
        (6, 0x05)  : "Cmd_sound_05",
        (6, 0x06)  : "Cmd_sound_06",
        (6, 0x07)  : "Cmd_sound_07",
        (6, 0x08)  : "Cmd_sound_08",
        (6, 0x09)  : "Cmd_sound_09",
        (6, 0x0A)  : "Cmd_sound_0A",
        (6, 0x0B)  : "Cmd_sound_0B",
        (6, 0x0C)  : "Cmd_sound_0C",
        (6, 0x0D)  : "Cmd_sound_0D",
        (6, 0x0E)  : "Cmd_sound_0E",
        (6, 0x0F)  : "Cmd_sound_0F",
        (6, 0x10)  : "Cmd_sound_10",
        (6, 0x11)  : "Cmd_sound_11",
        (6, 0x12)  : "Cmd_sound_12",
        (6, 0x13)  : "Cmd_sound_13",
        (6, 0x14)  : "Cmd_sound_14",
        (6, 0x15)  : "Cmd_sound_15",
        (6, 0x16)  : "Cmd_sound_16",
        (6, 0x17)  : "Cmd_sound_17",
        (6, 0x18)  : "Cmd_sound_18",
        (6, 0x19)  : "Cmd_sound_19",
        (6, 0x1A)  : "Cmd_sound_1A",
        (6, 0x1B)  : "Cmd_sound_1B",
        (6, 0x1C)  : "Cmd_sound_1C",
        (6, 0x1D)  : "Cmd_sound_1D",
        (6, 0x1E)  : "Cmd_sound_1E",
        (6, 0x1F)  : "Cmd_sound_1F",
        (6, 0x20)  : "Cmd_sound_20",
        (6, 0x21)  : "Cmd_sound_21",
        (6, 0x22)  : "Cmd_sound_22",
        (6, 0x23)  : "Cmd_sound_23",
        (6, 0x24)  : "Cmd_sound_24",
        (6, 0x25)  : "Cmd_sound_25",
        (6, 0x26)  : "Cmd_sound_26",
        (6, 0x27)  : "Cmd_sound_27",
        (6, 0x28)  : "Cmd_sound_28",
        (6, 0x29)  : "Cmd_sound_29",
        (7, 0x00)  : "Cmd_unknown_2_00",
        (8, 0x00)  : "Cmd_movies_00",
        (8, 0x01)  : "Cmd_movies_01",
        (8, 0x02)  : "Cmd_movies_02",
        (9, 0x00)  : "Cmd_unknown_3_00",
        (10, 0x00)  : "Cmd_unknown_4_00",
        (10, 0x01)  : "Cmd_unknown_4_01",
        (10, 0x02)  : "Cmd_unknown_4_02",
        (10, 0x03)  : "Cmd_unknown_4_03",
        (10, 0x04)  : "Cmd_unknown_4_04",
        (10, 0x05)  : "Cmd_unknown_4_05",
        (10, 0x06)  : "Cmd_unknown_4_06",
        (10, 0x07)  : "Cmd_unknown_4_07",
        (10, 0x08)  : "Cmd_unknown_4_08",
        (10, 0x09)  : "Cmd_unknown_4_09",
        (10, 0x0A)  : "Cmd_unknown_4_0A",
        (10, 0x0B)  : "Cmd_unknown_4_0B",
        (10, 0x0C)  : "Cmd_unknown_4_0C",
        (10, 0x0D)  : "Cmd_unknown_4_0D",
        (10, 0x0E)  : "Cmd_unknown_4_0E",
        (10, 0x0F)  : "Cmd_unknown_4_0F",
        (10, 0x10)  : "Cmd_unknown_4_10",
    (0xB, 0x00)  : "Cmd_map_00",
    (0xB, 0x01)  : "Cmd_map_01",
    (0xB, 0x02)  : "Cmd_map_02",
    (0xB, 0x03)  : "Cmd_map_03",
    (0xB, 0x04)  : "Cmd_map_04",
    (0xB, 0x05)  : "Cmd_map_05",
    (0xB, 0x06)  : "Cmd_map_06",
    (0xB, 0x07)  : "Cmd_map_07",
    (0xB, 0x08)  : "Cmd_map_08",
    (0xB, 0x09)  : "Cmd_map_09",
    (0xB, 0x0A)  : "Cmd_map_0A",
    (0xB, 0x0B)  : "Cmd_map_0B",
    (0xB, 0x0C)  : "Cmd_map_0C",
    (0xB, 0x0D)  : "Cmd_map_0D",
    (0xB, 0x0E)  : "Cmd_map_0E",
    (0xB, 0x0F)  : "Cmd_map_0F",
    (0xB, 0x10)  : "Cmd_map_10",
    (0xB, 0x11)  : "Cmd_map_11",
    (0xB, 0x12)  : "Cmd_map_12",
    (0xB, 0x13)  : "Cmd_map_13",
    (0xB, 0x14)  : "Cmd_map_14",
    (0xB, 0x15)  : "Cmd_map_15",
    (0xB, 0x16)  : "Cmd_map_16",
    (0xB, 0x17)  : "Cmd_map_17",
    (0xB, 0x18)  : "Cmd_map_18",
    (0xB, 0x19)  : "Cmd_map_19",
    (0xB, 0x1A)  : "Cmd_map_1A",
    (0xB, 0x1B)  : "Cmd_map_1B",
    (0xB, 0x1C)  : "Cmd_map_1C",
    (0xB, 0x1D)  : "Cmd_map_1D",
    (0xB, 0x1E)  : "Cmd_map_1E",
    (0xB, 0x1F)  : "Cmd_map_1F",
    (0xB, 0x20)  : "Cmd_map_20",
    (0xB, 0x21)  : "Cmd_map_21",
    (0xB, 0x22)  : "Cmd_map_22",
    (0xB, 0x23)  : "Cmd_map_23",
    (0xB, 0x24)  : "Cmd_map_24",
    (0xB, 0x25)  : "Cmd_map_25",
    (0xB, 0x26)  : "Cmd_map_26",
    (0xB, 0x27)  : "Cmd_map_27",
    (0xB, 0x28)  : "Cmd_map_28",
    (0xB, 0x29)  : "Cmd_map_29",
    (0xB, 0x2A)  : "Cmd_map_2A",
    (0xB, 0x2B)  : "Cmd_map_2B",
    (0xB, 0x2C)  : "Cmd_map_2C",
    (0xB, 0x2D)  : "Cmd_map_2D",
    (0xB, 0x2E)  : "Cmd_map_2E",
    (0xB, 0x2F)  : "Cmd_map_2F",
    (0xB, 0x30)  : "Cmd_map_30",
    (0xB, 0x31)  : "Cmd_map_31",
    (0xB, 0x32)  : "Cmd_map_32",
    (0xB, 0x33)  : "Cmd_map_33",
    (0xB, 0x34)  : "Cmd_map_34",
    (0xB, 0x35)  : "Cmd_map_35",
    (0xB, 0x36)  : "Cmd_map_36",
    (0xB, 0x37)  : "Cmd_map_37",
    (0xB, 0x38)  : "Cmd_map_38",
    (0xB, 0x39)  : "Cmd_map_39",
    (0xB, 0x3A)  : "Cmd_map_3A",
    (0xB, 0x3B)  : "Cmd_map_3B",
    (0xB, 0x3C)  : "Cmd_map_3C",
    (0xB, 0x3D)  : "Cmd_map_3D",
    (0xB, 0x3E)  : "Cmd_map_3E",
    (0xB, 0x3F)  : "Cmd_map_3F",
    (0xB, 0x40)  : "Cmd_map_40",
    (0xB, 0x41)  : "Cmd_map_41",
    (0xB, 0x42)  : "Cmd_map_42",
    (0xB, 0x43)  : "Cmd_map_43",
    (0xB, 0x44)  : "Cmd_map_44",
    (0xB, 0x45)  : "Cmd_map_45",
    (0xB, 0x46)  : "Cmd_map_46",
    (0xB, 0x47)  : "Cmd_map_47",
    (0xB, 0x48)  : "Cmd_map_48",
    (0xB, 0x49)  : "Cmd_map_49",
    (0xB, 0x4A)  : "Cmd_map_4A",
    (0xB, 0x4B)  : "Cmd_map_4B",
    (0xB, 0x4C)  : "Cmd_map_4C",
    (0xB, 0x4D)  : "Cmd_map_4D",
    (0xB, 0x4E)  : "Cmd_map_4E",
    (0xB, 0x4F)  : "Cmd_map_4F",
    (0xB, 0x50)  : "Cmd_map_50",
	(0xB, 0x51)  : "Cmd_map_51",
	(0xB, 0x52)  : "Cmd_map_52",
	(0xB, 0x53)  : "Cmd_map_53",
	(0xB, 0x54)  : "Cmd_map_54",
	(0xB, 0x55)  : "Cmd_map_55",
    (0xC, 0x00) : "Cmd_party_00",
    (0xC, 0x01) : "Cmd_party_01",
    (0xC, 0x02) : "Cmd_party_02",
    (0xC, 0x03) : "Cmd_party_03",
    (0xC, 0x04) : "Cmd_party_04",
    (0xC, 0x05) : "Cmd_party_05",
    (0xC, 0x06) : "Cmd_party_06",
    (0xC, 0x07) : "Cmd_party_07",
    (0xC, 0x08) : "Cmd_party_08",
    (0xC, 0x09) : "Cmd_party_09",
    (0xC, 0x0A) : "Cmd_party_0A",
    (0xC, 0x0B) : "Cmd_party_0B",
    (0xC, 0x0C) : "Cmd_party_0C",
	(0xC, 0x0D) : "Cmd_party_0D",
    (0xC, 0x0E) : "Cmd_party_0E",
	(0xC, 0x0F) : "Cmd_party_0F",
    (0xC, 0x10) : "Cmd_party_10",
	(0xC, 0x11) : "Cmd_party_11",
    (0xC, 0x12) : "Cmd_party_12",
	(0xC, 0x13) : "Cmd_party_13",
    (0xC, 0x14) : "Cmd_party_14",
	(0xC, 0x15) : "Cmd_party_15",
    (0xC, 0x16) : "Cmd_party_16",
	(0xC, 0x17) : "Cmd_party_17",
    (0xC, 0x18) : "Cmd_party_18",
	(0xC, 0x19) : "Cmd_party_19",
	(0xC, 0x1A) : "Cmd_party_1A",
	(0xC, 0x1B) : "Cmd_party_1B",
	(0xC, 0x1C) : "Cmd_party_1C",
	(0xC, 0x1D) : "Cmd_party_1D",
	(0xC, 0x1E) : "Cmd_party_1E",
	(0xC, 0x1F) : "Cmd_party_1F",
	(0xC, 0x20) : "Cmd_party_20",
	(0xC, 0x21) : "Cmd_party_21",
	(0xC, 0x22) : "Cmd_party_22",
	(0xC, 0x23) : "Cmd_party_23",
	(0xC, 0x24) : "Cmd_party_24",
    (0xC, 0x25) : "Cmd_party_25",
    (0xC, 0x26) : "Cmd_party_26",
    (0xC, 0x27) : "Cmd_party_27",
    (0xC, 0x28) : "Cmd_party_28",
    (0xC, 0x29) : "Cmd_party_29",
    (0xC, 0x2A) : "Cmd_party_2A",
    (0xC, 0x2B) : "Cmd_party_2B",
    (0xC, 0x2C) : "Cmd_party_2C",
    (0xC, 0x2D) : "Cmd_party_2D",
    (0xC, 0x2E) : "Cmd_party_2E",
    (0xC, 0x2F) : "Cmd_party_2F",
    (0xC, 0x30) : "Cmd_party_30",
    (0xC, 0x31) : "Cmd_party_31",
    (0xC, 0x32) : "Cmd_party_32",
    (0xC, 0x33) : "Cmd_party_33",
    (0xC, 0x34) : "Cmd_party_34",
    (0xC, 0x35) : "Cmd_party_35",
    (0xD, 0x00) : "Cmd_btl_00",
    (0xD, 0x01) : "Cmd_btl_01",
    (0xD, 0x02) : "Cmd_btl_02",
    (0xD, 0x03) : "Cmd_btl_03",
    (0xD, 0x04) : "Cmd_btl_04",
    (0xD, 0x05) : "Cmd_btl_05",
    (0xD, 0x06) : "Cmd_btl_06",
    (0xD, 0x07) : "Cmd_btl_07",
    (0xD, 0x08) : "Cmd_btl_08",
    (0xD, 0x09) : "Cmd_btl_09",
    (0xD, 0x0A) : "Cmd_btl_0A",
    (0xD, 0x0B) : "Cmd_btl_0B",
    (0xD, 0x0C) : "Cmd_btl_0C",
    (0xD, 0x0D) : "Cmd_btl_0D",
    (0xD, 0x0E) : "Cmd_btl_0E",
    (0xD, 0x0F) : "Cmd_btl_0F",
    (0xD, 0x10) : "Cmd_btl_10",
    (0xD, 0x11) : "Cmd_btl_11",
    (0xD, 0x12) : "Cmd_btl_12",
    (0xD, 0x13) : "Cmd_btl_13",
    (0xD, 0x14) : "Cmd_btl_14",
    (0xD, 0x15) : "Cmd_btl_15",
    (0xD, 0x16) : "Cmd_btl_16",
    (0xD, 0x17) : "Cmd_btl_17",
    (0xD, 0x18) : "Cmd_btl_18",
    (0xD, 0x19) : "Cmd_btl_19",
    (0xD, 0x1A) : "Cmd_btl_1A",
    (0xD, 0x1B) : "Cmd_btl_1B",
    (0xD, 0x1C) : "Cmd_btl_1C",
    (0xD, 0x1D) : "Cmd_btl_1D",
    (0xD, 0x1E) : "Cmd_btl_1E",
    (0xD, 0x1F) : "Cmd_btl_1F",
    (0xD, 0x20) : "Cmd_btl_20",
    (0xD, 0x21) : "Cmd_btl_21",
    (0xD, 0x22) : "Cmd_btl_22",
    (0xD, 0x23) : "Cmd_btl_23",
    (0xD, 0x24) : "Cmd_btl_24",
    (0xD, 0x25) : "Cmd_btl_25",
    (0xD, 0x26) : "Cmd_btl_26",
    (0xD, 0x27) : "Cmd_btl_27",
    (0xD, 0x28) : "Cmd_btl_28",
    (0xD, 0x29) : "Cmd_btl_29",
    (0xD, 0x2A) : "Cmd_btl_2A",
    (0xD, 0x2B) : "Cmd_btl_2B",
    (0xD, 0x2C) : "Cmd_btl_2C",
    (0xD, 0x2D) : "Cmd_btl_2D",
    (0xD, 0x2E) : "Cmd_btl_2E",
    (0xD, 0x2F) : "Cmd_btl_2F",
    (0xD, 0x30) : "Cmd_btl_30",
    (0xD, 0x31) : "Cmd_btl_31",
    (0xD, 0x32) : "Cmd_btl_32",
    (0xD, 0x33) : "Cmd_btl_33",
    (0xD, 0x34) : "Cmd_btl_34",
    (0xD, 0x35) : "Cmd_btl_35",
    (0xD, 0x36) : "Cmd_btl_36",
    (0xD, 0x37) : "Cmd_btl_37",
    (0xD, 0x38) : "Cmd_btl_38",
    (0xD, 0x39) : "Cmd_btl_39",
    (0xD, 0x3A) : "Cmd_btl_3A",
    (0xD, 0x3B) : "Cmd_btl_3B",
    (0xD, 0x3C) : "Cmd_btl_3C",
    (0xD, 0x3D) : "Cmd_btl_3D",
    (0xD, 0x3E) : "Cmd_btl_3E",
    (0xD, 0x3F) : "Cmd_btl_3F",
    (0xD, 0x40) : "Cmd_btl_40",
    (0xD, 0x41) : "Cmd_btl_41",
    (0xD, 0x42) : "Cmd_btl_42",
    (0xD, 0x43) : "Cmd_btl_43",
    (0xD, 0x44) : "Cmd_btl_44",
    (0xD, 0x45) : "Cmd_btl_45",
    (0xD, 0x46) : "Cmd_btl_46",
    (0xD, 0x47) : "Cmd_btl_47",
    (0xD, 0x48) : "Cmd_btl_48",
    (0xD, 0x49) : "Cmd_btl_49",
    (0xD, 0x4A) : "Cmd_btl_4A",
    (0xD, 0x4B) : "Cmd_btl_4B",
    (0xD, 0x4C) : "Cmd_btl_4C",
    (0xD, 0x4D) : "Cmd_btl_4D",
    (0xD, 0x4E) : "Cmd_btl_4E",
    (0xD, 0x4F) : "Cmd_btl_4F",
    (0xD, 0x50) : "Cmd_btl_50",
    (0xD, 0x51) : "Cmd_btl_51",
    (0xD, 0x52) : "Cmd_btl_52",
    (0xD, 0x53) : "Cmd_btl_53",
    (0xD, 0x54) : "Cmd_btl_54",
    (0xD, 0x55) : "Cmd_btl_55",
    (0xD, 0x56) : "Cmd_btl_56",
    (0xD, 0x57) : "Cmd_btl_57",
    (0xD, 0x58) : "Cmd_btl_58",
    (0xD, 0x59) : "Cmd_btl_59",
    (0xD, 0x5A) : "Cmd_btl_5A",
    (0xD, 0x5B) : "Cmd_btl_5B",
    (0xD, 0x5C) : "Cmd_btl_5C",
    (0xD, 0x5D) : "Cmd_btl_5D",
	(0xD, 0x5E) : "Cmd_btl_5E",
	(0xD, 0x5F) : "Cmd_btl_5F",
	(0xD, 0x60) : "Cmd_btl_60",
	(0xD, 0x61) : "Cmd_btl_61",
	(0xD, 0x62) : "Cmd_btl_62",
	(0xD, 0x63) : "Cmd_btl_63",
    (0xD, 0x64) : "Cmd_btl_64",
    (0xE, 0x00) : "Cmd_unknown_5_00",
    (0xE, 0x01) : "Cmd_unknown_5_01",
    (0xE, 0x02) : "Cmd_unknown_5_02",
    (0xE, 0x03) : "Cmd_unknown_5_03",
    (0xE, 0x04) : "Cmd_unknown_5_04",
    (0xE, 0x05) : "Cmd_unknown_5_05",
    (0xE, 0x06) : "Cmd_unknown_5_06",
    (0xE, 0x07) : "Cmd_unknown_5_07",
    (0xE, 0x08) : "Cmd_unknown_5_08",
    (0xE, 0x09) : "Cmd_unknown_5_09",
    (0xE, 0x0A) : "Cmd_unknown_5_0A",
    (0xE, 0x0B) : "Cmd_unknown_5_0B",
    (0xE, 0x0C) : "Cmd_unknown_5_0C",
    (0xE, 0x0D) : "Cmd_unknown_5_0D",
    (0xE, 0x0E) : "Cmd_unknown_5_0E",
    (0xE, 0x0F) : "Cmd_unknown_5_0F",
    (0xE, 0x10) : "Cmd_unknown_5_10",
    (0xE, 0x11) : "Cmd_unknown_5_11",
    (0xE, 0x12) : "Cmd_unknown_5_12",
    (0xE, 0x13) : "Cmd_unknown_5_13",
    (0xE, 0x14) : "Cmd_unknown_5_14",
    (0xE, 0x15) : "Cmd_unknown_5_15",
    (0xE, 0x16) : "Cmd_unknown_5_16",
    (0xE, 0x17) : "Cmd_unknown_5_17",
    (0xE, 0x18) : "Cmd_unknown_5_18",
    (0xE, 0x19) : "Cmd_unknown_5_19",
    (0xE, 0x1A) : "Cmd_unknown_5_1A",
    (0xE, 0x1B) : "Cmd_unknown_5_1B",
    (0xE, 0x1C) : "Cmd_unknown_5_1C",
    (0xF, 0x00) : "Cmd_menu_00",
    (0xF, 0x01) : "AddItemToMenu",
    (0xF, 0x02) : "OpenMenu",
    (0xF, 0x03) : "CloseMenu",
    (0xF, 0x04) : "Cmd_menu_04",
    (0xF, 0x05) : "Cmd_menu_05",
    (0xF, 0x06) : "Cmd_menu_06",
    (0xF, 0x07) : "Cmd_menu_07",
    (0xF, 0x08) : "Cmd_menu_08",
    (0x10, 0x00) : "Cmd_unknown_6_00",
    (0x10, 0x01) : "Cmd_unknown_6_01",
    (0x10, 0x02) : "Cmd_unknown_6_02",
    (0x10, 0x03) : "Cmd_unknown_6_03",
    (0x10, 0x04) : "Cmd_unknown_6_04",
    (0x10, 0x05) : "Cmd_unknown_6_05",
    (0x10, 0x06) : "Cmd_unknown_6_06",
    (0x10, 0x07) : "Cmd_unknown_6_07",
    (0x10, 0x08) : "Cmd_unknown_6_08",
    (0x10, 0x09) : "Cmd_unknown_6_09",
    (0x10, 0x0A) : "Cmd_unknown_6_0A",
    (0x10, 0x0B) : "Cmd_unknown_6_0B",
    (0x10, 0x0C) : "Cmd_unknown_6_0C",
    (0x10, 0x0D) : "Cmd_unknown_6_0D",
    (0x10, 0x0E) : "Cmd_unknown_6_0E",
    (0x10, 0x0F) : "Cmd_unknown_6_0F",
    (0x10, 0x10) : "Cmd_unknown_6_10",
    (0x10, 0x11) : "Cmd_unknown_6_11",
    (0x10, 0x12) : "Cmd_unknown_6_12",
    (0x10, 0x13) : "Cmd_unknown_6_13",
    (0x11, 0x00) : "Cmd_unknown_7_00",
    (0x11, 0x01) : "Cmd_unknown_7_01",
    (0x11, 0x02) : "Cmd_unknown_7_02",
    (0x11, 0x03) : "Cmd_unknown_7_03",
    (0x11, 0x04) : "Cmd_unknown_7_04",
    (0x12, 0x00)   : "Cmd_portraits_00",
    (0x12, 0x01)   : "Cmd_portraits_01",
    (0x12, 0x02)   : "Cmd_portraits_02",
    (0x12, 0x03)   : "Cmd_portraits_03",
    (0x12, 0x04)   : "Cmd_portraits_04",
    (0x12, 0x05)   : "Cmd_portraits_05",
    (0x12, 0x06)   : "Cmd_portraits_06",
    (0x12, 0x07)   : "Cmd_portraits_07",
    (0x12, 0x08)   : "Cmd_portraits_08",
    (0x12, 0x09)   : "Cmd_portraits_09",
    (0x12, 0x0A)   : "Cmd_portraits_0A",
    (0x12, 0x0B)   : "Cmd_portraits_0B",
    (0x12, 0x0C)   : "Cmd_portraits_0C",
    (0x13, 0x00) : "Cmd_unknown_8_00", 
    (0x13, 0x01) : "Cmd_unknown_8_01", 
    (0x13, 0x02) : "Cmd_unknown_8_02", 
    (0x13, 0x03) : "Cmd_unknown_8_03", 
    (0x13, 0x04) : "Cmd_unknown_8_04", 
    (0x13, 0x05) : "Cmd_unknown_8_05", 
    (0x13, 0x06) : "Cmd_unknown_8_06", 
    (0x13, 0x07) : "Cmd_unknown_8_07", 
    (0x13, 0x08) : "Cmd_unknown_8_08", 
    (0x13, 0x09) : "Cmd_unknown_8_09", 
    (0x13, 0x0A) : "Cmd_unknown_8_0A", 
    (0x13, 0x0B) : "Cmd_unknown_8_0B", 
    (0x13, 0x0C) : "Cmd_unknown_8_0C", 
    (0x13, 0x0D) : "Cmd_unknown_8_0D", 
    (0x13, 0x0E) : "Cmd_unknown_8_0E", 
    (0x13, 0x0F) : "Cmd_unknown_8_0F", 
    (0x13, 0x10) : "Cmd_unknown_8_10", 
    (0x13, 0x11) : "Cmd_unknown_8_11", 
    (0x13, 0x12) : "Cmd_unknown_8_12", 
    (0x13, 0x13) : "Cmd_unknown_8_13", 
    (0x13, 0x14) : "Cmd_unknown_8_14",
    (0x14, 0x00) : "Cmd_activevoice_00", 
    (0x14, 0x01) : "Cmd_activevoice_01", 
    (0x14, 0x02) : "Cmd_activevoice_02", 
    (0x14, 0x03) : "Cmd_activevoice_03",
    (0x15, 0x00) : "Cmd_unknown_9_00", 
    (0x15, 0x01) : "Cmd_unknown_9_01", 
    (0x16, 0x00)  : "Cmd_mapjump_00",
    (0x16, 0x01)  : "Cmd_mapjump_01",
    (0x16, 0x02)  : "Cmd_mapjump_02",
    (0x16, 0x03)  : "Cmd_mapjump_03",
    (0x16, 0x04)  : "Cmd_mapjump_04",
    (0x16, 0x05)  : "Cmd_mapjump_05",
    (0x16, 0x06)  : "Cmd_mapjump_06",
    (0x16, 0x07)  : "Cmd_mapjump_07",
    (0x16, 0x08)  : "Cmd_mapjump_08",
    (0x16, 0x09)  : "Cmd_mapjump_09",
    (0x16, 0x0A)  : "Cmd_mapjump_0A",
    (0x16, 0x0B)  : "Cmd_mapjump_0B",
    (0x16, 0x0C)  : "Cmd_mapjump_0C",
    (0x16, 0x0D)  : "Cmd_mapjump_0D",
    (0x16, 0x0E)  : "Cmd_mapjump_0E",
    (0x16, 0x0F)  : "Cmd_mapjump_0F",
    (0x16, 0x10)  : "Cmd_mapjump_10", 
    (0x17, 0x00)  : "Cmd_ui_00",
    (0x17, 0x01)  : "Cmd_ui_01",
    (0x17, 0x02)  : "Cmd_ui_02",
    (0x17, 0x03)  : "Cmd_ui_03",
    (0x17, 0x04)  : "Cmd_ui_04",
    (0x17, 0x05)  : "Cmd_ui_05",
    (0x17, 0x06)  : "Cmd_ui_06",
    (0x17, 0x07)  : "Cmd_ui_07",
    (0x17, 0x08)  : "Cmd_ui_08",
    (0x17, 0x09)  : "Cmd_ui_09",
    (0x17, 0x0A)  : "Cmd_ui_0A",
    (0x17, 0x0B)  : "Cmd_ui_0B",
    (0x17, 0x0C)  : "Cmd_ui_0C",
    (0x17, 0x0D)  : "Cmd_ui_0D",
    (0x17, 0x0E)  : "Cmd_ui_0E",
    (0x17, 0x0F)  : "Cmd_ui_0F",
    (0x17, 0x10)  : "Cmd_ui_10",
    (0x17, 0x11)  : "Cmd_ui_11",
    (0x17, 0x12)  : "Cmd_ui_12",
    (0x17, 0x13)  : "Cmd_ui_13",
    (0x17, 0x14)  : "Cmd_ui_14",
    (0x17, 0x15)  : "Cmd_ui_15",
    (0x17, 0x16)  : "Cmd_ui_16",
    (0x17, 0x17)  : "Cmd_ui_17",
    (0x17, 0x18)  : "Cmd_ui_18",
    (0x18, 0x00) : "Cmd_unknown_10_00", 
    (0x18, 0x01) : "Cmd_unknown_10_01", 
    (0x18, 0x02) : "Cmd_unknown_10_02", 
    (0x18, 0x03) : "Cmd_unknown_10_03", 
    (0x18, 0x04) : "Cmd_unknown_10_04", 
    (0x18, 0x05) : "Cmd_unknown_10_05", 
    (0x18, 0x06) : "Cmd_unknown_10_06", 
    (0x18, 0x07) : "Cmd_unknown_10_07", 
    (0x18, 0x08) : "Cmd_unknown_10_08", 
    (0x18, 0x09) : "Cmd_unknown_10_09", 
    (0x18, 0x0A) : "Cmd_unknown_10_0A", 
    (0x18, 0x0B) : "Cmd_unknown_10_0B", 
    (0x18, 0x0C) : "Cmd_unknown_10_0C", 
    (0x18, 0x0D) : "Cmd_unknown_10_0D", 
    (0x18, 0x0E) : "Cmd_unknown_10_0E",
    (0x19, 0x00) : "Cmd_battlestatus_00",
    (0x19, 0x01) : "Cmd_battlestatus_01",
    (0x19, 0x02) : "Cmd_battlestatus_02",
    (0x19, 0x03) : "Cmd_battlestatus_03",
    (0x19, 0x04) : "Cmd_battlestatus_04",
    (0x19, 0x05) : "Cmd_battlestatus_05",
    (0x19, 0x06) : "Cmd_battlestatus_06",
    (0x19, 0x07) : "Cmd_battlestatus_07",
    (0x19, 0x08) : "SetEquip",
    (0x19, 0x09) : "Cmd_battlestatus_09",
    (0x19, 0x0A) : "Cmd_battlestatus_0A",
    (0x19, 0x0B) : "Cmd_battlestatus_0B",
    (0x19, 0x0C) : "Cmd_battlestatus_0C",
    (0x19, 0x0D) : "Cmd_battlestatus_0D",
    (0x19, 0x0E) : "Cmd_battlestatus_0E",
    (0x19, 0x0F) : "Cmd_battlestatus_0F",
    (0x19, 0x10) : "Cmd_battlestatus_10",
    (0x19, 0x11) : "Cmd_battlestatus_11",
    (0x19, 0x12) : "Cmd_battlestatus_12",
    (0x19, 0x13) : "Cmd_battlestatus_13",
    (0x19, 0x14) : "Cmd_battlestatus_14",
    (0x19, 0x15) : "Cmd_battlestatus_15",
    (0x19, 0x16) : "Cmd_battlestatus_16",
    (0x19, 0x17) : "Cmd_battlestatus_17",
    (0x19, 0x18) : "Cmd_battlestatus_18",
    (0x19, 0x19) : "Cmd_battlestatus_19",
    (0x19, 0x1A) : "Cmd_battlestatus_1A",
    (0x19, 0x1B) : "Cmd_battlestatus_1B",
    (0x19, 0x1C) : "Cmd_battlestatus_1C",
    (0x19, 0x1D) : "Cmd_battlestatus_1D",
    (0x19, 0x1E) : "Cmd_battlestatus_1E",
    (0x19, 0x1F) : "Cmd_battlestatus_1F",
    (0x19, 0x20) : "Cmd_battlestatus_20",
	(0x19, 0x21) : "Cmd_battlestatus_21",
    (0x1A, 0x00) : "Cmd_shop_00",
    (0x1A, 0x01) : "Cmd_shop_01",
    (0x1A, 0x02) : "Cmd_shop_02",
    (0x1A, 0x03) : "Cmd_shop_03",
    (0x1A, 0x04) : "Cmd_shop_04",
    (0x1A, 0x05) : "Cmd_shop_05",
    (0x1A, 0x06) : "Cmd_shop_06",
    (0x1B, 0x00) : "Cmd_unknown_11_00",
    (0x1B, 0x01) : "Cmd_unknown_11_01",
    (0x1C, 0x00) : "Cmd_achievements_00",
    (0x1C, 0x01) : "Cmd_achievements_01",
    (0x1C, 0x02) : "Cmd_achievements_02",
    (0x1C, 0x03) : "Cmd_achievements_03",
	(0x1C, 0x04) : "Cmd_achievements_04",
    (0x1C, 0x05) : "Cmd_achievements_05",
    (0x1C, 0x06) : "Cmd_achievements_06",
    }
    
    reverse_commands_dict =  {v: k for k, v in commands_dict.items()}


locations_dict = {} #Address, LocationName
location_counter = 0
smallest_data_ptr = sys.maxsize #big enough
commands_dict = {}
reverse_commands_dict = {}

init_command_names_dicts()




class operand:
    def __init__(self, value, MSB_encoded):
        self.value = value
        self.MSB_encoded = MSB_encoded
        

def OP_0(instr, stream):
    global smallest_data_ptr

    size = readint(stream, 1)
    value = readint(stream, size)
    if (size == 4):
        
        type = identifytype(value)
        if (type == "undefined"):
            instr.name = "PUSHUNDEFINED"
        elif (type == "integer"):
            instr.name = "PUSHINTEGER"
        elif (type == "float"):
            instr.name = "PUSHFLOAT"
        elif (type == "string"):
            instr.name = "PUSHSTRING"
            actual_value = remove2MSB(value)
            if smallest_data_ptr > actual_value:
                smallest_data_ptr = actual_value

    instr.operands.append(operand(value, True))

def OP_1(instr, stream):
    
    size = readint(stream, 1)
    instr.name = "POP"
    instr.operands.append(operand(size, False))

def OP_2(instr, stream):
    
    index = readint(stream, 4, signed=True)

    instr.name = "RETRIEVEELEMENTATINDEX"
    instr.operands.append(operand(index, False))

def OP_3(instr, stream):
    
    index = readint(stream, 4, signed=True)

    instr.name = "RETRIEVEELEMENTATINDEX2"
    instr.operands.append(operand(index, False))

def OP_4(instr, stream):
    
    index = readint(stream, 4, signed=True)

    instr.name = "PUSHCONVERTINTEGER"
    instr.operands.append(operand(index, False))

def OP_5(instr, stream):
    
    index = readint(stream, 4, signed=True)

    instr.name = "PUTBACKATINDEX"
    instr.operands.append(operand(index, False))

def OP_6(instr, stream):
    
    index = readint(stream, 4, signed=True)

    instr.name = "PUTBACK"
    instr.operands.append(operand(index, False))

def OP_7(instr, stream):
    
    index = readint(stream, 4, signed=True)

    instr.name = "LOAD32"
    instr.operands.append(operand(index, False))

def OP_8(instr, stream):
    
    index = readint(stream, 4, signed=True)

    instr.name = "STORE32"
    instr.operands.append(operand(index, False))

def OP_9(instr, stream):
    
    index = readint(stream, 1)

    instr.name = "LOADRESULT"
    instr.operands.append(operand(index, False))

def OP_A(instr, stream):
    
    index = readint(stream, 1)

    instr.name = "SAVERESULT"
    instr.operands.append(operand(index, False))

def OP_B(instr, stream):
    global location_counter
    global locations_dict

    addr = readint(stream, 4)

    instr.name = "JUMP"
    if addr in locations_dict: #A jump exists already to this location
        label = locations_dict[addr]
    else:
        label = "Loc_"+ str(location_counter)
        locations_dict[addr] = label
        location_counter = location_counter + 1

    instr.operands.append(operand(label, False))

def OP_C(instr, stream):
    
    function_index = readint(stream, 2)

    instr.name = "CALL"

    instr.operands.append(operand(function_index, False))

def OP_D(instr, stream):
    
    instr.name = "EXIT"

def OP_E(instr, stream):
    global location_counter
    global locations_dict

    instr.name = "JUMPIFFALSE"
    addr = readint(stream, 4)
    if addr in locations_dict:
        label = locations_dict[addr]
    else:
        label = "Loc_"+ str(location_counter)
        locations_dict[addr] = label
        location_counter = location_counter + 1

    instr.operands.append(operand(label, False))

def OP_F(instr, stream):
    global location_counter
    global locations_dict

    instr.name = "JUMPIFTRUE"
    addr = readint(stream, 4)
    if addr in locations_dict:
        label = locations_dict[addr]
    else:
        label = "Loc_"+ str(location_counter)
        locations_dict[addr] = label
        location_counter = location_counter + 1

    instr.operands.append(operand(label, False))

def OP_10(instr, stream):

    instr.name = "ADD"
def OP_11(instr, stream):

    instr.name = "SUBTRACT"
def OP_12(instr, stream):

    instr.name = "MULTIPLY"
def OP_13(instr, stream):

    instr.name = "DIVIDE"
def OP_14(instr, stream):

    instr.name = "MODULO"
def OP_15(instr, stream):

    instr.name = "EQUAL"
def OP_16(instr, stream):

    instr.name = "NONEQUAL"
def OP_17(instr, stream):

    instr.name = "GREATERTHAN"
def OP_18(instr, stream):

    instr.name = "GREATEROREQ"
def OP_19(instr, stream):

    instr.name = "LOWERTHAN"
def OP_1A(instr, stream):

    instr.name = "LOWEROREQ"
def OP_1B(instr, stream):

    instr.name = "AND_"
def OP_1C(instr, stream):

    instr.name = "OR1"
def OP_1D(instr, stream):

    instr.name = "OR2"
def OP_1E(instr, stream):

    instr.name = "OR3"
def OP_1F(instr, stream):

    instr.name = "NEGATIVE"
def OP_20(instr, stream):

    instr.name = "ISTRUE"
def OP_21(instr, stream):

    instr.name = "XOR1"
def OP_22(instr, stream):
    global smallest_data_ptr

    value = readint(stream, 4)
    instr.operands.append(operand(value, True))
    actual_value = remove2MSB(value)
    if smallest_data_ptr > actual_value:
        smallest_data_ptr = actual_value

    value = readint(stream, 4)
    instr.operands.append(operand(value, True))
    actual_value = remove2MSB(value)
    if smallest_data_ptr > actual_value:
        smallest_data_ptr = actual_value
    nb_args = readint(stream, 1)
    instr.operands.append(operand(nb_args, False))
    instr.name = "CALLFROMANOTHERSCRIPT"
def OP_23(instr, stream):
    global smallest_data_ptr

    value = readint(stream, 4)
    instr.operands.append(operand(value, True))
    actual_value = remove2MSB(value)
    if smallest_data_ptr > actual_value:
        smallest_data_ptr = actual_value

    value = readint(stream, 4)
    instr.operands.append(operand(value, True))
    actual_value = remove2MSB(value)
    if smallest_data_ptr > actual_value:
        smallest_data_ptr = actual_value
    nb_args = readint(stream, 1)
    instr.operands.append(operand(nb_args, False))
    instr.name = "CALLFROMANOTHERSCRIPT2"
def OP_24(instr, stream):
    global command_dicts
    structID = readint(stream, 1)
    command_op_code = readint(stream, 1)
    nb_args = readint(stream, 1)
    

    instr.name = "RUNCMD"
    
    instr.operands.append(operand(nb_args, False)) 
    instr.operands.append(operand(commands_dict[(structID,command_op_code)], False)) #The user needs the number of arguments since it's not really apparent for the moment

def OP_25(instr, stream): #Not sure if it's a jump here, but it's pointing to some instruction, and we need to record that to update later
    global location_counter
    global locations_dict
    addr = readint(stream, 4)
    #if addr in locations_dict:
    #    label = locations_dict[addr]
    #else:
    #    label = "Loc_"+ str(location_counter)
    #    locations_dict[addr] = label
    #    location_counter = location_counter + 1

    instr.operands.append(operand(addr, False))
    instr.name = "PUSHRETURNADDRESSFROMANOTHERSCRIPT"

def OP_26(instr, stream):
    value = readint(stream, 2)
    instr.operands.append(operand(value, False))
    instr.name = "ADDLINEMARKER"

    
def OP_27(instr, stream):
    value = readint(stream, 1)
    instr.operands.append(operand(value, False))
    instr.name = "POP2"

def OP_28(instr, stream):
    value = readint(stream, 4)
    instr.operands.append(operand(vakye, False))
    instr.name = "DEBUG"

instruction_set = {0 : OP_0,
                   1 : OP_1,
                   2 : OP_2,
                   3 : OP_3,
                   4 : OP_4,
                   5 : OP_5,
                   6 : OP_6,
                   7 : OP_7,
                   8 : OP_8,
                   9 : OP_9,
                   0xA : OP_A,
                   0xB : OP_B,
                   0xC : OP_C,
                   0xD : OP_D,
                   0xE : OP_E,
                   0xF : OP_F,
                   0x10 : OP_10,
                   0x11 : OP_11,
                   0x12 : OP_12,
                   0x13 : OP_13,
                   0x14 : OP_14,
                   0x15 : OP_15,
                   0x16 : OP_16,
                   0x17 : OP_17,
                   0x18 : OP_18,
                   0x19 : OP_19,
                   0x1A : OP_1A,
                   0x1B : OP_1B,
                   0x1C : OP_1C,
                   0x1D : OP_1D,
                   0x1E : OP_1E,
                   0x1F : OP_1F,
                   0x20 : OP_20,
                   0x21 : OP_21,
                   0x22 : OP_22,
                   0x23 : OP_23,
                   0x24 : OP_24,
                   0x25 : OP_25,
                   0x26 : OP_26,
                   0x27 : OP_27,
                   0x28 : OP_28,
}



class instruction(object):
    """description of class"""
    def __init__(self, stream, op_code):
        self.addr = stream.tell() - 1 #minus opcode
        self.op_code = op_code
        self.operands = []
        self.name = ""
        self.text_before = ""


        instruction_set[op_code](self, stream)


    def to_string(self, stream)->str:
        result = self.text_before + self.name + "("
        for operand_id in range(len(self.operands)-1):
            value = self.operands[operand_id].value
            if (type(value) == str):
                result = result + "\"" + value + "\""
            else:
                if self.operands[operand_id].MSB_encoded == True:
                    result = result + get_actual_value_str(stream, value)
                else:
                    result = result + str(int(value))
            result = result + ", "
        if len(self.operands) > 0:
            value = self.operands[len(self.operands)-1].value
            if (type(value) == str):
                result = result + "\"" + value + "\""
            else:
                if self.operands[len(self.operands)-1].MSB_encoded == True:
                    result = result + get_actual_value_str(stream, value)
                else:
                    result = result + str(int(value))
        result = result + ")"
        return result




