#!/usr/bin/env python3
"""
Discord Fake Game Player (Game Variety Badge / Polymath)
Otomatis mainkan game tiruan (dummy process + Discord IPC)
untuk menyelesaikan badge Discord Game Variety.

Fitur:
- Durasi otomatis 20 menit per game (dapat disesuaikan)
- Pilihan 100+ Game Populer atau Seluruh Database Discord (10.000+ game)
- Pemilihan acak (Shuffle tanpa duplikasi - pasti semua dapat)
- Pelacakan riwayat game yang sudah dimainkan (played_history.json)
- Standard Library Only (Tanpa pip install)
"""

import os
import sys
import time
import json
import struct
import shutil
import random
import tempfile
import subprocess
import urllib.request
from pathlib import Path

# Durasi bawaan 20 menit (1200 detik)
DEFAULT_DURATION = 20 * 60

HISTORY_FILE = "played_history.json"
CACHE_FILE = "detectable_cache.json"

# Daftar 107 Game Terverifikasi Resmi Discord (Populer & Lengkap)
DETECTABLE_GAMES = [
    {"name": "Overwatch", "id": "356875221078245376", "exe": "overwatch.exe"},
    {"name": "The Binding of Isaac: Rebirth", "id": "358420454764969994", "exe": "isaac-ng.exe"},
    {"name": "Fallout 4", "id": "359509759642042378", "exe": "fallout4.exe"},
    {"name": "Dota 2", "id": "356875988589740042", "exe": "dota2.exe"},
    {"name": "Rocket League", "id": "356877880938070016", "exe": "rocketleague.exe"},
    {"name": "Terraria", "id": "1402418344912752671", "exe": "terraria.exe"},
    {"name": "Bloons TD 6", "id": "1402418571715543120", "exe": "bloonstd6.exe"},
    {"name": "Among Us", "id": "1402418440685486130", "exe": "among us/among us.exe"},
    {"name": "World of Tanks", "id": "1402418078813523999", "exe": "worldoftanks.exe"},
    {"name": "The First Descendant", "id": "1256912167685587034", "exe": "m1-win64-shipping.exe"},
    {"name": "Sid Meier's Civilization VI", "id": "363413834301571072", "exe": "civilizationvi.exe"},
    {"name": "Call of Duty: Black Ops III", "id": "359509332490059776", "exe": "blackops3.exe"},
    {"name": "Monster Hunter: World", "id": "477152881196269569", "exe": "monsterhunterworld.exe"},
    {"name": "Genshin Impact", "id": "762434991303950386", "exe": "genshinimpact.exe"},
    {"name": "Battlefield 2042", "id": "1162076274622222346", "exe": "battlefield 2042/bf2042.exe"},
    {"name": "Red Dead Redemption 2", "id": "1402418648332898466", "exe": "red dead redemption 2/rdr2.exe"},
    {"name": "Krita", "id": "1124353632758939688", "exe": "bin/krita.exe"},
    {"name": "Counter-Strike 2", "id": "356875569427906560", "exe": "win64/cs2.exe"},
    {"name": "VALORANT", "id": "700144983058874428", "exe": "win64/valorant-win64-shipping.exe"},
    {"name": "Cyberpunk 2077", "id": "439169601008566273", "exe": "cyberpunk2077.exe"},
    {"name": "Apex Legends", "id": "542075586886107149", "exe": "apex/r5apex.exe"},
    {"name": "PUBG: BATTLEGROUNDS", "id": "356875883203657738", "exe": "win64/tslgame.exe"},
    {"name": "Elden Ring", "id": "890251147577544714", "exe": "game/eldenring.exe"},
    {"name": "Baldur's Gate 3", "id": "762002517868544020", "exe": "bin/bg3_dx11.exe"},
    {"name": "Palworld", "id": "1197775514652250162", "exe": "wingdk/palworld-wingdk-shipping.exe"},
    {"name": "Lethal Company", "id": "1168925345672613919", "exe": "lethal company.exe"},
    {"name": "Helldivers 2", "id": "1203010729792901170", "exe": "bin/helldivers2.exe"},
    {"name": "Phasmophobia", "id": "761623912189919242", "exe": "phasmophobia.exe"},
    {"name": "Rust", "id": "356875704169922570", "exe": "rustclient.exe"},
    {"name": "Dead by Daylight", "id": "356877073715167232", "exe": "deadby daylight/binaries/win64/deadbydaylight-win64-shipping.exe"},
    {"name": "Stardew Valley", "id": "356876352932413441", "exe": "stardew valley.exe"},
    {"name": "Hollow Knight", "id": "363413554495488000", "exe": "hollow_knight.exe"},
    {"name": "Hades", "id": "522137953258766347", "exe": "x64/hades.exe"},
    {"name": "Tom Clancy's Rainbow Six Siege", "id": "356876121406832640", "exe": "rainbowsix.exe"},
    {"name": "Destiny 2", "id": "356876229984518144", "exe": "destiny2.exe"},
    {"name": "Warframe", "id": "356876527587164160", "exe": "warframe.x64.exe"},
    {"name": "Sea of Thieves", "id": "358421868350537728", "exe": "athena/binaries/win64/seaofthieves.exe"},
    {"name": "Grand Theft Auto V", "id": "356876800720502784", "exe": "gta5.exe"},
    {"name": "Forza Horizon 5", "id": "893949811563032607", "exe": "forzahorizon5.exe"},
    {"name": "Euro Truck Simulator 2", "id": "363413988673060864", "exe": "bin/win_x64/eurotrucks2.exe"},
    {"name": "Left 4 Dead 2", "id": "356877232800661504", "exe": "left4dead2.exe"},
    {"name": "Team Fortress 2", "id": "356876930504720384", "exe": "hl2.exe"},
    {"name": "Garry's Mod", "id": "356877484643450880", "exe": "gmod.exe"},
    {"name": "Don't Starve Together", "id": "358421375251382272", "exe": "bin64/dontstarve_steam_x64.exe"},
    {"name": "PAYDAY 2", "id": "356877718018457600", "exe": "payday2_win32_release.exe"},
    {"name": "Subnautica", "id": "358420658700255232", "exe": "subnautica.exe"},
    {"name": "ARK: Survival Evolved", "id": "356876646571180032", "exe": "shootergame/binaries/win64/shootergame.exe"},
    {"name": "The Forest", "id": "358420958106714112", "exe": "theforest.exe"},
    {"name": "Sons of the Forest", "id": "1078652399993880596", "exe": "sonsoftheforest.exe"},
    {"name": "Slay the Spire", "id": "404022444530597899", "exe": "slaythespire.exe"},
    {"name": "Celeste", "id": "410534241680883712", "exe": "celeste.exe"},
    {"name": "Cuphead", "id": "363413344155336704", "exe": "cuphead.exe"},
    {"name": "Undertale", "id": "358421115854487552", "exe": "undertale.exe"},
    {"name": "Factorio", "id": "358420790757785600", "exe": "bin/x64/factorio.exe"},
    {"name": "RimWorld", "id": "358421639912226816", "exe": "rimworldwin64.exe"},
    {"name": "Cities: Skylines", "id": "358420542371495936", "exe": "cities.exe"},
    {"name": "Project Zomboid", "id": "358421757885415424", "exe": "projectzomboid64.exe"},
    {"name": "Deep Rock Galactic", "id": "418464673894105088", "exe": "fsd/binaries/win64/fsd-win64-shipping.exe"},
    {"name": "Risk of Rain 2", "id": "560548174486503434", "exe": "risk of rain 2.exe"},
    {"name": "Monster Hunter Rise", "id": "926590823334547466", "exe": "monsterhunterrise.exe"},
    {"name": "Dark Souls III", "id": "358421257403760640", "exe": "darksoulsiii.exe"},
    {"name": "Sekiro: Shadows Die Twice", "id": "558719266157821952", "exe": "sekiro.exe"},
    {"name": "Lies of P", "id": "1153443153676865677", "exe": "cp/binaries/win64/lop-win64-shipping.exe"},
    {"name": "Arma 3", "id": "356877342938890240", "exe": "arma3_x64.exe"},
    {"name": "Hearts of Iron IV", "id": "363413708304678912", "exe": "hoi4.exe"},
    {"name": "Stellaris", "id": "363413778508939264", "exe": "stellaris.exe"},
    {"name": "Crusader Kings III", "id": "750796335128641577", "exe": "binaries/ck3.exe"},
    {"name": "Mount & Blade II: Bannerlord", "id": "694314488341626910", "exe": "bin/win64_shipping_client/bannerlord.exe"},
    {"name": "No Man's Sky", "id": "356877602322907136", "exe": "binaries/nms.exe"},
    {"name": "Starfield", "id": "1147572791881764954", "exe": "starfield.exe"},
    {"name": "Fallout: New Vegas", "id": "363414073574162432", "exe": "falloutnv.exe"},
    {"name": "The Elder Scrolls V: Skyrim", "id": "356876442656702464", "exe": "tesv.exe"},
    {"name": "The Witcher 3: Wild Hunt", "id": "356876043237588992", "exe": "bin/x64/witcher3.exe"},
    {"name": "God of War", "id": "931238100586074122", "exe": "gow.exe"},
    {"name": "Horizon Zero Dawn", "id": "741406450143854652", "exe": "horizonzerodawn.exe"},
    {"name": "Death Stranding", "id": "733051405979615243", "exe": "ds.exe"},
    {"name": "Control", "id": "616016738416525332", "exe": "control_dx12.exe"},
    {"name": "Resident Evil 4", "id": "1088924619437645854", "exe": "re4.exe"},
    {"name": "Resident Evil Village", "id": "840280829807558666", "exe": "re8.exe"},
    {"name": "Street Fighter 6", "id": "1114258359487561848", "exe": "streetfighter6.exe"},
    {"name": "Tekken 8", "id": "1199738096174895104", "exe": "polaris/binaries/win64/polaris-win64-shipping.exe"},
    {"name": "Mortal Kombat 1", "id": "1153443153676865677", "exe": "mk12/binaries/win64/mk12.exe"},
    {"name": "Guilty Gear -Strive-", "id": "852613589998108712", "exe": "red/binaries/win64/ggst-win64-shipping.exe"},
    {"name": "Brawlhalla", "id": "358421487889416192", "exe": "brawlhalla.exe"},
    {"name": "Roblox", "id": "439223656200273931", "exe": "robloxplayerbeta.exe"},
    {"name": "osu!", "id": "356877983228887040", "exe": "osu!.exe"},
    {"name": "Honkai: Star Rail", "id": "1098679075775594586", "exe": "starrail.exe"},
    {"name": "Zenless Zone Zero", "id": "1258169123851079730", "exe": "zenlesszonezero.exe"},
    {"name": "Vampire Survivors", "id": "933068032542998599", "exe": "vampiresurvivors.exe"},
    {"name": "Dave the Diver", "id": "1124443652878520330", "exe": "davethediver.exe"},
    {"name": "Balatro", "id": "1209594191316258816", "exe": "balatro.exe"},
    {"name": "Content Warning", "id": "1224419918079557672", "exe": "content warning.exe"},
    {"name": "Chained Together", "id": "1253412587572629554", "exe": "chainedtogether/binaries/win64/chainedtogether-win64-shipping.exe"},
    {"name": "Supermarket Simulator", "id": "1211756461991395378", "exe": "supermarket simulator.exe"},
    {"name": "Manor Lords", "id": "1233075252876644402", "exe": "manorlords/binaries/win64/manorlords-win64-shipping.exe"},
    {"name": "Ready or Not", "id": "921869818812854342", "exe": "readyornot/binaries/win64/readyornot-win64-shipping.exe"},
    {"name": "Squad", "id": "358421037429391360", "exe": "squadgame/binaries/win64/squadgame.exe"},
    {"name": "Assetto Corsa", "id": "363413444474961920", "exe": "acs.exe"},
    {"name": "BeamNG.drive", "id": "363413628797452288", "exe": "bin64/beamng.drive.x64.exe"},
    {"name": "Farming Simulator 22", "id": "912383272938262538", "exe": "x64/farmingsimulator2022game.exe"},
    {"name": "Microsoft Flight Simulator", "id": "745722302381293628", "exe": "flightsimulator.exe"},
    {"name": "Geometry Dash", "id": "358421976077303808", "exe": "geometrydash.exe"},
    {"name": "Portal 2", "id": "356877151049351168", "exe": "portal2.exe"},
    {"name": "Half-Life 2", "id": "356876878436499456", "exe": "hl2.exe"},
    {"name": "Brotato", "id": "1024388836567941160", "exe": "brotato.exe"},
    {"name": "Enter the Gungeon", "id": "358420875969560576", "exe": "etg.exe"}
]

