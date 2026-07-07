"""
Fetch subscriber count + active user count for a list of subreddits,
using a real headless browser (Playwright) instead of raw HTTP requests.

Why this version: Reddit's bot detection is JS/TLS-based, not just a
User-Agent check. A plain `requests` call fails (403) even with the right
headers, because it doesn't run JavaScript or match a real browser's TLS
fingerprint. Opening the same link in your actual browser works because
the browser passes that check. This script uses Chromium under the hood,
so the request looks the same to Reddit as it does when you click the link.

Setup:
    pip install playwright
    playwright install chromium

Run:
    python get_subreddit_stats_browser.py

Output:
    subreddit_stats.csv
"""

import asyncio
import csv
import random
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from playwright.async_api import async_playwright

SUBREDDITS = list(dict.fromkeys([
    "AdaIndonesiaCoy", "Airdropsultan_IND", "aku_ddn", "AlamatkanSaya", "anjing",
    "awkarir", "AyundaRisu", "bacabuku", "BadutBucin", "bali", "Balikpapan",
    "BaliTravelTips", "BandarLampung", "Bandung", "Banjarmasin", "Batak", "batik",
    "Benang", "Bengkulu", "bestofID", "bisaland", "bokepindoplus",
    "BuddhismIndonesia", "bukanposronda", "cdid", "cekrek", "ceritaindah",
    "cerpen", "CoffeeID", "CollapseIndonesia", "CurhatDonk", "cursedindomie",
    "daster", "dblcinema", "diaspora_id", "dioramaid", "DIYogyakarta",
    "duniaberita", "EnemiMetal", "EnoBening", "finansial", "fucklippo",
    "fucktribune", "gadjahmada", "GameDevsIndonesia", "Gamelan",
    "GamerMobileIndonesia", "GAMERS_ID", "gelapindonesia", "giliislands",
    "golang_id", "GrabTranslation", "GudangGue", "hotindos", "idiotdijalanan",
    "indo", "indoaachener", "indobiz", "indocartalk", "IndoExMuslim",
    "indofemboy", "IndoFilms", "IndoFinance", "IndoFlicks", "indogamer",
    "IndoGamerPals", "indogirls", "indogonewild", "indohallyu", "indoindie",
    "IndoJAVHentaiNSFW", "indoleaked", "IndoLGBT", "indolostmedia",
    "Indomototalk", "indomusic", "indonesia_gadis_AI", "indonesiabebas",
    "indonesiacerah", "indonesiaemas", "IndonesiaExpats", "IndonesiaFunny",
    "indonesiagelap", "indonesiakaya", "IndonesiaLiveScene", "IndonesiaMaju",
    "Indonesiamiskin", "indonesian", "IndonesianCoffee", "IndonesianExMuslim",
    "indonesianfood", "IndonesianGIRLS", "IndonesianGirlsFap",
    "indonesiangirlsonly", "Indonesianlord", "IndonesianNSFW", "Indonesianporn",
    "indonesiansfw", "Indonesianshemales", "indonesiansingermany",
    "indonesiapaspasan", "IndonesiaPics", "Indonesias", "IndonesiaSwinger",
    "indonesigirlonly", "IndoNightLife", "indoparenting", "Indopeopletwitter",
    "IndoRiders", "indotech", "indotiktokhotties", "indowibu", "itb",
    "ITBandung", "Jabodetabek", "Jakarta", "JakartaDefaultism", "jalanjalan",
    "Javanese", "jerman", "jilboob", "jogja", "jualbeliindonesia", "JudiSaham",
    "karir", "kendaraan", "komododragons", "Kontol_Indo", "kucing",
    "kulineria", "Lahelu", "libertarianindonesia", "lndonesia", "Lombok",
    "MahastudentPlayground", "Makassar", "malang", "Manado",
    "MapsWithHalfIndonesia", "MapsWithoutIndonesia", "mataram", "MBGIndonesia",
    "Medan", "MedanID", "migoreng", "MuseumInternetIndo", "musikindonesia",
    "MWIDI", "Nanggroe", "naughtynusantara", "negriwakanda", "Ngentot_Indo",
    "ngeteh", "NoPrabowo", "NusaLembongan", "Nusantara", "NusantaraRaya",
    "nyanfm", "OkeKawanGoblok", "okkawanbodoh", "OlympTradeIndonesia",
    "ondonesia", "OOOBTC_Indonesia", "OrangIndo", "orangutan", "padang",
    "palembang", "panendividen", "pantattruk", "Pasundan", "PBI_Official",
    "pedulijiwaID", "pencaksilat", "Pengangguran", "perempuan",
    "PersibBandung", "pisang", "place_indomie", "PolitikIndo", "prabowo",
    "pria", "PsikologiIndonesia", "r4rindonesia", "RajaAmpat", "rakitpc",
    "rezaauditore", "RisetIndonesia", "S3Marketing", "sahamAS", "salintempel",
    "Samarinda", "SastraIndonesia", "Sderhana", "sehat", "sejarah",
    "sellerdongo", "SepakBolaIndonesia", "simulatorkeluarga", "SiskaeeeXXX",
    "smean", "sobatgalbay", "sudirmanbets", "sudutpandangyaya", "Sulawesi",
    "sulawesishrimp", "sumatra", "sumatratravel", "Sunda", "surabaya",
    "Tempeh", "the_bowo", "TheChurchOfIndomie", "tiktok_indonesia",
    "tiktokhotindo", "timpateks", "TodayILearnedID", "togeproductions",
    "TwitchIndonesia", "universitasindonesia", "UnivTerbuka", "UiDMod",
    "viruscovid19", "westpapua", "whooshHSR", "WkwkwkLand",
    "writestreakindonesian", "2indonesia4u", "3DPrintID",
]))


