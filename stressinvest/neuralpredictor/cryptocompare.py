import requests
import time
import datetime

# API
URL_COIN_LIST = 'https://www.cryptocompare.com/api/data/coinlist/'
URL_PRICE = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'
URL_PRICE_MULTI = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms={}'
URL_PRICE_MULTI_FULL = 'https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}'
URL_HIST_PRICE = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym={}&tsyms={}&ts={}'
URL_AVG = 'https://min-api.cryptocompare.com/data/generateAvg?fsym={}&tsym={}&markets={}'
URL_HISTO = 'https://min-api.cryptocompare.com/data/histo{}?fsym={}&tsym={}&limit={}&aggregate={}&e={}'

# FIELDS
PRICE = 'PRICE'
HIGH = 'HIGH24HOUR'
LOW = 'LOW24HOUR'
VOLUME = 'VOLUME24HOUR'
CHANGE = 'CHANGE24HOUR'
CHANGE_PERCENT = 'CHANGEPCT24HOUR'
MARKETCAP = 'MKTCAP'

# DEFAULTS
CURR = 'USD'

EXCHANGES = {
  'BTC': [
    'Abucoins',
    'BitBay',
    'BitTrex',
    'Bitfinex',
    'Bitstamp',
    'CCCAGG',
    'Cexio',
    'Coinbase',
    'Coinroom',
    'Exmo',
    'Gatecoin',
    'Gemini',
    'HitBTC',
    'Kraken',
    'LiveCoin',
    'LocalBitcoins',
    'Lykke',
    'MonetaGo',
    'Poloniex',
    'QuadrigaCX',
    'Quoine',
    'TheRockTrading',
    'WavesDEX',
    'Yobit',
    'itBit',
    ],

  'LTC': [
    'BitBay',
    'BitTrex',
    'Bitfinex',
    'Bitstamp',
    'CCCAGG',
    'Coinbase',
    'Coinroom',
    'Exmo',
    'HitBTC',
    'Kraken',
    'Poloniex',
    'Yobit',
    ],

  'DASH': [
    'BitTrex',
    'Bitfinex',
    'CCCAGG',
    'Coinroom',
    'Exmo',
    'HitBTC',
    'Kraken',
    'LiveCoin',
    'Poloniex',
    'Quoine',
    'Yobit',
    ],

  'ETH': [
    'BitBay',
    'BitTrex',
    'Bitfinex',
    'Bitstamp',
    'CCCAGG',
    'Cexio',
    'Coinbase',
    'Coinroom',
    'Exmo',
    'Gatecoin',
    'Gemini',
    'HitBTC',
    'Kraken',
    'LiveCoin',
    'Lykke',
    'Poloniex',
    'Quoine',
    'WavesDEX',
    'Yobit',
    ],

  'IOT': [
    'Bitfinex',
    'CCCAGG',
    ],

  'BCH': [
    'BitBay',
    'BitTrex',
    'Bitfinex',
    'CCCAGG',
    'Coinbase',
    'Coinroom',
    'Exmo',
    'HitBTC',
    'Kraken',
    'Poloniex',
    'Quoine',
    'Yobit',
    ],

  'XRP': [
    'Bitstamp',
    'Poloniex',
    'BitTrex',
    'Kraken',
    'Bitfinex',
    'HitBTC',
    'CCCAGG',
    'Exmo',
    ],

  'EDO': [
    'Bitfinex',
    'HitBTC',
    'CCCAGG',
    ],

  'ETC': [
    'BitTrex',
    'Bitfinex',
    'CCCAGG',
    'Exmo',
    'HitBTC',
    'Kraken',
    'Poloniex',
    'Yobit',
    ],

  'XVG': [
    'CCCAGG',
    'HitBTC',
    'Yobit',
    ],

}

DB_TABLE_ORDER = [
    u'TIMESTAMP',
    u'LASTUPDATE',
    u'OPEN24HOUR',
    u'OPENDAY',
    u'LOWDAY',
    u'HIGHDAY',
    u'CHANGE24HOUR',
    u'CHANGEPCT24HOUR',
    u'CHANGEDAY',
    u'MKTCAP',
    u'CHANGEPCTDAY',
    u'HIGH24HOUR',
    u'VOLUMEDAY',
    u'VOLUMEDAYTO',
    u'TOTALVOLUME24HTO',
    u'PRICE',
    u'LOW24HOUR',
    u'VOLUME24HOURTO',
    u'VOLUME24HOUR',
]