def load_history():
    """Memuat daftar game yang sudah pernah dimainkan sebelumnya."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_history(history_set):
    """Menyimpan riwayat game yang sudah dimainkan."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(list(history_set), f, indent=2)
    except Exception:
        pass

def load_all_detectable_games():
    """Memuat semua game dari cache lokal (10.000+ game) atau download jika belum ada."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if len(data) > 0:
                    return data
        except Exception:
            pass

    print("[*] Mengunduh database lengkap game terdeteksi dari Discord API...")
    try:
        req = urllib.request.Request(
            "https://discord.com/api/v9/applications/detectable",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
        
        extracted = []
        seen = set()
        for item in raw:
            name = item.get("name", "").strip()
            gid = item.get("id", "")
            if not name or name in seen:
                continue
            execs = item.get("executables", [])
            win_execs = [e.get("name") for e in execs if e.get("os") == "win32" and not e.get("is_launcher")]
            if not win_execs:
                win_execs = [e.get("name") for e in execs if e.get("os") == "win32"]
            if win_execs:
                seen.add(name)
                extracted.append({"name": name, "id": gid, "exe": win_execs[0]})
        
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(extracted, f, indent=2)
        print(f"[✓] Berhasil memuat {len(extracted)} game ke dalam cache!")
        return extracted
    except Exception as e:
        print(f"[-] Gagal mengunduh database lengkap ({e}). Menggunakan daftar bawaan ({len(DETECTABLE_GAMES)} game).")
        return DETECTABLE_GAMES

def find_csc():
    """Cari C# compiler bawaan Windows untuk membuat dummy executable native ringan."""
    candidates = [
        r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
        r"C:\Windows\Microsoft.NET\Framework\v4.0.30319\csc.exe",
        r"C:\Windows\Microsoft.NET\Framework64\v3.5\csc.exe",
        r"C:\Windows\Microsoft.NET\Framework\v3.5\csc.exe"
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

def build_dummy_runner(target_path):
    """Kompilasi executable dummy kecil (~4KB) agar Discord mendeteksi proses Windows."""
    csc = find_csc()
    if csc:
        cs_code = """
using System;
using System.Windows.Forms;

class Program {
    [STAThread]
    static void Main(string[] args) {
        int duration = 1200;
        if (args.Length > 0) int.TryParse(args[0], out duration);
        string title = args.Length > 1 ? args[1] : "Detectable Game";
        Form form = new Form();
        form.Text = title;
        form.Width = 320;
        form.Height = 180;
        form.WindowState = FormWindowState.Minimized;
        form.ShowInTaskbar = true;
        Timer timer = new Timer();
        timer.Interval = Math.Max(1000, duration * 1000);
        timer.Tick += (s, e) => { Application.Exit(); };
        timer.Start();
        Application.Run(form);
    }
}
"""
        temp_cs = target_path + ".cs"
        try:
            with open(temp_cs, "w", encoding="utf-8") as f:
                f.write(cs_code)
            cmd = [csc, "/nologo", "/target:winexe", f"/out:{target_path}", temp_cs]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if res.returncode == 0 and os.path.exists(target_path):
                return True
        finally:
            if os.path.exists(temp_cs):
                os.remove(temp_cs)

    # Fallback jika csc tidak ditemukan
    notepad = r"C:\Windows\System32\notepad.exe"
    if os.path.exists(notepad):
        shutil.copy(notepad, target_path)
        return True
    return False

def send_discord_ipc(game_id, game_name, pid):
    """Kirim handshake & set activity ke socket IPC lokal Discord."""
    for i in range(10):
        pipe_path = f"\\\\.\\pipe\\discord-ipc-{i}"
        if not os.path.exists(pipe_path):
            continue
        try:
            f = open(pipe_path, "r+b", buffering=0)
            # Handshake
            handshake = json.dumps({"v": 1, "client_id": str(game_id)}).encode("utf-8")
            f.write(struct.pack("<II", 0, len(handshake)) + handshake)
            header = f.read(8)
            if len(header) < 8:
                f.close()
                continue
            _, length = struct.unpack("<II", header)
            f.read(length)

            # SET_ACTIVITY
            activity_payload = {
                "cmd": "SET_ACTIVITY",
                "args": {
                    "pid": pid,
                    "activity": {
                        "details": f"Playing {game_name}",
                        "state": "In Game",
                        "timestamps": {"start": int(time.time())}
                    }
                },
                "nonce": str(int(time.time()))
            }
            act_bytes = json.dumps(activity_payload).encode("utf-8")
            f.write(struct.pack("<II", 1, len(act_bytes)) + act_bytes)
            f.read(8)
            return f
        except Exception:
            continue
    return None

def format_time(seconds):
    """Format detik menjadi format menit dan detik (contoh: 19m 45s)."""
    m, s = divmod(seconds, 60)
    if m > 0:
        return f"{m}m {s:02d}s"
    return f"{s}s"

def play_game(game, duration_sec, index, total):
    """Menjalankan 1 game tiruan selama durasi tertentu."""
    print("\n" + "=" * 65)
    print(f"[{index}/{total}] Memulai Game: {game['name']}")
    print(f"       Executable : {game['exe']}")
    print(f"       App ID     : {game['id']}")
    print(f"       Durasi     : {format_time(duration_sec)} ({duration_sec} detik)")
    print("=" * 65)

    temp_dir = tempfile.mkdtemp(prefix="discord_game_")
    clean_exe_subpath = game["exe"].replace("/", "\\").lstrip("\\")
    full_exe_path = os.path.join(temp_dir, clean_exe_subpath)
    os.makedirs(os.path.dirname(full_exe_path), exist_ok=True)

    base_dummy = os.path.join(temp_dir, "_runner.exe")
    if not build_dummy_runner(base_dummy):
        print("[-] Gagal membuat runner executable.")
        shutil.rmtree(temp_dir, ignore_errors=True)
        return False

    shutil.copy(base_dummy, full_exe_path)

    # Jalankan dummy process
    proc = subprocess.Popen([full_exe_path, str(duration_sec), game["name"]])
    ipc_pipe = send_discord_ipc(game["id"], game["name"], proc.pid)

    if ipc_pipe:
        print("[+] Terhubung ke Discord IPC & Rich Presence aktif.")
    else:
        print("[*] Berjalan dengan Process Scanner lokal Discord.")

    # Countdown progress bar
    try:
        start_time = time.time()
        while True:
            elapsed = int(time.time() - start_time)
            remaining = duration_sec - elapsed
            if remaining <= 0:
                break
            percent = int((elapsed / duration_sec) * 30)
            bar = "=" * percent + ">" + " " * max(0, 29 - percent)
            pct_num = int((elapsed / duration_sec) * 100)
            sys.stdout.write(f"\r  [{bar}] {format_time(remaining)} tersisa ({pct_num}%)... ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write(f"\r  [{'=' * 30}] Selesai dimainkan ({format_time(duration_sec)})!          \n")
        sys.stdout.flush()
    except KeyboardInterrupt:
        print("\n\n[!] Sesi dihentikan pengguna.")
        proc.terminate()
        if ipc_pipe:
            ipc_pipe.close()
        shutil.rmtree(temp_dir, ignore_errors=True)
        sys.exit(0)
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=2)
        except Exception:
            pass
        if ipc_pipe:
            try:
                ipc_pipe.close()
            except Exception:
                pass
        shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"[✓] Game '{game['name']}' berhasil dimainkan selama {format_time(duration_sec)}!")
    return True