CSV_PATH = "subreddit_stats.csv"
FIELDNAMES = ["subreddit", "subscribers", "active_users", "created_utc", "description", "status"]


def load_existing():
    """Load already-fetched results so a re-run can skip them."""
    done = {}
    try:
        with open(CSV_PATH, "r", newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                # only count it as done if it succeeded or was a real (non-429) failure
                if row["status"] == "ok" or (
                    row["status"].startswith("http_") and row["status"] != "http_429_gave_up"
                ):
                    done[row["subreddit"]] = row
    except FileNotFoundError:
        pass
    return done


def save_all(results):
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(results)


async def main():
    already_done = load_existing()
    results = list(already_done.values())
    remaining = [s for s in SUBREDDITS if s not in already_done]
    total = len(SUBREDDITS)

    if already_done:
        print(f"Resuming: {len(already_done)}/{total} already fetched, "
              f"{len(remaining)} left to go.\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        # Warm up: visit the homepage first so any bot-check cookie gets set,
        # same as what happens the first time you open reddit.com in a tab.
        await page.goto("https://www.reddit.com/", wait_until="domcontentloaded")
        await page.wait_for_timeout(2000)

        base_delay = 3.0  # seconds between requests, grows if we get rate limited

        for i, sub in enumerate(remaining, 1):
            url = f"https://www.reddit.com/r/{sub}/about.json"
            max_retries = 5
            attempt = 0
            row = None

            while attempt <= max_retries:
                try:
                    result = await page.evaluate(
                        """
                        async (url) => {
                            const res = await fetch(url, { headers: { "Accept": "application/json" } });
                            if (!res.ok) return { ok: false, status: res.status };
                            const j = await res.json();
                            return { ok: true, data: j.data };
                        }
                        """,
                        url,
                    )
                    if result.get("ok"):
                        d = result["data"]
                        created_utc = d.get("created_utc")
                        if created_utc:
                            created_utc = datetime.fromtimestamp(created_utc, tz=ZoneInfo("Asia/Jakarta")).isoformat()
                        row = {
                            "subreddit": sub,
                            "subscribers": d.get("subscribers"),
                            "active_users": d.get("active_user_count"),
                            "created_utc": created_utc,
                            "description": d.get("public_description"),
                            "status": "ok",
                        }
                        break
                    elif result.get("status") == 429:
                        # Rate limited: back off harder and permanently slow down
                        wait = min(60, (2 ** attempt) * 5)
                        base_delay = min(10.0, base_delay + 1.0)
                        print(f"  -> 429 on r/{sub}, backing off {wait}s "
                              f"(attempt {attempt + 1}/{max_retries}, new base delay {base_delay}s)")
                        await page.wait_for_timeout(wait * 1000)
                        attempt += 1
                        continue
                    else:
                        row = {
                            "subreddit": sub,
                            "subscribers": None,
                            "active_users": None,
                            "created_utc": None,
                            "description": None,
                            "status": f"http_{result.get('status')}",
                        }
                        break
                except Exception as e:
                    row = {
                        "subreddit": sub,
                        "subscribers": None,
                        "active_users": None,
                        "created_utc": None,
                        "description": None,
                        "status": f"error_{type(e).__name__}",
                    }
                    break

            if row is None:
                # exhausted retries, still 429
                row = {
                    "subreddit": sub,
                    "subscribers": None,
                    "active_users": None,
                    "created_utc": None,
                    "description": None,
                    "status": "http_429_gave_up",
                }

            results.append(row)
            print(f"[{i}/{len(remaining)}] r/{sub} -> {row['status']} "
                  f"(subs={row['subscribers']}, active={row['active_users']}, "
                  f"created={row['created_utc']}, desc={row['description'][:50] if row['description'] else None})")
            save_all(results)  # write progress after every row, not just at the end

            await page.wait_for_timeout(int(random.uniform(base_delay, base_delay + 1.5) * 1000))

        await browser.close()

    print(f"\nDone. {len(results)}/{total} subreddits saved to {CSV_PATH}")


if __name__ == "__main__":
    asyncio.run(main())