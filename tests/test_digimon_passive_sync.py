"""Run save-migration mocks against the shipped Lua passive synchronization code."""
import ctypes
import json
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class PassiveSyncTests(unittest.TestCase):
    def test_party_and_assembly_passive_migration(self):
        lua=ctypes.CDLL(str(ROOT/'PMDC/PMDC/runtimes/win-x64/native/lua54.dll'))
        lua.luaL_newstate.restype=ctypes.c_void_p
        lua.luaL_openlibs.argtypes=[ctypes.c_void_p]
        lua.luaL_loadstring.argtypes=[ctypes.c_void_p,ctypes.c_char_p]
        lua.luaL_loadstring.restype=ctypes.c_int
        lua.lua_pcallk.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_ssize_t,ctypes.c_void_p]
        lua.lua_pcallk.restype=ctypes.c_int
        lua.lua_tolstring.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p]
        lua.lua_tolstring.restype=ctypes.c_char_p
        lua.lua_close.argtypes=[ctypes.c_void_p]
        state=lua.luaL_newstate()
        self.assertTrue(state)
        try:
            lua.luaL_openlibs(state)
            scripts=ROOT/'DumpAsset/Data/Script'
            code='package.path = '+json.dumps(scripts.as_posix()+'/?.lua;'+scripts.as_posix()+'/?/init.lua;')+' .. package.path\n'
            code+='dofile('+json.dumps((ROOT/'tests/lua/test_digimon_passive_sync.lua').as_posix())+')'
            result=lua.luaL_loadstring(state,code.encode())
            if result==0: result=lua.lua_pcallk(state,0,0,0,0,None)
            error=lua.lua_tolstring(state,-1,None) if result else b''
            self.assertEqual(result,0,error.decode('utf-8',errors='replace'))
        finally:
            lua.lua_close(state)