def main():
    print("""
=================================================================
   Discord Fake Game Player (Badge Game Variety / Polymath)
=================================================================
- Durasi Default : 20 Menit per game (menjamin Discord mencatat statistik)
- Mode Pemilihan : Acak (Random Shuffle) tanpa duplikat (pasti semua dapat)
- Database Game  : 100+ Game Terkurasi & 10.000+ Database Lengkap
""")

    history = load_history()
    if history:
        print(f"[i] Anda sudah memainkan {len(history)} game sebelumnya (tersimpan di riwayat).")

    print("\nPilih Sumber Game:")
    print(f"1. Koleksi Game Populer Terverifikasi ({len(DETECTABLE_GAMES)} game) [Rekomendasi]")
    print("2. Seluruh Database Resmi Discord (10.000+ game)")
    
    db_choice = input("Pilih sumber [1-2] (Default: 1): ").strip()
    if db_choice == "2":
        game_pool = load_all_detectable_games()
    else:
        game_pool = list(DETECTABLE_GAMES)

    print("\nMenu Aksi:")
    print("1. Otomatis Mainkan 6 Game Acak (Target Sisa Badge Polymath)")
    print("2. Mainkan SEMUA Game yang ada (Acak / Shuffle hingga tuntas)")
    print("3. Tentukan Jumlah Game Acak Sendiri (Custom N Game)")
    print("4. Reset Riwayat Game yang Sudah Dimainkan")
    print("5. Keluar")

    choice = input("\nPilih opsi [1-5] (Default: 1): ").strip()
    if not choice:
        choice = "1"

    if choice == "4":
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        print("[✓] Riwayat game yang sudah dimainkan telah direset.")
        return
    elif choice == "5":
        print("Keluar.")
        return

    # Durasi otomatis default 20 menit (1200 detik)
    duration = DEFAULT_DURATION
    dur_input = input(f"\nMasukkan durasi per game dalam menit [Default: 20 menit]: ").strip()
    if dur_input:
        try:
            val = float(dur_input)
            if val > 0:
                duration = int(val * 60)
        except ValueError:
            pass

    # Filter game yang belum dimainkan agar "pasti semua dapat" tanpa pengulangan
    unplayed = [g for g in game_pool if g["name"] not in history]
    if not unplayed:
        print("\n[!] Semua game dalam database sudah pernah dimainkan! Mereset daftar antrean untuk mulai lagi...")
        unplayed = list(game_pool)

    # Acak daftar (Shuffle)
    random.shuffle(unplayed)

    selected_games = []

    if choice == "1":
        # Ambil 6 game acak
        count = min(6, len(unplayed))
        selected_games = unplayed[:count]
    elif choice == "2":
        # Ambil semua game yang belum dimainkan (seluruhnya diacak)
        selected_games = unplayed
    elif choice == "3":
        total_avail = len(unplayed)
        amt_str = input(f"Berapa game yang ingin dimainkan? (Tersedia: {total_avail}, Default: 6): ").strip()
        amt = 6
        if amt_str.isdigit() and int(amt_str) > 0:
            amt = min(int(amt_str), total_avail)
        selected_games = unplayed[:amt]
    else:
        print("Pilihan tidak valid.")
        return

    total_time_sec = len(selected_games) * duration
    print("\n" + "-" * 65)
    print(f" Ringkasan Rencana Sesi:")
    print(f" • Total Game Akan Dimainkan : {len(selected_games)} game")
    print(f" • Durasi Tiap Game          : {format_time(duration)}")
    print(f" • Estimasi Waktu Total      : {format_time(total_time_sec)} (~{total_time_sec/3600:.2f} jam)")
    print(f" • Urutan                    : Acak / Random (Semua pasti dapat)")
    print("-" * 65)

    print("\nDaftar Game yang Terpilih untuk Sesi Ini:")
    for idx, g in enumerate(selected_games, 1):
        print(f"  {idx:2d}. {g['name']}")

    print("\nPastikan aplikasi Discord Desktop Anda sedang terbuka dan aktif!")
    input("\nTekan [ENTER] untuk memulai permainan...")

    for i, g in enumerate(selected_games, 1):
        success = play_game(g, duration, i, len(selected_games))
        if success:
            history.add(g["name"])
            save_history(history)
        if i < len(selected_games):
            print("\n[...] Jeda 5 detik sebelum meluncurkan game berikutnya...")
            time.sleep(5)

    print("\n" + "=" * 65)
    print(" SELURUH GAME DALAM SESI INI SELESAI DIMAINKAN!")
    print(f" Total riwayat game yang sudah terdaftar: {len(history)} game.")
    print(" Silakan cek profil Discord Anda untuk melihat badge Polymath.")
    print("=" * 65)

if __name__ == "__main__":
    main()