FULL_COIN_LIST = [u'LIFE', u'XBY', u'CSNO', u'XBS', u'ORME', u'NYC', u'AGS',
u'XBC', u'SPX', u'MEGA', u'SPR', u'SPT', u'EDDIE', u'CHASH', u'SPM', u'SPN',
u'SPA', u'SPC', u'XPH', u'XPO', u'XPM', u'GP', u'XPB', u'XPD', u'XPY', u'GB',
u'XPS', u'BTTF', u'BYC', u'IXT', u'JNS', u'SND', u'MAR', u'BTX*', u'WEALTH',
u'PRIX', u'MAY', u'MAX', u'SNM', u'SNK', u'MAC', u'PQT', u'SNS', u'MAG',
u'MAN', u'SPHTX', u'BEN', u'CRTM', u'EVC', u'EVX', u'CARBON', u'EVR', u'YBC',
u'BET', u'OXY', u'LSD', u'LSK', u'TTT', u'TTC', u'VLT', u'Z2', u'GRW', u'GRT',
u'GRS', u'SOLE', u'GRX', u'GRF', u'GRE', u'GRC', u'KRONE', u'GRM', u'ZEPH',
u'ATKN', u'NOO', u'MPRO', u'OPAL', u'CTT', u'CTR', u'FJC', u'CTX', u'FUCK',
u'CTC', u'CTO', u'BLUE', u'MOBI', u'WHL', u'QTUM', u'DROP', u'DOVU', u'UNITY',
u'1ST', u'UNITS', u'DBET', u'EDC', u'BWK', u'EDG', u'FRN', u'PLU', u'RLC',
u'EDR', u'ORO', u'RLX', u'WAVES', u'LMC', u'ORB', u'JIF', u'DPP', u'MOTO',
u'SIFT', u'UKG', u'MOON', u'LC', u'LA', u'ONG', u'AXIOM', u'KEY*', u'PLBT',
u'JIO', u'MOOND', u'GBRC', u'LOAN*', u'HEAT', u'PTS*', u'ANTI', u'RZR',
u'EXCL', u'ANTC', u'CFI', u'CFD', u'CFC', u'WSC', u'PNK', u'JANE', u'PNC',
u'CALC', u'PND', u'HAMS', u'XQN', u'KAPU', u'ATOM*', u'ATB', u'PRE', u'PRG',
u'SAN', u'PRC', u'PRM', u'PRL', u'PRO', u'DTCT', u'404', u'PRP', u'SAR',
u'JOK', u'PRX', u'CHA', u'AST*', u'CHC', u'MRY', u'MINEX', u'MRT', u'MRV',
u'MRP', u'DTC*', u'NEVA', u'SNC', u'APX', u'MTRC', u'JNT', u'DBG', u'HONEY',
u'MONEY', u'APC', u'DBR', u'GREXIT', u'BT1', u'BT2', u'ISL', u'MAT', u'PIRL',
u'TKN', u'HMP', u'SNT', u'NLC', u'TKR', u'TKS', u'NLG', u'SUB*', u'DBTC',
u'MAD', u'DLC', u'GCC', u'PAYP', u'ORLY', u'GCN', u'DLR', u'SEEDS', u'SHADE',
u'DLT', u'BTQ', u'BTS', u'XCE', u'XCJ', u'SSV', u'XCN', u'BTX', u'BTZ', u'XCR',
u'PINKX', u'COIN*', u'PTOY', u'XCT', u'TIME', u'BTM', u'SSD', u'PROC', u'WYR',
u'SPOTS', u'RMS', u'ECC', u'LANA', u'ECO', u'LNK', u'RBIES', u'BET*', u'CLICK',
u'ALQO', u'YAY', u'TRIG', u'TRIA', u'EUC', u'BBT', u'BBR', u'YAC', u'LEPEN',
u'SOCC', u'TUR', u'VMC', u'TWIST', u'H2O', u'DEUR', u'NBIT', u'AIR*', u'AGRS',
u'CASH*', u'CYP', u'CYT', u'POT', u'FYN', u'POS', u'CLOUT', u'CYC', u'STALIN',
u'FYP', u'808', u'CYG', u'LBTC', u'POE', u'LEND', u'ARNA*', u'SHORTY', u'SKIN',
u'MILO', u'DICE', u'R', u'NICE', u'CKC', u'PAY', u'SWARM', u'WDC', u'PAK',
u'CFT*', u'DCN', u'DCK', u'BRDD', u'DCC', u'DCY', u'DCT', u'DCR', u'KC',
u'CHIEF', u'SIGU', u'SIGT', u'SCRT', u'WEX', u'SRC*', u'SEND', u'CDX*',
u'ANAL', u'ROOTS', u'DMD', u'ODNT', u'OROC', u'AEC', u'DMT', u'BOAT', u'XDC',
u'XDB', u'ACOIN', u'CRDS', u'XDN', u'RIDE', u'BUK', u'XDQ', u'XDP', u'365',
u'BIT16', u'XRL', u'XRE', u'XRA', u'XRB', u'XRP', u'PSI', u'DGDC', u'PSY',
u'KURT', u'GAT', u'PST', u'MOD', u'BCN', u'KMD', u'BCH', u'ETT', u'GIVE',
u'BCD', u'BCF', u'QVT', u'ETC', u'BCX', u'BCY', u'BOMB', u'ETH', u'ETN',
u'BCR', u'VRS', u'DETH', u'VRC', u'C2', u'VRM', u'CJ', u'CC', u'SRN', u'CF',
u'INS', u'PCN', u'SRT', u'CS', u'MYC', u'LDOGE', u'1CR', u'NMR', u'IOC',
u'NAMO', u'NMB', u'NMC', u'EVENT', u'LOC', u'FRWC', u'LOG', u'CSMIC', u'IMPCH',
u'EB3', u'CVC', u'PIZZA', u'QRK', u'QRL', u'DBIC', u'SWT', u'DBIX', u'GBYTE',
u'X8X', u'XCASH', u'HTML5', u'HPC', u'GHOUL', u'LGBTQ', u'ARDR', u'EBS',
u'xGOx', u'TRUST', u'ELITE', u'SPANK', u'EBZ', u'ZYD', u'DRZ', u'CANN', u'DRP',
u'DRS', u'DRT', u'KOLION', u'STEPS', u'DRA', u'DRC', u'XBOT', u'NVST',
u'SWEET', u'IOU', u'IOT', u'IOP', u'HVCO', u'ION', u'UIS', u'RVT', u'DRM8',
u'DRACO', u'KRAK', u'EVIL', u'NANAS', u'OK', u'UBQ', u'CXT', u'GRID', u'CXC',
u'WRC*', u'HZ', u'XSP', u'XST', u'CAN*', u'XSB', u'XSH', u'XSI', u'VIOR',
u'CTIC', u'MNX', u'MNY', u'SKR*', u'SCN', u'NEBL', u'PTC', u'PTA', u'MNM',
u'SCT', u'MNC', u'NEBU', u'MNE', u'SCR', u'PBT', u'CJC', u'CAPP', u'FCS',
u'WARP', u'PBC', u'RHOC', u'PBL', u'EGAS', u'RCN*', u'CJT', u'MMXVI', u'AVT',
u'FLVR', u'SENSE', u'XCO', u'AVE', u'AVA', u'SUB', u'DEEP', u'GAME', u'SUR',
u'SUP', u'TEK', u'GEMZ', u'TEC', u'NBT', u'FSC2', u'NBL', u'TER', u'TES',
u'BTG*', u'CORE', u'ADT', u'GRWI', u'DNA', u'GML', u'GMC', u'ADZ', u'ADX',
u'HUSH', u'DNT', u'GMX', u'ADB', u'ADC', u'DNR', u'ADN', u'ADL', u'EDRC',
u'GMT', u'ODMC', u'BRX', u'XEL', u'XEM', u'XEN', u'BRO', u'CIRC', u'BRK',
u'JPC', u'BLAZR', u'TDFB', u'DISK', u'QCN', u'OBITS', u'MAT*', u'EAC', u'RKC',
u'TRON', u'KUSH', u'ETHD', u'METAL', u'MNZ', u'BCD*', u'ETHS', u'VEG', u'VSX',
u'VSL', u'SOAR', u'EOC', u'MNT', u'BLAS', u'DIVX', u'RYC', u'EOS', u'RYZ',
u'DLISK', u'BUCKS*', u'BLITZ', u'FIT', u'CORAL', u'PIGGY', u'FIL', u'QSP',
u'SNGLS', u'WNET', u'WILD', u'DOGETH', u'PCS', u'CMC', u'HOLD', u'EDO',
u'KUBO', u'M1', u'KLC', u'PCM', u'CMT', u'CMS', u'CMP', u'MAG*', u'WOLF',
u'WOLK', u'FLAP', u'WGC', u'WGO', u'DSH', u'WGR', u'DSB', u'COOL', u'MG',
u'HYPER', u'MC', u'MM', u'INV', u'MN', u'MI', u'TKN*', u'MT', u'INN', u'GBIT',
u'IND', u'DTT*', u'INC', u'REAL', u'DON', u'GLA', u'NETKO', u'GLC', u'GLD',
u'GLX', u'COSS', u'GLT', u'DOT', u'GIFT', u'BST', u'XFC', u'SETH', u'ZOOM',
u'BSD', u'BSC', u'ELLA', u'XTZ', u'MCAR', u'AUR', u'XTC', u'AUT', u'XCS',
u'GRID*', u'SBC', u'SBD', u'TBCX', u'PUT', u'HDG', u'MMC', u'ERT', u'I0C',
u'BAT', u'BAR', u'ERR', u'OMNI', u'XHI', u'RIPO', u'ERY', u'BAY', u'RNDR',
u'BNX', u'BAC', u'ERB', u'ERC', u'BAN', u'XID', u'ERO', u'ZET2', u'PASC',
u'CELL', u'HAC', u'STA', u'STC', u'HODL', u'STH', u'KNC', u'MDC*', u'NEOS',
u'STV', u'STP', u'STS', u'STX', u'TFL', u'EDGE', u'FNT', u'ECOB', u'ELTC2',
u'ROYAL', u'LIV', u'FND', u'LIR', u'LINDA', u'SCL', u'BITOK', u'EQB', u'WTT',
u'UNAT', u'ONX', u'WTC', u'RC', u'XAUR', u'TPG', u'QBT', u'NEC', u'QBC',
u'QBK', u'BASH', u'HRB', u'WISC', u'MLITE', u'TRUMP', u'DT', u'8BIT', u'KAT',
u'KICK', u'COLX', u'EFYT', u'SWING', u'NET', u'XMCC', u'DRC*', u'SLING',
u'PLNC', u'PSEUD', u'UGT', u'ENE', u'ENG', u'ENJ', u'DOGED', u'ENT', u'ENV',
u'RT2', u'ZRX', u'F16', u'RFL', u'ATOM', u'CZC', u'XUP', u'DRXNE', u'ATL',
u'ATM', u'UTIL', u'ATS', u'INF8', u'XUN', u'ATX', u'SEQ', u'PLANET', u'BRAIN',
u'SMART', u'SEN', u'SEL', u'JKC', u'FRC', u'FRE', u'FRD', u'FRK', u'IML',
u'IMS', u'IMX', u'CLV', u'PDC', u'XNC*', u'CLR', u'MTLM3', u'ZEC', u'NUKE',
u'ZED', u'CRC', u'BKX', u'ZEN', u'ZER', u'ZET', u'INFX', u'FOREX', u'SHIFT',
u'DB', u'BPL', u'BTCL*', u'ASAFE2', u'HIRE*', u'DP', u'CESC', u'TGT', u'PIVX',
u'TGC', u'CREDO', u'BOTS', u'XPRO', u'MLN', u'MLS', u'XCRE', u'GOT', u'CFT',
u'NRO', u'NRN', u'NRC', u'NRB', u'XGB', u'NRS', u'XGR', u'QAU', u'GXC*', u'WC',
u'ADA', u'GHS', u'HSR', u'LTBC', u'HSP', u'HST', u'RIC', u'ARI*', u'YOVI',
u'HAL', u'XRED', u'PASL', u'RISE', u'EQT', u'XIN', u'BNT', u'BNK', u'EQM',
u'ENTER', u'BNC', u'BNB', u'VAPOR', u'SYC', u'ZEIT', u'SYS', u'LXC', u'YES',
u'SPEC', u'EMD', u'EMC', u'EMB', u'BELA', u'ZNT', u'EMT', u'RGC', u'IXC',
u'MIS', u'DAXX', u'LDM', u'FOOD', u'SMSR', u'ROOT', u'ARENA', u'MBRS', u'CLUB',
u'CLUD', u'SMAC', u'ECHT', u'FUNC', u'DNET', u'TODAY', u'INXT', u'ULTC',
u'KNC**', u'WINK', u'FLIXX', u'WINE', u'COR', u'PEX', u'ILC', u'COV', u'COX',
u'CHIP', u'FSN', u'COC', u'COB', u'FST', u'FIST', u'PEC', u'ZBC', u'THNX',
u'PWR', u'WAN', u'FAIR', u'DIME', u'COMM', u'SANDG', u'WAY', u'WAX', u'OPP',
u'GROW', u'SNRG', u'UFO', u'LUCKY', u'RNC', u'RUP', u'ALIS', u'TELL', u'DIM',
u'SAT2', u'GNT', u'RUBIT', u'INSN', u'AIR', u'MKR', u'GNJ', u'AID', u'GNO',
u'AIB', u'VIBE', u'VPRC', u'ATFS', u'ECASH', u'NSR', u'OLYMP', u'UTC', u'XVP',
u'UTH', u'AERO', u'UTN', u'IW', u'CLD', u'VOLT', u'IN', u'XVC', u'MRS', u'XVE',
u'XVG', u'SDP', u'SDC', u'VLTC', u'HBN', u'PARA', u'EPY', u'XJO', u'BOS',
u'NAN', u'BOU', u'XUC*', u'PART', u'NAV', u'CHESS', u'BON', u'HBT', u'BOB',
u'SHLD', u'BOG', u'MBIT', u'SXC', u'4CHN', u'LYB', u'LYC', u'JVY', u'BQC',
u'GOTX', u'XSPEC', u'BQX', u'GXC', u'2GIVE', u'BAC*', u'PEN', u'EBET', u'COE',
u'BTPL', u'FLY', u'FLX', u'LKK', u'FLP', u'FLASH', u'FLT', u'32BIT', u'APT',
u'FLO', u'LKY', u'FIND', u'VDO', u'MEDI', u'ESP', u'CABS*', u'AION', u'CON',
u'TRI', u'USDE', u'TRK', u'TRA', u'TRC', u'ETHB', u'USDT', u'TRX', u'KOBO',
u'ATCC', u'SAK', u'TRV', u'SFE', u'HTC', u'LTCX', u'MUDRA', u'KCN', u'ALTCOM',
u'LTCR', u'KCS', u'LTCD', u'BCAP', u'ZUR', u'QASH', u'FIBRE', u'NXTI', u'CASH',
u'CABS', u'SILK', u'MOJO', u'BCO*', u'MCRN', u'TECH', u'ODN', u'UET', u'RRT',
u'ICOS', u'ELM', u'ELC', u'J', u'ELE', u'RDD', u'ICOB', u'ELS', u'RDN',
u'AEON', u'ICOO', u'ICON', u'LEA', u'SMLY', u'LEO', u'EXIT', u'LEV', u'STHR',
u'CQST', u'USC', u'ONION', u'CAT*', u'ARGUS', u'BRONZ', u'XWC', u'BNB*',
u'AURS', u'STAR*', u'PXI', u'XIOS', u'PXL', u'PXC', u'PHR*', u'CNT', u'ICN',
u'FIRE', u'ICB', u'ICE', u'START', u'CND', u'ICX', u'CNC', u'CNO', u'CNL',
u'ZCG', u'KAYI', u'ZCC', u'ZCL', u'SNOV', u'PFR', u'FAZZ', u'EZC', u'INDI',
u'RATIO', u'HMQ', u'TRICK', u'SIB', u'JWL', u'MOIN', u'ACES', u'GAIA', u'TAT',
u'TAU', u'COV*', u'TAP', u'BBT*', u'TKT', u'ALTOCAR', u'TAG', u'TAB', u'TAM',
u'TAJ', u'TAK', u'PRIME', u'BTCZ', u'XPTX', u'BTCR', u'GIZ', u'EON', u'GIG',
u'BTCM', u'BTCL', u'REBL', u'GIM', u'BTCE', u'BTCD', u'LOOK', u'NPC', u'NPX',
u'AHT', u'RICE', u'GUE', u'TSE', u'GUP', u'BOXY', u'HUC', u'SPORT', u'BLX',
u'BLU', u'TRCT', u'HCC', u'SJCX', u'BLK', u'CRACK', u'SPRTS', u'UFR', u'BLC',
u'GCR', u'BTCS', u'EMC2', u'EKO', u'EKN', u'REX', u'REP', u'REQ', u'REV',
u'XMRG', u'REC', u'REA', u'RED', u'REE', u'CLAM', u'FCT', u'LFC', u'LGD*',
u'FUZZ', u'FCN', u'LTS', u'FC2', u'LTC', u'LTB', u'LTA', u'VEE', u'LTG',
u'LTD', u'VEN', u'LTH', u'SP', u'HNC*', u'ST', u'SH', u'SC', u'GUNS', u'GLYPH',
u'RUSTBITS', u'XCI', u'FUTC', u'CAS', u'CAP', u'CAV', u'CAT', u'CAM', u'CAB',
u'STEX', u'CAG', u'AR*', u'INCP', u'MRSA', u'BTD', u'ELIX', u'PGL', u'XCP',
u'COAL', u'DYN', u'BTA', u'WCT', u'611', u'RAIN', u'LUX*', u'ZRC', u'CREA',
u'CACH', u'NET*', u'NIMFA', u'ZNA', u'XXX', u'MIL', u'ZNE', u'MIN', u'CNBC',
u'ACT*', u'LINK', u'DKC', u'GHC', u'ZNY', u'MIV', u'MEOW', u'STRAT', u'VIDZ',
u'XZC', u'DGORE', u'URO', u'IPC', u'PYP', u'SFR', u'ASTRO', u'PYN', u'PYC',
u'SFC', u'NAS2', u'XLM', u'NGC', u'KORE', u'XLC', u'XLB', u'BCCOIN',
u'BLOCKPAY', u'XLR', u'BMC', u'DENT', u'BMT', u'UTK', u'SHP', u'BM*', u'NUBIS',
u'EA', u'EC', u'POSW', u'POST', u'CMPCO', u'EQ', u'EBCH', u'TRIBE', u'ECA',
u'MGO', u'PULSE', u'AMIS', u'STOCKBET', u'ADST', u'LUX', u'SPHR', u'XUC',
u'OCTO', u'LUN', u'TENNET', u'EPY*', u'SDAO', u'QTZ', u'BITB', u'WPR', u'BITZ',
u'X2', u'QTL', u'BITS', u'BTE', u'VTA', u'VTC', u'XC', u'XG', u'ATMS', u'VTR',
u'XAI*', u'VTX', u'XP', u'XT', u'KEK', u'HVN', u'GPL', u'APPC', u'HVC', u'KED',
u'CRAVE', u'KEY', u'KEX', u'BTG', u'SCRPT', u'888', u'ZSE', u'WBB', u'DUCK',
u'NDOGE', u'DPAY', u'EMIGR', u'RPC', u'TWLV', u'TEAM', u'NODE', u'RBY', u'RBX',
u'DOPE', u'RBT', u'RBR', u'STORJ', u'STORM', u'HXT', u'VERI', u'HXX', u'DRGN',
u'OTN', u'SMNX', u'LGD', u'OTX', u'BTC', u'ROCK*', u'FUEL', u'AXR', u'AXT',
u'UQC', u'BTB', u'VTY', u'BIGUP', u'B@', u'LCASH', u'RDN*', u'TRIP', u'PZM',
u'GSY', u'IWT', u'GSX', u'C20', u'KNC*', u'DASH', u'BSTAR', u'FRAZ', u'BURST',
u'ZAB', u'QWARK', u'MZC', u'PHS', u'PHR', u'XSEED', u'GUESS', u'JOBS', u'SKR',
u'SKY', u'SKB', u'TRST', u'GES', u'WISH*', u'GAKH', u'TCR', u'SOUL', u'GEA',
u'GEO', u'GEN', u'LIMX', u'ZOI', u'VOISE', u'DGMS', u'VISIO', u'DDF', u'EBTC',
u'AND', u'ANC', u'BITCNY', u'ANT', u'NVC', u'S8C', u'TMT', u'VUC', u'PRE*',
u'TMC', u'TME', u'RIYA', u'KDC', u'MND', u'NDC', u'XMG', u'BCPT', u'XMY',
u'KRB', u'KRC', u'XMR', u'XMS', u'GOAT', u'PRES', u'CHOOF', u'RCX', u'WSH',
u'ZSC', u'HYP', u'RCN', u'WSX', u'ARCO', u'ARCH', u'RCC', u'LK7', u'VEC2',
u'ROCK', u'BUCKS', u'IBANK', u'GOOD', u'GOON', u'YOC', u'LVG', u'007', u'CNMT',
u'PINK', u'NXTTY', u'PING', u'PURA', u'PURE', u'RPX', u'ARC*', u'NYAN', u'CCX',
u'STCN', u'DARK', u'CCN', u'CCC', u'OAX', u'PIO', u'PIE', u'PIX', u'FLIK',
u'UAEC', u'MYB', u'BTDX', u'WMC', u'XPOKE', u'FAME', u'SUMO', u'ALEX', u'NLC2',
u'HNC', u'OC', u'MAID', u'NTRN', u'SCT*', u'HALLO', u'DES', u'EBST', u'CLOAK',
u'JDC', u'MWC', u'ZLQ', u'DEM', u'DEA', u'DEB', u'GJC', u'BLOCK', u'MYST*',
u'POLL', u'AMC', u'AMB', u'AMY', u'AMP', u'AMS', u'AMT', u'XBTS', u'B3',
u'CWV', u'MDL', u'ENRG', u'POWR', u'IVZ', u'ACC', u'OPES', u'EMPC', u'ACE',
u'NEF', u'XNX', u'ACN', u'XNA', u'XNC', u'ACP', u'XNG', u'ACT', u'RING',
u'NEU', u'XNN', u'WABI', u'CRAFT', u'EARTH', u'SALT', u'MEME', u'VRP*',
u'INPAY', u'MED', u'HIRE', u'MEC', u'NAUT', u'MET', u'GDC', u'BOOM', u'MER',
u'SSTC', u'CREVA', u'WINGS', u'FONZ', u'EQUAL', u'CRPS', u'TX', u'OLDSF',
u'POINTS', u'TNT', u'AC', u'AE', u'ADCN', u'AM', u'AV', u'GVT', u'VZT',
u'RYCN', u'NKA', u'NKC', u'BTCRED', u'BON*', u'BITSD', u'NOTE', u'EZM', u'KGC',
u'MCAP', u'NKT', u'SUPER', u'INCNT', u'UNIFY', u'CPC', u'DCS.', u'XDE2',
u'DRKT', u'MONA', u'ARPA', u'MANA', u'DRKC', u'BMXT', u'HEEL', u'VOYA', u'WRC',
u'NOBL', u'HZT', u'WRT', u'ARBI', u'LAB', u'PAC', u'LAZ', u'LAT', u'FFC',
u'DTC', u'DTB', u'BOSON', u'VERSA', u'DTR', u'DTT', u'NTK', u'CCT*', u'AHT*',
u'FTP', u'PEPECASH', u'1337', u'FTC', u'CBD', u'MXT', u'RADI', u'RADS',
u'RUPX', u'CBX', u'XBL', u'FX', u'CRYPT', u'IFLT', u'SMT', u'POLY', u'FC',
u'SMF', u'ACID', u'SMC', u'GGS', u'MDC', u'MDA', u'MDT', u'WOMEN', u'DFT',
u'BENJI', u'ALN', u'ALF', u'ZRC*', u'ALC', u'MARV', u'NTM', u'NTO', u'MARS',
u'NTC', u'XCXT', u'MARX', u'OS76', u'WEB', u'TOR', u'SOIL', u'RIPT', u'TOT',
u'TOM', u'FRAC', u'TOA', u'HUGE', u'ETBT', u'ETBS', u'BULLS', u'ABC', u'HGT',
u'NZC', u'SCORE', u'ABT', u'BHC*', u'KTK', u'ABY', u'BHC', u'CRAB', u'ZXT',
u'ABYSS', u'EGO', u'DUTCH', u'EGC', u'EGG', u'IMPS', u'COIN', u'FGZ', u'LBC',
u'2015', u'DCRE', u'MMNXT', u'YMC', u'BFX', u'FIRST', u'VIB', u'VIA', u'VIP',
u'VIU', u'PUPA', u'LOCI', u'IFT', u'STAR', u'OCL', u'GOLOS', u'IFC', u'FUN',
u'NEOG', u'LENIN', u'PKT', u'COFI', u'CAIX', u'PKB', u'HILL', u'ELTCOIN',
u'RUST', u'STO', u'CSH', u'WOP', u'CSC', u'DIGS', u'NEO', u'MMXIV', u'STU',
u'DOGE', u'RBIT', u'8S', u'HEDG', u'STA*', u'MUU', u'STEEM', u'JBS', u'CHAO',
u'MUE', u'CURE', u'2BACCO', u'CHAT', u'DGB', u'DGC', u'MONETA', u'DGD', u'AST',
u'BTLC', u'WORM', u'NUM', u'MASS', u'ASN', u'DFBT', u'CSTL', u'DUO', u'DUB',
u'DUX', u'UNB', u'UNC', u'UNF', u'UNI', u'UNO', u'OMC', u'OMA', u'OMG',
u'NEU*', u'CVCOIN', u'ESC*', u'GBT', u'VIVO', u'KR', u'HAZE', u'DANK', u'ITT',
u'LEMON', u'BIO', u'BIC', u'SAND', u'GBX', u'BIS', u'BIP', u'SLR', u'SLS',
u'SLM', u'CRNK', u'SLG', u'MCO', u'MCN', u'MCI', u'BBCC', u'GFT', u'AMMO',
u'EXE', u'EXB', u'CLINT', u'WAND', u'EXN', u'BSTK', u'EAGS', u'EXP', u'SCASH',
u'LQD', u'BSTY', u'BEST', u'EXY', u'GLOBE', u'TZC', u'VNT', u'ELT', u'BITUSD',
u'N7', u'BamitCoin', u'ZENI', u'SONG', u'BOST', u'THS', u'BOSS', u'GPU',
u'THC', u'CETI', u'CINNI', u'XID*', u'NIO', u'LINX', u'NIC', u'KIN', u'ETP',
u'INSANE', u'FDC', u'WBTC', u'CRW', u'CRX', u'SYNC', u'CRB', u'STR*', u'SYNX',
u'CRE', u'ROUND', u'CRM', u'PX', u'AERM', u'SWIFT', u'TAGR', u'3DES', u'EFL',
u'UNIQ', u'UNIT', u'OPT', u'MARYJ', u'TESLA', u'FRST', u'NTCC', u'SAFEX',
u'BUZZ', u'RNS', u'DVC', u'FLLW', u'ICASH', u'UMC', u'RBTC', u'MUSIC', u'OLV',
u'QORA', u'BLRY', u'XWT', u'VIRAL', u'MSR', u'IEC', u'OBS', u'CCRB', u'PLR',
u'ILCT', u'CDN', u'PLX', u'CDT', u'PSB', u'RHEA', u'PLM', u'CDX', u'BXT',
u'WASH', u'BXC', u'SHREK', u'BTM*', u'PPC', u'MBI', u'GAY', u'SOJ', u'GAS',
u'GAP', u'GAM', u'PPP', u'PPT', u'MBT', u'PPY', u'MTX', u'JCR', u'MTR',
u'NETC', u'AUTH', u'BRIT', u'MTK', u'MTH', u'MTN', u'MTL', u'MAPC', u'PTC*',
u'ART', u'TPAY', u'ARB', u'ARC', u'ARG', u'ARI', u'ARK', u'BTMI', u'ARM',
u'ARN', u'TIX', u'TIT', u'BM', u'SOON', u'BT', u'TIO', u'BQ', u'BS', u'TIE',
u'GSM', u'TIA', u'TIO*', u'TIC', u'APEX', u'HKG', u'NXT', u'NXS', u'BOLI',
u'XAS', u'XAU', u'NXE', u'XAI', u'NXC', u'CRAIG', u'SQP', u'VOOT', u'COVAL',
u'BVC', u'SCOT', u'SCOR', u'SQL', u'JUDGE', u'BTCRY', u'ETG', u'YOYOW',
u'CUBE', u'QSLV', u'ETK', u'KING', u'ROK', u'LAB*', u'UBIQ', u'ICC', u'FLDC',
u'OSC', u'ROS', u'TAAS', u'BDG', u'CPAY', u'BDL', u'CNX', u'BDR', u'BERN',
u'LRC', u'ZECD', u'MYST', u'UP', u'UR', u'VOT', u'VOX', u'OPTION', u'SPKTR',
u'BIOB', u'CND*', u'CGA', u'GRAV', u'BIOS', u'GRAM', u'MINE', u'DIEM', u'MINT',
u'WIC', u'CMT*', u'8BT', u'BRAT', u'WIZ', u'DGPT', u'NULS', u'SRC', u'NEWB',
u'MST', u'CIN', u'MSP', u'CIR', u'CWXT', u'CIX', u'MSC', u'KARM', u'42',
u'DAT', u'DAR', u'DAS', u'DAY', u'PLAY', u'IGNIS', u'SPACE', u'CHILD', u'U',
u'JPC*', u'AMBER', u'DATA', u'ANCP', u'MUT']

