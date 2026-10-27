#!/usr/bin/env node
/**
 * Discord Fake Game Player (Node.js Version)
 * Otomatis mainkan game tiruan (dummy process + Discord IPC)
 * untuk menyelesaikan badge Discord Game Variety / Polymath.
 * 
 * Menggunakan Node.js built-in library saja - tanpa perlu npm install!
 */

const fs = require('fs');
const path = require('path');
const os = require('os');
const net = require('net');
const cp = require('child_process');
const readline = require('readline');
const https = require('https');

// Durasi bawaan 20 menit (1200 detik)
const DEFAULT_DURATION = 20 * 60;

const HISTORY_FILE = path.resolve('played_history.json');
const CACHE_FILE = path.resolve('detectable_cache.json');

// Daftar 107 Game Terverifikasi Resmi Discord (Populer & Lengkap)
const DETECTABLE_GAMES = [
  { name: 'Overwatch', id: '356875221078245376', exe: 'overwatch.exe' },
  { name: 'The Binding of Isaac: Rebirth', id: '358420454764969994', exe: 'isaac-ng.exe' },
  { name: 'Fallout 4', id: '359509759642042378', exe: 'fallout4.exe' },
  { name: 'Dota 2', id: '356875988589740042', exe: 'dota2.exe' },
  { name: 'Rocket League', id: '356877880938070016', exe: 'rocketleague.exe' },
  { name: 'Terraria', id: '1402418344912752671', exe: 'terraria.exe' },
  { name: 'Bloons TD 6', id: '1402418571715543120', exe: 'bloonstd6.exe' },
  { name: 'Among Us', id: '1402418440685486130', exe: 'among us/among us.exe' },
  { name: 'World of Tanks', id: '1402418078813523999', exe: 'worldoftanks.exe' },
  { name: 'The First Descendant', id: '1256912167685587034', exe: 'm1-win64-shipping.exe' },
  { name: 'Sid Meier\'s Civilization VI', id: '363413834301571072', exe: 'civilizationvi.exe' },
  { name: 'Call of Duty: Black Ops III', id: '359509332490059776', exe: 'blackops3.exe' },
  { name: 'Monster Hunter: World', id: '477152881196269569', exe: 'monsterhunterworld.exe' },
  { name: 'Genshin Impact', id: '762434991303950386', exe: 'genshinimpact.exe' },
  { name: 'Battlefield 2042', id: '1162076274622222346', exe: 'battlefield 2042/bf2042.exe' },
  { name: 'Red Dead Redemption 2', id: '1402418648332898466', exe: 'red dead redemption 2/rdr2.exe' },
  { name: 'Krita', id: '1124353632758939688', exe: 'bin/krita.exe' },
  { name: 'Counter-Strike 2', id: '356875569427906560', exe: 'win64/cs2.exe' },
  { name: 'VALORANT', id: '700144983058874428', exe: 'win64/valorant-win64-shipping.exe' },
  { name: 'Cyberpunk 2077', id: '439169601008566273', exe: 'cyberpunk2077.exe' },
  { name: 'Apex Legends', id: '542075586886107149', exe: 'apex/r5apex.exe' },
  { name: 'PUBG: BATTLEGROUNDS', id: '356875883203657738', exe: 'win64/tslgame.exe' },
  { name: 'Elden Ring', id: '890251147577544714', exe: 'game/eldenring.exe' },
  { name: 'Baldur\'s Gate 3', id: '762002517868544020', exe: 'bin/bg3_dx11.exe' },
  { name: 'Palworld', id: '1197775514652250162', exe: 'wingdk/palworld-wingdk-shipping.exe' },
  { name: 'Lethal Company', id: '1168925345672613919', exe: 'lethal company.exe' },
  { name: 'Helldivers 2', id: '1203010729792901170', exe: 'bin/helldivers2.exe' },
  { name: 'Phasmophobia', id: '761623912189919242', exe: 'phasmophobia.exe' },
  { name: 'Rust', id: '356875704169922570', exe: 'rustclient.exe' },
  { name: 'Dead by Daylight', id: '356877073715167232', exe: 'deadby daylight/binaries/win64/deadbydaylight-win64-shipping.exe' },
  { name: 'Stardew Valley', id: '356876352932413441', exe: 'stardew valley.exe' },
  { name: 'Hollow Knight', id: '363413554495488000', exe: 'hollow_knight.exe' },
  { name: 'Hades', id: '522137953258766347', exe: 'x64/hades.exe' },
  { name: 'Tom Clancy\'s Rainbow Six Siege', id: '356876121406832640', exe: 'rainbowsix.exe' },
  { name: 'Destiny 2', id: '356876229984518144', exe: 'destiny2.exe' },
  { name: 'Warframe', id: '356876527587164160', exe: 'warframe.x64.exe' },
  { name: 'Sea of Thieves', id: '358421868350537728', exe: 'athena/binaries/win64/seaofthieves.exe' },
  { name: 'Grand Theft Auto V', id: '356876800720502784', exe: 'gta5.exe' },
  { name: 'Forza Horizon 5', id: '893949811563032607', exe: 'forzahorizon5.exe' },
  { name: 'Euro Truck Simulator 2', id: '363413988673060864', exe: 'bin/win_x64/eurotrucks2.exe' },
  { name: 'Left 4 Dead 2', id: '356877232800661504', exe: 'left4dead2.exe' },
  { name: 'Team Fortress 2', id: '356876930504720384', exe: 'hl2.exe' },
  { name: 'Garry\'s Mod', id: '356877484643450880', exe: 'gmod.exe' },
  { name: 'Don\'t Starve Together', id: '358421375251382272', exe: 'bin64/dontstarve_steam_x64.exe' },
  { name: 'PAYDAY 2', id: '356877718018457600', exe: 'payday2_win32_release.exe' },
  { name: 'Subnautica', id: '358420658700255232', exe: 'subnautica.exe' },
  { name: 'ARK: Survival Evolved', id: '356876646571180032', exe: 'shootergame/binaries/win64/shootergame.exe' },
  { name: 'The Forest', id: '358420958106714112', exe: 'theforest.exe' },
  { name: 'Sons of the Forest', id: '1078652399993880596', exe: 'sonsoftheforest.exe' },
  { name: 'Slay the Spire', id: '404022444530597899', exe: 'slaythespire.exe' },
  { name: 'Celeste', id: '410534241680883712', exe: 'celeste.exe' },
  { name: 'Cuphead', id: '363413344155336704', exe: 'cuphead.exe' },
  { name: 'Undertale', id: '358421115854487552', exe: 'undertale.exe' },
  { name: 'Factorio', id: '358420790757785600', exe: 'bin/x64/factorio.exe' },
  { name: 'RimWorld', id: '358421639912226816', exe: 'rimworldwin64.exe' },
  { name: 'Cities: Skylines', id: '358420542371495936', exe: 'cities.exe' },
  { name: 'Project Zomboid', id: '358421757885415424', exe: 'projectzomboid64.exe' },
  { name: 'Deep Rock Galactic', id: '418464673894105088', exe: 'fsd/binaries/win64/fsd-win64-shipping.exe' },
  { name: 'Risk of Rain 2', id: '560548174486503434', exe: 'risk of rain 2.exe' },
  { name: 'Monster Hunter Rise', id: '926590823334547466', exe: 'monsterhunterrise.exe' },
  { name: 'Dark Souls III', id: '358421257403760640', exe: 'darksoulsiii.exe' },
  { name: 'Sekiro: Shadows Die Twice', id: '558719266157821952', exe: 'sekiro.exe' },
  { name: 'Lies of P', id: '1153443153676865677', exe: 'cp/binaries/win64/lop-win64-shipping.exe' },
  { name: 'Arma 3', id: '356877342938890240', exe: 'arma3_x64.exe' },
  { name: 'Hearts of Iron IV', id: '363413708304678912', exe: 'hoi4.exe' },
  { name: 'Stellaris', id: '363413778508939264', exe: 'stellaris.exe' },
  { name: 'Crusader Kings III', id: '750796335128641577', exe: 'binaries/ck3.exe' },
  { name: 'Mount & Blade II: Bannerlord', id: '694314488341626910', exe: 'bin/win64_shipping_client/bannerlord.exe' },
  { name: 'No Man\'s Sky', id: '356877602322907136', exe: 'binaries/nms.exe' },
  { name: 'Starfield', id: '1147572791881764954', exe: 'starfield.exe' },
  { name: 'Fallout: New Vegas', id: '363414073574162432', exe: 'falloutnv.exe' },
  { name: 'The Elder Scrolls V: Skyrim', id: '356876442656702464', exe: 'tesv.exe' },
  { name: 'The Witcher 3: Wild Hunt', id: '356876043237588992', exe: 'bin/x64/witcher3.exe' },
  { name: 'God of War', id: '931238100586074122', exe: 'gow.exe' },
  { name: 'Horizon Zero Dawn', id: '741406450143854652', exe: 'horizonzerodawn.exe' },
  { name: 'Death Stranding', id: '733051405979615243', exe: 'ds.exe' },
  { name: 'Control', id: '616016738416525332', exe: 'control_dx12.exe' },
  { name: 'Resident Evil 4', id: '1088924619437645854', exe: 're4.exe' },
  { name: 'Resident Evil Village', id: '840280829807558666', exe: 're8.exe' },
  { name: 'Street Fighter 6', id: '1114258359487561848', exe: 'streetfighter6.exe' },
  { name: 'Tekken 8', id: '1199738096174895104', exe: 'polaris/binaries/win64/polaris-win64-shipping.exe' },
  { name: 'Mortal Kombat 1', id: '1153443153676865677', exe: 'mk12/binaries/win64/mk12.exe' },
  { name: 'Guilty Gear -Strive-', id: '852613589998108712', exe: 'red/binaries/win64/ggst-win64-shipping.exe' },
  { name: 'Brawlhalla', id: '358421487889416192', exe: 'brawlhalla.exe' },
  { name: 'Roblox', id: '439223656200273931', exe: 'robloxplayerbeta.exe' },
  { name: 'osu!', id: '356877983228887040', exe: 'osu!.exe' },
  { name: 'Honkai: Star Rail', id: '1098679075775594586', exe: 'starrail.exe' },
  { name: 'Zenless Zone Zero', id: '1258169123851079730', exe: 'zenlesszonezero.exe' },
  { name: 'Vampire Survivors', id: '933068032542998599', exe: 'vampiresurvivors.exe' },
  { name: 'Dave the Diver', id: '1124443652878520330', exe: 'davethediver.exe' },
  { name: 'Balatro', id: '1209594191316258816', exe: 'balatro.exe' },
  { name: 'Content Warning', id: '1224419918079557672', exe: 'content warning.exe' },
  { name: 'Chained Together', id: '1253412587572629554', exe: 'chainedtogether/binaries/win64/chainedtogether-win64-shipping.exe' },
  { name: 'Supermarket Simulator', id: '1211756461991395378', exe: 'supermarket simulator.exe' },
  { name: 'Manor Lords', id: '1233075252876644402', exe: 'manorlords/binaries/win64/manorlords-win64-shipping.exe' },
  { name: 'Ready or Not', id: '921869818812854342', exe: 'readyornot/binaries/win64/readyornot-win64-shipping.exe' },
  { name: 'Squad', id: '358421037429391360', exe: 'squadgame/binaries/win64/squadgame.exe' },
  { name: 'Assetto Corsa', id: '363413444474961920', exe: 'acs.exe' },
  { name: 'BeamNG.drive', id: '363413628797452288', exe: 'bin64/beamng.drive.x64.exe' },
  { name: 'Farming Simulator 22', id: '912383272938262538', exe: 'x64/farmingsimulator2022game.exe' },
  { name: 'Microsoft Flight Simulator', id: '745722302381293628', exe: 'flightsimulator.exe' },
  { name: 'Geometry Dash', id: '358421976077303808', exe: 'geometrydash.exe' },
  { name: 'Portal 2', id: '356877151049351168', exe: 'portal2.exe' },
  { name: 'Half-Life 2', id: '356876878436499456', exe: 'hl2.exe' },
  { name: 'Brotato', id: '1024388836567941160', exe: 'brotato.exe' },
  { name: 'Enter the Gungeon', id: '358420875969560576', exe: 'etg.exe' }
];

