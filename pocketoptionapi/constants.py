"""
Autor: AdminhuDev
"""

from typing import Dict, List
import random

ACTIVES = {
    # COMMODITY - 16 ativos
    "UKBrent": 50,  # Brent Oil - 50.0%
    "UKBrent_otc": 164,  # Brent Oil OTC - 80.0%
    "USCrude": 64,  # WTI Crude Oil - 50.0%
    "USCrude_otc": 165,  # WTI Crude Oil OTC - 80.0%
    "XAGEUR": 103,  # XAG/EUR - 50.0%
    "XAGUSD": 65,  # Silver - 50.0%
    "XAGUSD_otc": 167,  # Silver OTC - 80.0%
    "XAUEUR": 102,  # XAU/EUR - 50.0%
    "XAUUSD": 2,  # Gold - 50.0%
    "XAUUSD_otc": 169,  # Gold OTC - 80.0%
    "XNGUSD": 311,  # Natural Gas - 45.0%
    "XNGUSD_otc": 399,  # Natural Gas OTC - 45.0%
    "XPDUSD": 313,  # Palladium spot - 45.0%
    "XPDUSD_otc": 401,  # Palladium spot OTC - 45.0%
    "XPTUSD": 312,  # Platinum spot - 45.0%
    "XPTUSD_otc": 400,  # Platinum spot OTC - 45.0%

    # CRYPTOCURRENCY - 23 ativos
    "ADA-USD_otc": 473,  # Cardano OTC - 92.0%
    "AVAX_otc": 481,  # Avalanche OTC - 59.0%
    "BCHEUR": 450,  # BCH/EUR - 15.0%
    "BCHGBP": 451,  # BCH/GBP - 15.0%
    "BCHJPY": 452,  # BCH/JPY - 15.0%
    "BITB_otc": 494,  # Bitcoin ETF OTC - 91.0%
    "BNB-USD_otc": 470,  # BNB OTC - 92.0%
    "BTCGBP": 453,  # BTC/GBP - 15.0%
    "BTCJPY": 454,  # BTC/JPY - 15.0%
    "BTCUSD": 197,  # Bitcoin - 15.0%
    "BTCUSD_otc": 484,  # Bitcoin OTC - 76.0%
    "DASH_USD": 209,  # Dash - 25.0%
    "DOGE_otc": 485,  # Dogecoin OTC - 82.0%
    "DOTUSD_otc": 486,  # Polkadot OTC - 28.0%
    "ETHUSD": 272,  # Ethereum - 40.0%
    "ETHUSD_otc": 487,  # Ethereum OTC - 92.0%
    "LINK_otc": 478,  # Chainlink OTC - 92.0%
    "LNKUSD": 464,  # Chainlink - 15.0%
    "LTCUSD_otc": 488,  # Litecoin OTC - 51.0%
    "MATIC_otc": 491,  # Polygon OTC - 92.0%
    "SOL-USD_otc": 472,  # Solana OTC - 51.0%
    "TON-USD_otc": 480,  # Toncoin OTC - 92.0%
    "TRX-USD_otc": 476,  # TRON OTC - 40.0%

    # CURRENCY - 80 ativos
    "AEDCNY_otc": 538,  # AED/CNY OTC - 67.0%
    "AUDCAD": 36,  # AUD/CAD - 50.0%
    "AUDCAD_otc": 67,  # AUD/CAD OTC - 92.0%
    "AUDCHF": 37,  # AUD/CHF - 50.0%
    "AUDCHF_otc": 68,  # AUD/CHF OTC - 92.0%
    "AUDJPY": 38,  # AUD/JPY - 50.0%
    "AUDJPY_otc": 69,  # AUD/JPY OTC - 57.0%
    "AUDNZD_otc": 70,  # AUD/NZD OTC - 48.0%
    "AUDUSD": 40,  # AUD/USD - 47.0%
    "AUDUSD_otc": 71,  # AUD/USD OTC - 92.0%
    "BHDCNY_otc": 536,  # BHD/CNY OTC - 52.0%
    "CADCHF": 41,  # CAD/CHF - 50.0%
    "CADCHF_otc": 72,  # CAD/CHF OTC - 92.0%
    "CADJPY": 42,  # CAD/JPY - 50.0%
    "CADJPY_otc": 73,  # CAD/JPY OTC - 76.0%
    "CHFJPY": 43,  # CHF/JPY - 50.0%
    "CHFJPY_otc": 74,  # CHF/JPY OTC - 60.0%
    "CHFNOK_otc": 457,  # CHF/NOK OTC - 62.0%
    "EURAUD": 44,  # EUR/AUD - 50.0%
    "EURCAD": 45,  # EUR/CAD - 30.0%
    "EURCHF": 46,  # EUR/CHF - 40.0%
    "EURCHF_otc": 77,  # EUR/CHF OTC - 92.0%
    "EURGBP": 47,  # EUR/GBP - 50.0%
    "EURGBP_otc": 78,  # EUR/GBP OTC - 88.0%
    "EURHUF_otc": 460,  # EUR/HUF OTC - 71.0%
    "EURJPY": 48,  # EUR/JPY - 58.0%
    "EURJPY_otc": 79,  # EUR/JPY OTC - 92.0%
    "EURNZD_otc": 80,  # EUR/NZD OTC - 92.0%
    "EURRUB_otc": 200,  # EUR/RUB OTC - 71.0%
    "EURTRY_otc": 468,  # EUR/TRY OTC - 85.0%
    "EURUSD": 1,  # EUR/USD - 50.0%
    "EURUSD_otc": 66,  # EUR/USD OTC - 90.0%
    "GBPAUD": 51,  # GBP/AUD - 50.0%
    "GBPAUD_otc": 81,  # GBP/AUD OTC - 92.0%
    "GBPCAD": 52,  # GBP/CAD - 45.0%
    "GBPCHF": 53,  # GBP/CHF - 50.0%
    "GBPJPY": 54,  # GBP/JPY - 58.0%
    "GBPJPY_otc": 84,  # GBP/JPY OTC - 89.0%
    "GBPUSD": 56,  # GBP/USD - 49.0%
    "GBPUSD_otc": 86,  # GBP/USD OTC - 92.0%
    "IRRUSD_otc": 548,  # IRR/USD OTC - 86.0%
    "JODCNY_otc": 546,  # JOD/CNY OTC - 45.0%
    "KESUSD_otc": 554,  # KES/USD OTC - 54.0%
    "LBPUSD_otc": 530,  # LBP/USD OTC - 92.0%
    "MADUSD_otc": 534,  # MAD/USD OTC - 81.0%
    "NGNUSD_otc": 552,  # NGN/USD OTC - 66.0%
    "NZDJPY_otc": 89,  # NZD/JPY OTC - 73.0%
    "NZDUSD_otc": 90,  # NZD/USD OTC - 59.0%
    "OMRCNY_otc": 544,  # OMR/CNY OTC - 84.0%
    "QARCNY_otc": 542,  # QAR/CNY OTC - 89.0%
    "SARCNY_otc": 540,  # SAR/CNY OTC - 92.0%
    "SYPUSD_otc": 550,  # SYP/USD OTC - 92.0%
    "TNDUSD_otc": 532,  # TND/USD OTC - 92.0%
    "UAHUSD_otc": 558,  # UAH/USD OTC - 54.0%
    "USDARS_otc": 506,  # USD/ARS OTC - 58.0%
    "USDBDT_otc": 500,  # USD/BDT OTC - 57.0%
    "USDBRL_otc": 502,  # USD/BRL OTC - 85.0%
    "USDCAD": 61,  # USD/CAD - 50.0%
    "USDCAD_otc": 91,  # USD/CAD OTC - 92.0%
    "USDCHF": 62,  # USD/CHF - 50.0%
    "USDCHF_otc": 92,  # USD/CHF OTC - 52.0%
    "USDCLP_otc": 525,  # USD/CLP OTC - 92.0%
    "USDCNH_otc": 467,  # USD/CNH OTC - 53.0%
    "USDCOP_otc": 515,  # USD/COP OTC - 81.0%
    "USDDZD_otc": 508,  # USD/DZD OTC - 92.0%
    "USDEGP_otc": 513,  # USD/EGP OTC - 92.0%
    "USDIDR_otc": 504,  # USD/IDR OTC - 68.0%
    "USDINR_otc": 202,  # USD/INR OTC - 70.0%
    "USDJPY": 63,  # USD/JPY - 50.0%
    "USDJPY_otc": 93,  # USD/JPY OTC - 62.0%
    "USDMXN_otc": 509,  # USD/MXN OTC - 92.0%
    "USDMYR_otc": 523,  # USD/MYR OTC - 41.0%
    "USDPHP_otc": 511,  # USD/PHP OTC - 63.0%
    "USDPKR_otc": 517,  # USD/PKR OTC - 91.0%
    "USDRUB_otc": 199,  # USD/RUB OTC - 44.0%
    "USDSGD_otc": 526,  # USD/SGD OTC - 59.0%
    "USDTHB_otc": 521,  # USD/THB OTC - 78.0%
    "USDVND_otc": 519,  # USD/VND OTC - 82.0%
    "YERUSD_otc": 528,  # YER/USD OTC - 92.0%
    "ZARUSD_otc": 556,  # ZAR/USD OTC - 77.0%

    # INDEX - 24 ativos
    "100GBP": 315,  # 100GBP - 45.0%
    "100GBP_otc": 403,  # 100GBP OTC - 45.0%
    "AEX25": 449,  # AEX 25 - 45.0%
    "AUS200": 305,  # AUS 200 - 37.0%
    "AUS200_otc": 306,  # AUS 200 OTC - 67.0%
    "CAC40": 455,  # CAC 40 - 45.0%
    "D30EUR": 318,  # D30/EUR - 45.0%
    "D30EUR_otc": 406,  # D30EUR OTC - 45.0%
    "DJI30": 322,  # DJI30 - 45.0%
    "DJI30_otc": 409,  # DJI30 OTC - 45.0%
    "E35EUR": 314,  # E35EUR - 45.0%
    "E35EUR_otc": 402,  # E35EUR OTC - 45.0%
    "E50EUR": 319,  # E50/EUR - 45.0%
    "E50EUR_otc": 407,  # E50EUR OTC - 45.0%
    "F40EUR": 316,  # F40/EUR - 45.0%
    "F40EUR_otc": 404,  # F40EUR OTC - 45.0%
    "H33HKD": 463,  # HONG KONG 33 - 45.0%
    "JPN225": 317,  # JPN225 - 45.0%
    "JPN225_otc": 405,  # JPN225 OTC - 45.0%
    "NASUSD": 323,  # US100 - 45.0%
    "NASUSD_otc": 410,  # US100 OTC - 45.0%
    "SMI20": 466,  # SMI 20 - 45.0%
    "SP500": 321,  # SP500 - 45.0%
    "SP500_otc": 408,  # SP500 OTC - 45.0%

    # STOCK - 40 ativos
    "#AAPL": 5,  # Apple - 50.0%
    "#AAPL_otc": 170,  # Apple OTC - 92.0%
    "#AXP": 140,  # American Express - 50.0%
    "#AXP_otc": 291,  # American Express OTC - 92.0%
    "#BA": 8,  # Boeing Company - 50.0%
    "#BA_otc": 292,  # Boeing Company OTC - 82.0%
    "#CSCO": 154,  # Cisco - 45.0%
    "#CSCO_otc": 427,  # Cisco OTC - 71.0%
    "#FB": 177,  # FACEBOOK INC - 50.0%
    "#FB_otc": 187,  # FACEBOOK INC OTC - 92.0%
    "#INTC": 180,  # Intel - 25.0%
    "#INTC_otc": 190,  # Intel OTC - 92.0%
    "#JNJ": 144,  # Johnson & Johnson - 50.0%
    "#JNJ_otc": 296,  # Johnson & Johnson OTC - 57.0%
    "#JPM": 20,  # JPMorgan Chase & Co - 50.0%
    "#MCD": 23,  # McDonald's - 50.0%
    "#MCD_otc": 175,  # McDonald's OTC - 92.0%
    "#MSFT": 24,  # Microsoft - 50.0%
    "#MSFT_otc": 176,  # Microsoft OTC - 78.0%
    "#PFE": 147,  # Pfizer Inc - 50.0%
    "#PFE_otc": 297,  # Pfizer Inc OTC - 92.0%
    "#TSLA": 186,  # Tesla - 50.0%
    "#TSLA_otc": 196,  # Tesla OTC - 85.0%
    "#XOM": 153,  # ExxonMobil - 45.0%
    "#XOM_otc": 426,  # ExxonMobil OTC - 88.0%
    "AMD_otc": 568,  # Advanced Micro Devices OTC - 90.0%
    "AMZN_otc": 412,  # Amazon OTC - 92.0%
    "BABA": 183,  # Alibaba - 50.0%
    "BABA_otc": 428,  # Alibaba OTC - 88.0%
    "CITI": 326,  # Citigroup Inc - 50.0%
    "CITI_otc": 413,  # Citigroup Inc OTC - 92.0%
    "COIN_otc": 570,  # Coinbase Global OTC - 53.0%
    "FDX_otc": 414,  # FedEx OTC - 84.0%
    "GME_otc": 566,  # GameStop Corp OTC - 28.0%
    "MARA_otc": 572,  # Marathon Digital Holdings OTC - 92.0%
    "NFLX": 182,  # Netflix - 50.0%
    "NFLX_otc": 429,  # Netflix OTC - 88.0%
    "PLTR_otc": 562,  # Palantir Technologies OTC - 38.0%
    "VISA_otc": 416,  # VISA OTC - 84.0%
    "VIX_otc": 560,  # VIX OTC - 57.0%

}