COIN_LIST = ['LTC', 'BTC', 'ETH', 'XRP', 'DASH', 'IOT', 'BCH', 'ETC', 'EDO',
        'XVG']

###############################################################################

def query_cryptocompare(url, errorCheck=False):
    try:
        response = requests.get(url).json()
    except Exception as e:
        print('Error getting coin information. %s' % str(e))
        return None
    if errorCheck and 'Response' in response.keys():
        print('[ERROR] %s' % response['Message'])
        return None
    return response

def format_parameter(parameter):
    if isinstance(parameter, list):
        return ','.join(parameter)
    else:
        return parameter

###############################################################################

def get_coin_list(format=False):
    response = query_cryptocompare(URL_COIN_LIST, False)['Data']
    if format:
        return list(response.keys())
    else:
        return response

# TODO: add option to filter json response according to a list of fields
def get_price(coin, curr=CURR, full=False):
    if full:
        return query_cryptocompare(URL_PRICE_MULTI_FULL.format(format_parameter(coin),
            format_parameter(curr)))
    if isinstance(coin, list):
        return query_cryptocompare(URL_PRICE_MULTI.format(format_parameter(coin),
            format_parameter(curr)))
    else:
        return query_cryptocompare(URL_PRICE.format(coin, format_parameter(curr)))

def get_historical_price(coin, curr=CURR, timestamp=time.time()):
    if isinstance(timestamp, datetime.datetime):
        timestamp = time.mktime(timestamp.timetuple())
    return query_cryptocompare(URL_HIST_PRICE.format(coin, format_parameter(curr), int(timestamp)))

def get_histo(dhm, coin, limit, aggregate, exchange, curr=CURR):
    assert dhm in ('day', 'hour', 'minute')
    return query_cryptocompare(URL_HISTO.format(dhm, coin, curr, limit, aggregate, exchange))

def get_avg(coin, curr, markets):
    response = query_cryptocompare(URL_AVG.format(coin, curr, format_parameter(markets)))
    if response:
        return response['RAW']

if __name__ == '__main__':
    print(get_price('BTC'))
    print(get_price('BTC', full=True))
    ans = get_coin_list(format=True)
    print(get_price(['BTC', 'LTC'], full=True))