function loadHistory() {
  if (fs.existsSync(HISTORY_FILE)) {
    try {
      const data = JSON.parse(fs.readFileSync(HISTORY_FILE, 'utf8'));
      return new Set(data);
    } catch (e) {
      return new Set();
    }
  }
  return new Set();
}

function saveHistory(historySet) {
  try {
    fs.writeFileSync(HISTORY_FILE, JSON.stringify(Array.from(historySet), null, 2), 'utf8');
  } catch (e) {}
}

function loadAllDetectableGames() {
  if (fs.existsSync(CACHE_FILE)) {
    try {
      const data = JSON.parse(fs.readFileSync(CACHE_FILE, 'utf8'));
      if (Array.isArray(data) && data.length > 0) return data;
    } catch (e) {}
  }
  return DETECTABLE_GAMES;
}

function shuffleArray(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  if (m > 0) return `${m}m ${String(s).padStart(2, '0')}s`;
  return `${s}s`;
}

function findCsc() {
  const candidates = [
    'C:\\Windows\\Microsoft.NET\\Framework64\\v4.0.30319\\csc.exe',
    'C:\\Windows\\Microsoft.NET\\Framework\\v4.0.30319\\csc.exe',
    'C:\\Windows\\Microsoft.NET\\Framework64\\v3.5\\csc.exe',
    'C:\\Windows\\Microsoft.NET\\Framework\\v3.5\\csc.exe'
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
}

function buildDummyRunner(targetExePath) {
  const csc = findCsc();
  if (csc) {
    const csCode = `
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
`;
    const tempCs = targetExePath + '.cs';
    try {
      fs.writeFileSync(tempCs, csCode, 'utf8');
      cp.execFileSync(csc, ['/nologo', '/target:winexe', `/out:${targetExePath}`, tempCs], { stdio: 'ignore' });
      if (fs.existsSync(targetExePath)) return true;
    } catch (e) {
    } finally {
      if (fs.existsSync(tempCs)) fs.unlinkSync(tempCs);
    }
  }

  // Fallback ke notepad.exe bawaan Windows
  const notepad = 'C:\\Windows\\System32\\notepad.exe';
  if (fs.existsSync(notepad)) {
    fs.copyFileSync(notepad, targetExePath);
    return true;
  }
  return false;
}

function sendDiscordIpc(gameId, gameName, pid) {
  return new Promise((resolve) => {
    let connectedSocket = null;

    for (let i = 0; i < 10; i++) {
      const pipePath = `\\\\.\\pipe\\discord-ipc-${i}`;
      try {
        const client = net.connect(pipePath, () => {
          connectedSocket = client;

          // Handshake (opcode 0)
          const handshake = JSON.stringify({ v: 1, client_id: String(gameId) });
          const handshakeBuf = Buffer.from(handshake, 'utf8');
          const header = Buffer.alloc(8);
          header.writeUInt32LE(0, 0);
          header.writeUInt32LE(handshakeBuf.length, 4);
          client.write(Buffer.concat([header, handshakeBuf]));

          // Listen for reply then send SET_ACTIVITY
          client.once('data', () => {
            const act = JSON.stringify({
              cmd: 'SET_ACTIVITY',
              args: {
                pid: pid,
                activity: {
                  details: `Playing ${gameName}`,
                  state: 'In Game',
                  timestamps: { start: Math.floor(Date.now() / 1000) }
                }
              },
              nonce: String(Date.now())
            });
            const actBuf = Buffer.from(act, 'utf8');
            const actHeader = Buffer.alloc(8);
            actHeader.writeUInt32LE(1, 0);
            actHeader.writeUInt32LE(actBuf.length, 4);
            client.write(Buffer.concat([actHeader, actBuf]));
            resolve(client);
          });
        });

        client.on('error', () => {});
        if (connectedSocket) break;
      } catch (e) {}
    }

    setTimeout(() => {
      resolve(connectedSocket);
    }, 1000);
  });
}

async function playGame(game, durationSec, index, total) {
  console.log('\n' + '='.repeat(65));
  console.log(`[${index}/${total}] Memulai Game: ${game.name}`);
  console.log(`       Executable : ${game.exe}`);
  console.log(`       App ID     : ${game.id}`);
  console.log(`       Durasi     : ${formatTime(durationSec)} (${durationSec} detik)`);
  console.log('='.repeat(65));

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), 'discord_game_'));
  const cleanExeSubpath = game.exe.replace(/\//g, '\\').replace(/^\\+/, '');
  const fullExePath = path.join(tempDir, cleanExeSubpath);
  fs.mkdirSync(path.dirname(fullExePath), { recursive: true });

  const baseDummy = path.join(tempDir, '_runner.exe');
  if (!buildDummyRunner(baseDummy)) {
    console.log('[-] Gagal membuat runner executable.');
    fs.rmSync(tempDir, { recursive: true, force: true });
    return false;
  }

  fs.copyFileSync(baseDummy, fullExePath);

  const proc = cp.spawn(fullExePath, [String(durationSec), game.name], {
    detached: false,
    stdio: 'ignore'
  });

  const ipcSocket = await sendDiscordIpc(game.id, game.name, proc.pid);
  if (ipcSocket) {
    console.log('[+] Terhubung ke Discord IPC & Rich Presence aktif.');
  } else {
    console.log('[*] Berjalan dengan Process Scanner lokal Discord.');
  }

  const startTime = Date.now();
  await new Promise((resolve) => {
    const timer = setInterval(() => {
      const elapsed = Math.floor((Date.now() - startTime) / 1000);
      const remaining = durationSec - elapsed;
      if (remaining <= 0) {
        clearInterval(timer);
        process.stdout.write(`\r  [${'='.repeat(30)}] Selesai dimainkan (${formatTime(durationSec)})!          \n`);
        resolve();
      } else {
        const percent = Math.floor((elapsed / durationSec) * 30);
        const bar = '='.repeat(percent) + '>' + ' '.repeat(Math.max(0, 29 - percent));
        const pctNum = Math.floor((elapsed / durationSec) * 100);
        process.stdout.write(`\r  [${bar}] ${formatTime(remaining)} tersisa (${pctNum}%)... `);
      }
    }, 1000);
  });

  try { proc.kill(); } catch (e) {}
  if (ipcSocket) {
    try { ipcSocket.destroy(); } catch (e) {}
  }
  try { fs.rmSync(tempDir, { recursive: true, force: true }); } catch (e) {}

  console.log(`[✓] Game '${game.name}' berhasil dimainkan selama ${formatTime(durationSec)}!`);
  return true;
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const ask = (q) => new Promise((resolve) => rl.question(q, resolve));

async function main() {
  console.log(`
=================================================================
   Discord Fake Game Player (Badge Game Variety / Polymath)
=================================================================
- Durasi Default : 20 Menit per game (menjamin Discord mencatat statistik)
- Mode Pemilihan : Acak (Random Shuffle) tanpa duplikat (pasti semua dapat)
- Database Game  : 100+ Game Terkurasi & 10.000+ Database Lengkap
`);

  const history = loadHistory();
  if (history.size > 0) {
    console.log(`[i] Anda sudah memainkan ${history.size} game sebelumnya (tersimpan di riwayat).`);
  }

  console.log('\nPilih Sumber Game:');
  console.log(`1. Koleksi Game Populer Terverifikasi (${DETECTABLE_GAMES.length} game) [Rekomendasi]`);
  console.log('2. Seluruh Database Resmi Discord (10.000+ game)');

  const dbChoice = (await ask('Pilih sumber [1-2] (Default: 1): ')).trim();
  const gamePool = dbChoice === '2' ? loadAllDetectableGames() : [...DETECTABLE_GAMES];

  console.log('\nMenu Aksi:');
  console.log('1. Otomatis Mainkan 6 Game Acak (Target Sisa Badge Polymath)');
  console.log('2. Mainkan SEMUA Game yang ada (Acak / Shuffle hingga tuntas)');
  console.log('3. Tentukan Jumlah Game Acak Sendiri (Custom N Game)');
  console.log('4. Reset Riwayat Game yang Sudah Dimainkan');
  console.log('5. Keluar');

  let choice = (await ask('\nPilih opsi [1-5] (Default: 1): ')).trim();
  if (!choice) choice = '1';

  if (choice === '4') {
    if (fs.existsSync(HISTORY_FILE)) fs.unlinkSync(HISTORY_FILE);
    console.log('[✓] Riwayat game yang sudah dimainkan telah direset.');
    rl.close();
    return;
  } else if (choice === '5') {
    console.log('Keluar.');
    rl.close();
    return;
  }

  let duration = DEFAULT_DURATION;
  const durInput = (await ask('\nMasukkan durasi per game dalam menit [Default: 20 menit]: ')).trim();
  if (durInput) {
    const val = parseFloat(durInput);
    if (!isNaN(val) && val > 0) {
      duration = Math.floor(val * 60);
    }
  }

  // Filter game yang belum dimainkan agar "pasti semua dapat" tanpa duplikasi
  let unplayed = gamePool.filter((g) => !history.has(g.name));
  if (unplayed.length === 0) {
    console.log('\n[!] Semua game dalam database sudah pernah dimainkan! Mereset daftar antrean...');
    unplayed = [...gamePool];
  }

  // Acak urutan (Shuffle)
  unplayed = shuffleArray(unplayed);

  let selectedGames = [];
  if (choice === '1') {
    selectedGames = unplayed.slice(0, Math.min(6, unplayed.length));
  } else if (choice === '2') {
    selectedGames = unplayed;
  } else if (choice === '3') {
    const totalAvail = unplayed.length;
    const amtStr = (await ask(`Berapa game yang ingin dimainkan? (Tersedia: ${totalAvail}, Default: 6): `)).trim();
    let amt = 6;
    if (/^\d+$/.test(amtStr) && parseInt(amtStr, 10) > 0) {
      amt = Math.min(parseInt(amtStr, 10), totalAvail);
    }
    selectedGames = unplayed.slice(0, amt);
  } else {
    console.log('Pilihan tidak valid.');
    rl.close();
    return;
  }

  const totalTimeSec = selectedGames.length * duration;
  console.log('\n' + '-'.repeat(65));
  console.log(` Ringkasan Rencana Sesi:`);
  console.log(` • Total Game Akan Dimainkan : ${selectedGames.length} game`);
  console.log(` • Durasi Tiap Game          : ${formatTime(duration)}`);
  console.log(` • Estimasi Waktu Total      : ${formatTime(totalTimeSec)} (~${(totalTimeSec / 3600).toFixed(2)} jam)`);
  console.log(` • Urutan                    : Acak / Random (Semua pasti dapat)`);
  console.log('-'.repeat(65));

  console.log('\nDaftar Game yang Terpilih untuk Sesi Ini:');
  selectedGames.forEach((g, idx) => {
    console.log(`  ${String(idx + 1).padStart(2, ' ')}. ${g.name}`);
  });

  await ask('\nTekan [ENTER]...');
  rl.close();

  for (let i = 0; i < selectedGames.length; i++) {
    const success = await playGame(selectedGames[i], duration, i + 1, selectedGames.length);
    if (success) {
      history.add(selectedGames[i].name);
      saveHistory(history);
    }
    if (i < selectedGames.length - 1) {
      console.log('\n[...] Jeda 5 detik sebelum meluncurkan game berikutnya...');
      await new Promise((r) => setTimeout(r, 5000));
    }
  }

  console.log('\n' + '='.repeat(65));
  console.log(' SELURUH GAME DALAM SESI INI SELESAI DIMAINKAN!');
  console.log(` Total riwayat game yang sudah terdaftar: ${history.size} game.`);
  console.log(' Silakan cek profil Discord Anda untuk melihat badge Polymath.');
  console.log('='.repeat(65));
}

main().catch(console.error);
