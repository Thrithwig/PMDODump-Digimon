"""Execute the shipped Lua scripts in the same Lua 5.4 native VM used by PMDC."""
import ctypes
import json
from pathlib import Path
import unittest

from Scripts.digimon_terminal_catalog import render

ROOT = Path(__file__).resolve().parents[1]


class TerminalTests(unittest.TestCase):
    def test_catalog_matches_source_and_overlay(self):
        data = ROOT / "DataAsset" / "Digimon"
        expected = render(json.loads((data / "phase2_manifest.json").read_text()),
                          json.loads((data / "phase1_overlay.json").read_text()))
        self.assertEqual((ROOT / "DumpAsset/Data/Script/origin/digimon/catalog.lua").read_text(), expected)

    def test_runtime_lua_scenarios_and_changed_script_syntax(self):
        path = ROOT / "PMDC/PMDC/runtimes/win-x64/native/lua54.dll"
        lua = ctypes.CDLL(str(path))
        lua.luaL_newstate.restype = ctypes.c_void_p
        lua.luaL_openlibs.argtypes = [ctypes.c_void_p]
        lua.luaL_loadstring.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        lua.luaL_loadstring.restype = ctypes.c_int
        lua.lua_pcallk.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ssize_t, ctypes.c_void_p]
        lua.lua_pcallk.restype = ctypes.c_int
        lua.lua_tolstring.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
        lua.lua_tolstring.restype = ctypes.c_char_p
        lua.lua_close.argtypes = [ctypes.c_void_p]
        state = lua.luaL_newstate()
        self.assertTrue(state)
        try:
            lua.luaL_openlibs(state)
            scripts = ROOT / "DumpAsset/Data/Script"
            code = "package.path = " + json.dumps(scripts.as_posix() + "/?.lua;" + scripts.as_posix() + "/?/init.lua;") + " .. package.path\n"
            for relative in ("origin/common.lua", "origin/digimon/evolution_preview.lua", "origin/digimon/item_effects.lua", "origin/digimon/story_missions.lua", "origin/event_battle.lua", "origin/ground/luminous_spring/init.lua", "origin/scriptvars.lua", "origin/event_single.lua", "origin/zone/tropical_path/init.lua", "origin/zone/faultline_ridge/init.lua", "origin/zone/trickster_woods/init.lua", "origin/digimon/progression.lua", "origin/digimon/farm.lua", "origin/digimon/terminal.lua", "origin/services/digimon_runtime/init.lua"):
                code += "assert(loadfile(" + json.dumps((scripts / relative).as_posix()) + "))\n"
            code += "dofile(" + json.dumps((ROOT / "tests/lua/test_digimon_terminal.lua").as_posix()) + ")"
            code += "\ndofile(" + json.dumps((ROOT / "tests/lua/test_digimon_runtime.lua").as_posix()) + ")"
            code += "\ndofile(" + json.dumps((ROOT / "tests/lua/test_digimon_story_missions.lua").as_posix()) + ")"
            common = (scripts / 'origin/common.lua').read_text(encoding='utf-8-sig')
            menu = common[common.index('function COMMON.ShowDestinationMenu('):common.index('function COMMON.CreateWalkArea(')]
            code += '\n' + menu
            code += "\ndofile(" + json.dumps((ROOT / "tests/lua/test_digimon_access.lua").as_posix()) + ")"
            result = lua.luaL_loadstring(state, code.encode())
            if result == 0:
                result = lua.lua_pcallk(state, 0, 0, 0, 0, None)
            error = lua.lua_tolstring(state, -1, None) if result else b""
            self.assertEqual(result, 0, error.decode("utf-8", errors="replace"))
        finally:
            lua.lua_close(state)


if __name__ == "__main__":
    unittest.main()