# WebSocket regions with their URLs
class REGION:
    """WebSocket region endpoints"""

    REGIONS = {
        "EUROPA": "wss://api-eu.po.market/socket.io/?EIO=4&transport=websocket",
        "SEYCHELLES": "wss://api-sc.po.market/socket.io/?EIO=4&transport=websocket",
        "HONGKONG": "wss://api-hk.po.market/socket.io/?EIO=4&transport=websocket",
        "SERVER1": "wss://api-spb.po.market/socket.io/?EIO=4&transport=websocket",
        "FRANCE2": "wss://api-fr2.po.market/socket.io/?EIO=4&transport=websocket",
        "UNITED_STATES4": "wss://api-us4.po.market/socket.io/?EIO=4&transport=websocket",
        "UNITED_STATES3": "wss://api-us3.po.market/socket.io/?EIO=4&transport=websocket",
        "UNITED_STATES2": "wss://api-us2.po.market/socket.io/?EIO=4&transport=websocket",
        "DEMO": "wss://demo-api-eu.po.market/socket.io/?EIO=4&transport=websocket",
        "DEMO_2": "wss://try-demo-eu.po.market/socket.io/?EIO=4&transport=websocket",
        "UNITED_STATES": "wss://api-us-north.po.market/socket.io/?EIO=4&transport=websocket",
        "RUSSIA": "wss://api-msk.po.market/socket.io/?EIO=4&transport=websocket",
        "SERVER2": "wss://api-l.po.market/socket.io/?EIO=4&transport=websocket",
        "INDIA": "wss://api-in.po.market/socket.io/?EIO=4&transport=websocket",
        "FRANCE": "wss://api-fr.po.market/socket.io/?EIO=4&transport=websocket",
        "FINLAND": "wss://api-fin.po.market/socket.io/?EIO=4&transport=websocket",
        "SERVER3": "wss://api-c.po.market/socket.io/?EIO=4&transport=websocket",
        "ASIA": "wss://api-asia.po.market/socket.io/?EIO=4&transport=websocket",
        "SERVER4": "wss://api-us-south.po.market/socket.io/?EIO=4&transport=websocket",
    }

    @classmethod
    def get_all(cls, randomize: bool = True) -> List[str]:
        """Get all region URLs"""
        if randomize:
            urls = list(cls.REGIONS.values())
            random.shuffle(urls)
            return urls
        else:
            return cls.get_priority_regions()

    @classmethod
    def get_all_regions(cls) -> Dict[str, str]:
        """Get all regions as a dictionary"""
        return cls.REGIONS.copy()

    from typing import Optional

    @classmethod
    def get_regions(cls, region_name: str) -> Optional[str]:
        """Get specific region URL"""
        return cls.REGIONS.get(region_name.upper())

    @classmethod
    def get_demo_regions(cls) -> List[str]:
        """Get demo region URLs in priority order"""
        demo_urls = []
        priority_demos = ["DEMO", "DEMO_2"]
        
        for name in priority_demos:
            if name in cls.REGIONS:
                demo_urls.append(cls.REGIONS[name])
        
        return demo_urls
    
    @classmethod
    def get_priority_regions(cls) -> List[str]:
        """Get production regions in priority order - Europa first"""
        priority_order = [
            "EUROPA",
            "SEYCHELLES", 
            "FRANCE",
            "UNITED_STATES",
            "UNITED_STATES2",
            "UNITED_STATES3",
            "UNITED_STATES4",
            "SERVER1",
            "SERVER2",
            "SERVER3",
            "SERVER4",
            "ASIA",
            "HONGKONG",
            "INDIA",
            "RUSSIA",
            "FRANCE2",
            "FINLAND"
        ]
        
        priority_urls = []
        for name in priority_order:
            if name in cls.REGIONS:
                priority_urls.append(cls.REGIONS[name])
        
        return priority_urls


# Global constants
REGIONS = REGION()

# Timeframes (in seconds)
TIMEFRAMES = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "30m": 1800,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "1w": 604800,
}

# Connection settings
CONNECTION_SETTINGS = {
    "ping_interval": 20,  # seconds
    "ping_timeout": 10,  # seconds
    "close_timeout": 10,  # seconds
    "max_reconnect_attempts": 5,
    "reconnect_delay": 5,  # seconds
    "message_timeout": 30,  # seconds
}

# API Limits
API_LIMITS = {
    "min_order_amount": 1.0,
    "max_order_amount": 50000.0,
    "min_duration": 5,  # seconds
    "max_duration": 43200,  # 12 hours in seconds
    "max_concurrent_orders": 10,
    "rate_limit": 100,  # requests per minute
}

# Default headers
DEFAULT_HEADERS = {
    "Origin": "https://pocketoption.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}
