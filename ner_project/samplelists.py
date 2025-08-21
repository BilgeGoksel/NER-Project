# ------------------------------------------------------------------
#  TuM LISTELERIN BIRLEsTIRILIP DOgRULANDIgI GuNCEL KOD BLOgU
# ------------------------------------------------------------------

# --- 1. DuZ (GENEL) LISTELER ---
# Bu listeler, hem uzunluk bazli gruplama hem de genel kullanim icin temel veri kaynagidir.

sirket_samples = [
    "BIM", "sOK", "A101", "IKEA", "Metro", "Migros", "Real", "Kipa", "Sarar", "Damat", "Koton", "Zara", "Mango", "Puma", "Nike", "Bosch", "Beko", "Arcelik", "Vestel", "Profilo", "Siemens", "Samsung", "LG", "Philips", "Koctas", "Teknosa", "Pegasus", "Akbank", "ETI", "ulker", "Nestle", "Pepsi", "Boyner", "Kigili", "H&M", "Vans", "Adidas", "Reebok", "Network", "Beymen", "Yapi Kredi", "VakifBank", "Halkbank", "ING Bank", "DenizBank", "Unilever", "P&G", "Colin's", "DeFacto", "Bauhaus", "Turkcell", "Vodafone", "Carrefour", "Intersport", "Decathlon", "Is Bankasi", "LC Waikiki", "MediaMarkt", "Converse", "Timberland", "Columbia", "CarrefourSA", "Altinyildiz", "Leroy Merlin", "Ziraat Bankasi", "Turkish Airlines", "Coca Cola", "QNB Finansbank", "The North Face", "Turk Telekom"
]

ad_soyad_samples = [
    "Ali", "Can", "Ahmet", "Zehra", "Mehmet", "Fatma", "Seda Ates", "Gul Akgul", "Cem Balci", "Sibel Tuna", "Burak Kose", "Tolga ozgur", "Murat Isik", "ozlem Oral", "Deniz Tekin", "Burcu cag", "Ayse Kaya", "Emine Tas", "Hatice Uz", "Zeliha Can", "Fadime oz", "Serkan Peker", "Dilek Soylu", "Emre Basak", "Serap Gur", "Ercan Sever", "Melike Karan", "Volkan cam", "sule Nas", "Kadir Sonmez", "Ahmet Kaya", "Hacer Bulut", "Mustafa sahin", "Emine Yildiz", "Ali ozkan", "Ibrahim Dogan", "Zeynep Kilic", "Huseyin Aslan", "Zeliha Polat", "Osman Akin", "Pinar Durak", "Ahmet Yilmaz", "Mehmet Kaya", "Fatma Demir", "Ayse celik", "Hatice Arslan", "Suleyman Yucel", "Hacer Turk", "Meryem ozturk", "Yasar Tunc", "Rukiye Aydin", "Recep ozdemir", "Hanife Basaran", "Yusuf Koc", "Gulay Karaca", "Hasan Ucar", "Nuriye ciftci", "Kemal Duman", "Necla Keskin", "Ramazan Bulut", "Melahat Tas", "Bayram Yavuz", "Saliha Ceylan", "omer Sezer", "Cemile Ergin", "Halil Kurt", "Fatih Uzun", "Mehmet Demir", "Ibrahim ozkan", "Abdullah Gunes", "Abdullah Dogan", "Mustafa Yilmaz", "Suleyman Erdogan"
]

para_samples = [
    "50 TL", "75 TL", "80 TL", "120 TL", "300 TL", "480 TL", "650 TL", "899 TL", "950 TL", "150 EUR", "200 USD", "1.250 TL", "1.500 TL", "1.800 TL", "2.100 TL", "2.350 TL", "2.900 TL", "3.750 TL", "4.500 TL", "5.500 TL", "6.500 TL", "7.250 TL", "8.900 TL", "9.750 TL", "1.200 EUR", "1.500 USD", "2.250 USD", "2.800 EUR", "6.250 TL", "8.500 EUR", "12.750 TL", "15.750 TL", "19.750 TL", "22.500 TL", "25.000 TL", "28.500 TL", "38.000 TL", "45.000 TL", "55.000 TL", "95.000 TL", "10.000 USD", "12.500 EUR", "15.500 USD", "18.000 EUR", "25.000 USD", "65.000 EUR", "75.000 USD", "100.000 TL", "125.000 TL", "140.000 TL", "175.000 TL", "180.000 TL", "220.000 TL", "350.000 TL"
]

adres_samples = [
    "Ist", "Ank", "Bursa", "Izmir", "Adana", "Ankara", "Istanbul", "Antalya", "Denizli", "Eskisehir", "Samsun", "Gaziantep", "Atakum", "Kocasinan", "Konak/Izm", "No:15 Kadikoy", "Cad. cankaya", "Bursa/Mrkz", "Kadikoy/Ist", "cankaya/Ank", "Mah. Inonu Cad", "Zafer Mah. Kordon", "Ataturk Mah. Cad", "Sok. No:23 Bursa", "Barbaros Mah. Ataturk", "Gazi Bulvari No:42", "Fatih Mah. Sinan S.", "Kultur Mah. Hurriyet", "Yildirim Mah. Istiklal", "Guzelyali Mah. sehit C.", "Kocatepe Mah. Mithatp.", "Fevzi Pasa Mah. Gaziler", "Mehmet Akif Mah. can.", "Yenisehir Mah. Cumhur. B.", "Selcuklu Mah. Mevlana Bul.", "Inonu Mah. Ataturk Cad. ", "camlik Mah. Sahil Yolu No:", "Yesilova Mah. Ankara Cad. ", "Karsiyaka Mah. Izmir Yolu N", "Bati Mah. Londra Asfalti No", "Dogu Mah. Bagdat Cad. No:2", "Merkez Mah. Sakarya Cad. No", "Guney Mah. Antalya Bulvari ", "Kuzey Mah. Sivas Yolu No:87", "Anadolu Mah. Trabzon Cad. N", "Rumeli Mah. Edirne Yolu No:", "Orta Mah. Konya Cad. No:54 ", "Ic Mah. Ankara Bulvari No:76", "Dis Mah. Istanbul Yolu No:1", "Alt Mah. Bursa Cad. No:43 Os", "ust Mah. Adana Yolu No:85 S", "on Mah. Mersin Bulvari No:16", "Arka Mah. Gaziantep Cad. No", "Orman Mah. Tabiat Yolu No:18", "Deniz Mah. Sahil Cad. No:7 K", "Dag Mah. Uludag Sok. No:31 O", "Vadi Mah. camlik Cad. No:64 ", "Tepe Mah. Yuksek Sok. No:19 c", "Duz Mah. Ovacik Yolu No:145 ", "Egik Mah. Yamac Cad. No:52 Ka", "Genis Mah. Acik Alan Sok. No:", "Dar Mah. Kisa Yol No:6 Kadiko", "Uzun Mah. Mesafe Cad. No:174 ", "Kisa Mah. Yakin Sok. No:11 Ko", "Buyuk Mah. Genis Bulvari No:2", "Kucuk Mah. Minik Sok. No:4 Be", "Eski Mah. Tarih Cad. No:99 Ulus/Ankara", "Zafer Mah. Kordon Cad. No:8 Konak/Izmir", "Yeni Mah. Modern Bulvari No:156 Bornova/Izmir", "Ataturk Mah. Inonu Cad. No:15 Kadikoy/Istanbul", "Fatih Mah. Mimar Sinan Sok. No:23 Osmangazi/Bursa", "Cumhuriyet Mah. Gazi Bulvari No:42 cankaya/Ankara", "Kultur Mah. Hurriyet Cad. No:12 Seyhan/Adana", "Yildirim Mah. Istiklal Sok. No:5 Merkez/Eskisehir", "Guzelyali Mah. sehit Cad. No:34 Atakum/Samsun", "Barbaros Mah. Ataturk Bulvari No:67 Muratpasa/Antalya", "Kocatepe Mah. Mithatpasa Cad. No:56 Kocasinan/Kayseri", "Mehmet Akif Mah. cankiri Cad. No:89 Altindag/Ankara", "Fevzi Pasa Mah. Gaziler Cad. No:91 sahinbey/Gaziantep", "Yenisehir Mah. Cumhuriyet Bulvari No:78 Pamukkale/Denizli", "Selcuklu Mah. Mevlana Bulvari No:25 Selcuklu/Konya", "Inonu Mah. Ataturk Cad. No:47 Tepebasi/Eskisehir", "camlik Mah. Sahil Yolu No:13 Bodrum/Mugla", "Yesilova Mah. Ankara Cad. No:62 Osmangazi/Bursa", "Karsiyaka Mah. Izmir Yolu No:38 Torbali/Izmir", "Bati Mah. Londra Asfalti No:155 Esenyurt/Istanbul", "Dogu Mah. Bagdat Cad. No:244 Maltepe/Istanbul", "Merkez Mah. Sakarya Cad. No:71 Adapazari/Sakarya", "Guney Mah. Antalya Bulvari No:103 Kepez/Antalya", "Kuzey Mah. Sivas Yolu No:87 Melikgazi/Kayseri", "Anadolu Mah. Trabzon Cad. No:29 Atakum/Samsun", "Rumeli Mah. Edirne Yolu No:126 Arnavutkoy/Istanbul", "Orta Mah. Konya Cad. No:54 Selcuklu/Konya", "Ic Mah. Ankara Bulvari No:76 cankaya/Ankara", "Dis Mah. Istanbul Yolu No:198 Nilufer/Bursa", "Alt Mah. Bursa Cad. No:43 Osmangazi/Bursa", "ust Mah. Adana Yolu No:85 Seyhan/Adana", "on Mah. Mersin Bulvari No:167 Mezitli/Mersin", "Arka Mah. Gaziantep Cad. No:92 sehitkamil/Gaziantep", "Orman Mah. Tabiat Yolu No:18 Beykoz/Istanbul", "Deniz Mah. Sahil Cad. No:7 Kartal/Istanbul", "Dag Mah. Uludag Sok. No:31 Osmangazi/Bursa", "Vadi Mah. camlik Cad. No:64 Bornova/Izmir", "Tepe Mah. Yuksek Sok. No:19 cankaya/Ankara", "Duz Mah. Ovacik Yolu No:145 Tuzla/Istanbul", "Egik Mah. Yamac Cad. No:52 Karsiyaka/Izmir", "Genis Mah. Acik Alan Sok. No:28 Nilufer/Bursa", "Dar Mah. Kisa Yol No:6 Kadikoy/Istanbul", "Uzun Mah. Mesafe Cad. No:174 cankaya/Ankara", "Kisa Mah. Yakin Sok. No:11 Konak/Izmir", "Buyuk Mah. Genis Bulvari No:233 Osmangazi/Bursa", "Kucuk Mah. Minik Sok. No:4 Beyoglu/Istanbul", "Guzel Mah. Hos Sok. No:37 Nilufer/Bursa", "cirkin Mah. Kotu Yol No:83 Pendik/Istanbul", "Temiz Mah. Pak Cad. No:21 Kecioren/Ankara", "Kirli Mah. Pis Sok. No:77 Kartal/Istanbul", "Sessiz Mah. Sakin Yolu No:14 cankaya/Ankara", "Gurultulu Mah. samata Cad. No:118 Kadikoy/Istanbul", "Aydinlik Mah. Isik Bulvari No:65 Konak/Izmir", "Karanlik Mah. Golge Sok. No:39 Besiktas/Istanbul"
]

telefon_samples = [
    "05321234567", "05421234568", "05331234569", "05531234570", "05341234571", "05441234572", "05351234573", "05451234574", "05361234575", "05461234576", "05371234577", "05471234578", "05381234579", "05481234580", "05391234581", "05491234582", "05321111111", "05322222222", "05333333333", "05444444444", "05355555555", "05466666666", "05377777777", "05488888888", "05339999999", "05320000000", "05429876543", "05338765432", "05547654321", "05346543210", "05455432109", "05364321098", "05375210987", "05486109876", "05397098765", "05498987654", "05321357924", "05422468135", "05333691470", "05544702581", "05355813692", "05466924703", "05377035814", "05488146925", "05399258036", "05320369147", "05429470258", "05338581369", "05547692470", "05346703581", "05455814692", "05364925703", "05376036814", "05487147925", "05398259036", "05499360147"
]

tarih_samples = [
    "03.03.2023", "04.09.2023", "05.02.2023", "07.10.2022", "08.12.2022", "09.05.2023", "10.01.2024", "11.06.2023", "12.06.2022", "13.08.2023", "14.07.2024", "15.03.2024", "15.05.2023", "16.11.2022", "17.01.2024", "18.12.2023", "19.04.2024", "20.03.2022", "21.09.2022", "22.07.2023", "23.08.2024", "24.07.2023", "25.04.2024", "26.11.2022", "27.09.2022", "28.10.2023", "29.02.2024", "30.01.2024", "31.05.2024", "01.10.2022", "02.11.2024", "03.10.2022", "04.11.2023", "06.12.2022", "08.08.2023", "09.01.2024", "10.08.2022", "13.04.2024", "14.09.2022", "16.04.2024", "17.05.2022", "18.06.2023", "21.06.2023", "22.03.2024", "25.12.2023", "26.02.2024", "28.12.2023", "32.07.2023", "4 Eylul 2023", "8 Aralik 2022", "15 Mart 2024", "17 Ocak 2024", "22 Temmuz 2023", "31 Mayis 2024"
]

email_samples = [
    "ayse@outlook.com", "seda.ates@yahoo.com", "ahmet@gmail.com", "burak@outlook.com", "deniz.tekin@outlook.com", "serkan@hotmail.com", "emre@outlook.com", "tolga@hotmail.com", "ozlem@gmail.com", "sibel@yahoo.com", "volkan@hotmail.com", "burcu@gmail.com", "fatma.demir@yahoo.com", "zeynep@hotmail.com", "fadime@hotmail.com", "gulay@hotmail.com", "necla@hotmail.com", "melahat@outlook.com", "cemile@outlook.com", "serap.gur@gmail.com", "pinar.durak@yahoo.com", "cem.balci@hotmail.com", "sule.nas@yahoo.com", "mehmet.kaya@hotmail.com", "ali.ozkan@yahoo.com", "hatice@gmail.com", "hacer.turk@yahoo.com", "meryem@gmail.com", "yasar@gmail.com", "hanife@outlook.com", "nuriye@outlook.com", "ramazan@yahoo.com", "saliha@hotmail.com", "dilek.soylu@yahoo.com", "murat.isik@outlook.com", "ercan.sever@outlook.com", "melike.karan@gmail.com", "mustafa123@gmail.com", "emine.yildiz@hotmail.com", "ibrahim.dogan@outlook.com", "huseyin.aslan@gmail.com", "zeliha@yahoo.com", "osman.akin@outlook.com", "suleyman@gmail.com", "abdullah@outlook.com", "rukiye.aydin@hotmail.com", "recep.ozdemir@yahoo.com", "yusuf.koc@gmail.com", "hasan.ucar@yahoo.com", "kemal.duman@gmail.com", "bayram.yavuz@gmail.com", "omer.sezer@yahoo.com", "halil.kurt@gmail.com", "fatih.uzun@hotmail.com", "gul.akgul@gmail.com"
]

iban_samples = [
    "TR330006100519786457841326", "TR640004600119786543210987", "TR750001500658742039485760", "TR860010005018765432109876", "TR970006200119874563201234", "TR180009900658741250963847", "TR290001200519632540789513", "TR400010100119753951486270", "TR510006400658987654321098", "TR620004800519874563201357", "TR730001700119654783921046", "TR840009800658741852963047", "TR950006300519987654321579", "TR060010200119753846291570", "TR170001600658852741963048", "TR280009700519741963085274", "TR390006500119863529471604", "TR500004900658741963852074", "TR610001800519654387291046", "TR720010300119741852963074", "TR830006600658987321456078", "TR940009600519852741963047", "TR050001900119654789321046", "TR160010400658741963852074", "TR270006700519987654123578", "TR380004700119852963741046", "TR490002000658741963852074", "TR600009500519654789321046", "TR710006800119852741963074", "TR820010500658987654321078", "TR930001100519741963852074", "TR040009400119654789321046", "TR150006900658852741963074", "TR260002100519987321456078", "TR370004600119741963852074", "TR480010600658654789321046", "TR590009300519852741963074", "TR700007000119987654321078", "TR810001300658741963852074", "TR920009200519654789321046", "TR030010700119852741963074", "TR140007100658987321456078", "TR250002200519741963852074", "TR360004500119654789321046", "TR470009100658852741963074", "TR580007200119987321456078", "TR690010800519741963852074", "TR800001400658654789321046", "TR910009000119852741963074", "TR020007300658987321456078", "TR130002300519741963852074"
]

# --- 2. UZUNLUK BAZLI LISTELER (DOgRU FORMATTA VE DOgRU UZUNLUKLARLA) ---
# Bu listeler, kodunuzun beklentisine uygun olarak "sozluk listesi" formatindadir.

sirket_len_samples = [
    {
        "length": 3,
        "samples": [
            "BIM",
            "SOK",
            "ETI",
            "LG",
            "P&G"
        ]
    },
    {
        "length": 4,
        "samples": [
            "A101",
            "IKEA",
            "Real",
            "Kipa",
            "Zara",
            "Puma",
            "Nike",
            "Beko",
            "Vans",
            "LCW"
        ]
    },
    {
        "length": 5,
        "samples": [
            "Metro",
            "Sarar",
            "Damat",
            "Koton",
            "Mango",
            "Bosch",
            "Ulker",
            "Pepsi",
            "Tofas",
            "Vestel"
        ]
    },
    {
        "length": 6,
        "samples": [
            "Migros",
            "Kigili",
            "H&M",
            "Adidas",
            "Reebok",
            "Nestle",
            "Arcelik",
            "Boyner",
            "Teknosa",
            "Koctas"
        ]
    },
    {
        "length": 7,
        "samples": [
            "Pegasus",
            "Akbank",
            "Network",
            "Beymen",
            "Profilo",
            "Siemens",
            "Samsung",
            "Philips",
            "Unilever",
            "Vatan"
        ]
    },
    {
        "length": 8,
        "samples": [
            "Turkcell",
            "Vodafone",
            "Colin's",
            "DeFacto",
            "Bauhaus",
            "VakifBank",
            "Halkbank",
            "ING Bank",
            "FibaBanka",
            "Eczacibasi"
        ]
    },
    {
        "length": 9,
        "samples": [
            "Carrefour",
            "DenizBank",
            "Yapi Kredi",
            "Sisecam",
            "Tupras A.S."
        ]
    },
    {
        "length": 10,
        "samples": [
            "Is Bankasi",
            "LC Waikiki",
            "MediaMarkt",
            "Converse",
            "Coca Cola",
            "Brisa Brid."
        ]
    },
    {
        "length": 11,
        "samples": [
            "CarrefourSA",
            "Altinyildiz",
            "Timberland",
            "Ziraat Bankasi",
            "Ata Holding"
        ]
    },
    {
        "length": 12,
        "samples": [
            "Intersport",
            "Decathlon",
            "Turk Telekom",
            "AnadoluJet"
        ]
    },
    {
        "length": 13,
        "samples": [
            "Leroy Merlin",
            "QNB Finansbank",
            "Yemeksepeti",
            "Kredi Garanti"
        ]
    },
    {
        "length": 14,
        "samples": [
            "Turkish Airlines",
            "Gunes Sigorta"
        ]
    },
    {
        "length": 15,
        "samples": [
            "The North Face",
            "Mavi Jeans A.S.",
            "Petrol Ofisi AS"
        ]
    },
    {
        "length": 16,
        "samples": [
            "Opet Petrolculuk",
            "Migros Ticaret AS"
        ]
    },
    {
        "length": 17,
        "samples": [
            "Inci Holding A.S.",
            "Koctas Yapi A.S."
        ]
    },
    {
        "length": 18,
        "samples": [
            "Petrol Ofisi A.S.",
            "BIM Birlesik A.S."
        ]
    },
    {
        "length": 19,
        "samples": [
            "Turkiye Is Bankasi",
            "Turkiye Finans"
        ]
    },
    {
        "length": 20,
        "samples": [
            "Ford Otomotiv Sanayi",
            "Anadolu Hayat Emek."
        ]
    },
    {
        "length": 21,
        "samples": [
            "Sabanci Holding A.S.",
            "Vakifbank Genel Mud."
        ]
    },
    {
        "length": 22,
        "samples": [
            "Turkiye Is Bankasi A.S.",
            "Halkbank Genel Mudurluk"
        ]
    },
    {
        "length": 23,
        "samples": [
            "Akbank Genel Mudurlugu",
            "Yapi Kredi Genel Mud."
        ]
    },
    {
        "length": 24,
        "samples": [
            "Eczacibasi Yatirim Holding",
            "Garanti Bankasi A.S."
        ]
    },
    {
        "length": 25,
        "samples": [
            "Turk Hava Yollari A.O.",
            "Turkiye Sinai Kalkinma Bankasi"
        ]
    },
    {
        "length": 26,
        "samples": [
            "Turkiye Garanti Bankasi",
            "VakifBank International"
        ]
    },
    {
        "length": 27,
        "samples": [
            "Dogus Holding A.S.",
            "Koc Holding Anonim Sirketi"
        ]
    },
    {
        "length": 28,
        "samples": [
            "Koc Holding A.S.",
            "Izmir Enternasyonel Fuari"
        ]
    },
    {
        "length": 29,
        "samples": [
            "Turkiye Petrolleri Anonim Ortakligi",
            "Dogus Otomotiv Ticaret A.S."
        ]
    },
    {
        "length": 30,
        "samples": [
            "Akbank Genel Mudurluk",
            "Coca-Cola Icecek A.S."
        ]
    },
    {
        "length": 31,
        "samples": [
            "Anadolu Grubu Holding A.S.",
            "Otokar Otomotiv Sanayi A.S."
        ]
    },
    {
        "length": 32,
        "samples": [
            "Turk Telekomunikasyon A.S.",
            "T.C. Ziraat Bankasi A.S."
        ]
    },
    {
        "length": 33,
        "samples": [
            "Ziraat Katilim Bankasi A.S.",
            "Dogan Holding Anonim Sirketi"
        ]
    },
    {
        "length": 34,
        "samples": [
            "Yapi ve Kredi Bankasi A.S.",
            "T.C. Halk Bankasi A.S."
        ]
    },
    {
        "length": 35,
        "samples": [
            "Eczacibasi Holding A.S.",
            "Ford Otosan Otomotiv A.S."
        ]
    },
    {
        "length": 36,
        "samples": [
            "Turkiye Vakiflar Bankasi T.A.O.",
            "Denizbank Anonim Sirketi"
        ]
    },
    {
        "length": 37,
        "samples": [
            "Haci Sakir Sanayi ve Ticaret A.S.",
            "Anadolu Sigorta Anonim Sirketi"
        ]
    },
    {
        "length": 38,
        "samples": [
            "Anadolu Efes Biracilik ve Malt Sanayii A.S.",
            "Borusan Holding Anonim Sirketi"
        ]
    },
    {
        "length": 39,
        "samples": [
            "Otokar Otomotiv ve Savunma Sanayi A.S.",
            "MediaMarkt Elektronik A.S."
        ]
    },
    {
        "length": 40,
        "samples": [
            "Turkiye Emlak Katilim Bankasi A.S.",
            "Pegasus Hava Tasimaciligi A.S."
        ]
    },
    {
        "length": 41,
        "samples": [
            "T.C. Ziraat Bankasi A.S. Genel Mudurlugu",
            "Mudo Konsept Magazacilik A.S."
        ]
    },
    {
        "length": 42,
        "samples": [
            "T.C. Ziraat Bankasi A.S.",
            "Vestel Elektronik Sanayi ve Ticaret A.S."
        ]
    },
    {
        "length": 43,
        "samples": [
            "Havaalanlari ve Yer Hizmetleri A.S.",
            "Sabanci Holding Anonim Sirketi"
        ]
    },
    {
        "length": 44,
        "samples": [
            "Turk Telekomunikasyon A.S. Genel Mudurlugu",
            "CarrefourSA Carrefour Sabanci Ticaret Merkezi A.S."
        ]
    },
    {
        "length": 45,
        "samples": [
            "Turkiye Garanti Bankasi A.S.",
            "Teknosa Ic ve Dis Ticaret A.S."
        ]
    },
    {
        "length": 46,
        "samples": [
            "Petrol Ofisi A.S. Genel Mudurlugu",
            "Opet Petrolculuk Anonim Sirketi"
        ]
    },
    {
        "length": 47,
        "samples": [
            "Turk Petrol Anonim Sirketi",
            "Siemens Sanayi ve Ticaret A.S."
        ]
    },
    {
        "length": 48,
        "samples": [
            "T.C. Vakiflar Bankasi T.A.O. Genel Mudurlugu",
            "Koc Holding Anonim Sirketi Genel Mudurlugu"
        ]
    },
    {
        "length": 49,
        "samples": [
            "Dogus Otomotiv Servis ve Ticaret A.S.",
            "Philips Ticaret A.S. Genel Mudurlugu"
        ]
    },
    {
        "length": 50,
        "samples": [
            "Turkiye Cumhuriyeti Merkez Bankasi",
            "Ziraat Bankasi Anonim Sirketi Genel Mudurlugu"
        ]
    }
] 

ad_soyad_len_samples = [
    {
        "length": 3,
        "samples": [
            "Ali",
            "Can",
            "Cem",
            "Ece",
            "Efe"
        ]
    },
    {
        "length": 4,
        "samples": [
            "Ahmet",
            "Zehra",
            "Fuat",
            "Okan",
            "Zeynep"
        ]
    },
    {
        "length": 5,
        "samples": [
            "Mehmet",
            "Fatma",
            "Berna",
            "Deniz",
            "Hakan"
        ]
    },
    {
        "length": 6,
        "samples": [
            "Emine Tas",
            "Hatice Uz",
            "Dilek Sen",
            "Seda Can"
        ]
    },
    {
        "length": 7,
        "samples": [
            "Zeliha Can",
            "Fadime Oz",
            "Burak Tas",
            "Tolga Aydin"
        ]
    },
    {
        "length": 8,
        "samples": [
            "Seda Ates",
            "Gul Akgul",
            "Cem Balci",
            "Sibel Tuna",
            "Emre Sonmez"
        ]
    },
    {
        "length": 9,
        "samples": [
            "Ayse Kaya",
            "Burak Kose",
            "Tolga Ozgur",
            "Murat Isik",
            "Ozlem Oral"
        ]
    },
    {
        "length": 10,
        "samples": [
            "Ahmet Kaya",
            "Deniz Tekin",
            "Burcu Cag",
            "Serkan Peker",
            "Dilek Soylu"
        ]
    },
    {
        "length": 11,
        "samples": [
            "Hacer Bulut",
            "Ercan Sever",
            "Melike Karan",
            "Volkan Cam",
            "Sule Nas",
            "Kadir Sonmez"
        ]
    },
    {
        "length": 12,
        "samples": [
            "Ahmet Yilmaz",
            "Mehmet Kaya",
            "Fatma Demir",
            "Ayse Celik",
            "Pinar Durak",
            "Halil Durmus"
        ]
    },
    {
        "length": 13,
        "samples": [
            "Mustafa Sahin",
            "Emine Yildiz",
            "Ali Ozkan",
            "Ibrahim Dogan",
            "Zeynep Kilic",
            "Huseyin Aslan"
        ]
    },
    {
        "length": 14,
        "samples": [
            "Hatice Arslan",
            "Suleyman Yucel",
            "Hacer Turk",
            "Meryem Ozturk",
            "Yasar Tunc",
            "Rukiye Aydin"
        ]
    },
    {
        "length": 15,
        "samples": [
            "Mehmet Demir",
            "Ibrahim Ozkan",
            "Abdullah Gunes",
            "Abdullah Dogan"
        ]
    },
    {
        "length": 16,
        "samples": [
            "Mustafa Yilmaz",
            "Suleyman Erdogan",
            "Recep Ozdemir",
            "Hanife Basaran"
        ]
    },
    {
        "length": 17,
        "samples": [
            "Ramazan Bulut",
            "Melahat Tas",
            "Bayram Yavuz",
            "Saliha Ceylan"
        ]
    },
    {
        "length": 18,
        "samples": [
            "Omer Sezer",
            "Cemile Ergin",
            "Halil Kurt",
            "Fatih Uzun"
        ]
    },
    {
        "length": 19,
        "samples": [
            "Kemal Duman",
            "Necla Keskin",
            "Hasan Ucar",
            "Nuriye Ciftci"
        ]
    },
    {
        "length": 20,
        "samples": [
            "Ayse Fatma Kaya",
            "Ali Riza Yildirim"
        ]
    },
    {
        "length": 21,
        "samples": [
            "Mehmet Emin Ozturk",
            "Deniz Su Gokdemir"
        ]
    },
    {
        "length": 22,
        "samples": [
            "Huseyin Can Aslan",
            "Zeynep Naz Polat"
        ]
    },
    {
        "length": 23,
        "samples": [
            "Mustafa Kemal Aydin",
            "Ahmet Kerem Dogan"
        ]
    },
    {
        "length": 24,
        "samples": [
            "Serap Gunes Yilmaz",
            "Suleyman Taner Erdogan"
        ]
    },
    {
        "length": 25,
        "samples": [
            "Ayse Nazli Gungor Demir",
            "Emre Can Atalay Sonmez"
        ]
    }
]
adres_len_samples =[
    {
        "length": 3,
        "samples": [
            "Ist",
            "Ank",
            "Bursa",
            "Izm"
        ]
    },
    {
        "length": 5,
        "samples": [
            "Bursa",
            "Izmir",
            "Adana",
            "Konya"
        ]
    },
    {
        "length": 6,
        "samples": [
            "Ankara",
            "Mersin",
            "Samsun"
        ]
    },
    {
        "length": 7,
        "samples": [
            "Antalya",
            "Denizli",
            "Gaziantep"
        ]
    },
    {
        "length": 8,
        "samples": [
            "Istanbul",
            "Eskisehir",
            "Kocasinan"
        ]
    },
    {
        "length": 9,
        "samples": [
            "Gaziantep",
            "Atakum",
            "Konak/Izm"
        ]
    },
    {
        "length": 10,
        "samples": [
            "Kocasinan",
            "Bursa/Mrkz",
            "Konak/Izmir"
        ]
    },
    {
        "length": 11,
        "samples": [
            "cankaya/Ank",
            "Kadikoy/Ist",
            "Nilufer/Bursa"
        ]
    },
    {
        "length": 12,
        "samples": [
            "No:15 Kadikoy",
            "Cad. Cankaya",
            "Sokak No:1"
        ]
    },
    {
        "length": 13,
        "samples": [
            "Mah. Inonu Cad",
            "Yol No: 12 Camlik"
        ]
    },
    {
        "length": 14,
        "samples": [
            "Zafer Mah. Kordon",
            "Ataturk Mah. Cad",
            "Istiklal Cad."
        ]
    },
    {
        "length": 15,
        "samples": [
            "Sok. No:23 Bursa",
            "Gazi Bulvari No:42"
        ]
    },
    {
        "length": 16,
        "samples": [
            "Fatih Mah. Sinan S.",
            "Kultur Mah. Hurriyet"
        ]
    },
    {
        "length": 17,
        "samples": [
            "Yildirim Mah. Istiklal",
            "Fevzi Pasa Mah. Gaziler"
        ]
    },
    {
        "length": 18,
        "samples": [
            "Gazi Bulvari No:42",
            "Yildirim Mah. Istiklal"
        ]
    },
    {
        "length": 19,
        "samples": [
            "Yildirim Mah. Istiklal",
            "Mehmet Akif Mah. Can."
        ]
    },
    {
        "length": 20,
        "samples": [
            "Barbaros Mah. Ataturk",
            "Guzelyali Mah. Sehit C."
        ]
    },
    {
        "length": 21,
        "samples": [
            "Guzelyali Mah. Sehit C.",
            "Kocatepe Mah. Mithatp."
        ]
    },
    {
        "length": 22,
        "samples": [
            "Fevzi Pasa Mah. Gaziler",
            "Mehmet Akif Mah. Can."
        ]
    },
    {
        "length": 23,
        "samples": [
            "Yenisehir Mah. Cumhur. B.",
            "Selcuklu Mah. Mevlana Bul."
        ]
    },
    {
        "length": 24,
        "samples": [
            "Inonu Mah. Ataturk Cad. ",
            "Camlik Mah. Sahil Yolu No:"
        ]
    },
    {
        "length": 25,
        "samples": [
            "Yesilova Mah. Ankara Cad. ",
            "Bati Mah. Londra Asfalti No"
        ]
    },
    {
        "length": 26,
        "samples": [
            "Karsiyaka Mah. Izmir Yolu N",
            "Dogu Mah. Bagdat Cad. No:2"
        ]
    },
    {
        "length": 27,
        "samples": [
            "Merkez Mah. Sakarya Cad. No",
            "Guney Mah. Antalya Bulvari "
        ]
    },
    {
        "length": 28,
        "samples": [
            "Kuzey Mah. Sivas Yolu No:87",
            "Anadolu Mah. Trabzon Cad. N"
        ]
    },
    {
        "length": 29,
        "samples": [
            "Rumeli Mah. Edirne Yolu No:",
            "Orta Mah. Konya Cad. No:54 "
        ]
    },
    {
        "length": 30,
        "samples": [
            "Ic Mah. Ankara Bulvari No:76",
            "Dis Mah. Istanbul Yolu No:1"
        ]
    },
    {
        "length": 31,
        "samples": [
            "Alt Mah. Bursa Cad. No:43 Os",
            "Ust Mah. Adana Yolu No:85 S"
        ]
    },
    {
        "length": 32,
        "samples": [
            "On Mah. Mersin Bulvari No:16",
            "Arka Mah. Gaziantep Cad. No"
        ]
    },
    {
        "length": 33,
        "samples": [
            "Orman Mah. Tabiat Yolu No:18",
            "Deniz Mah. Sahil Cad. No:7 K"
        ]
    },
    {
        "length": 34,
        "samples": [
            "Dag Mah. Uludag Sok. No:31 O",
            "Vadi Mah. Camlik Cad. No:64 "
        ]
    },
    {
        "length": 35,
        "samples": [
            "Tepe Mah. Yuksek Sok. No:19 c",
            "Duz Mah. Ovacik Yolu No:145 "
        ]
    },
    {
        "length": 36,
        "samples": [
            "Egik Mah. Yamac Cad. No:52 Ka",
            "Genis Mah. Acik Alan Sok. No:"
        ]
    },
    {
        "length": 37,
        "samples": [
            "Dar Mah. Kisa Yol No:6 Kadiko",
            "Uzun Mah. Mesafe Cad. No:174 "
        ]
    },
    {
        "length": 38,
        "samples": [
            "Kisa Mah. Yakin Sok. No:11 Ko",
            "Buyuk Mah. Genis Bulvari No:2"
        ]
    },
    {
        "length": 39,
        "samples": [
            "Kucuk Mah. Minik Sok. No:4 Be",
            "Eski Mah. Tarih Cad. No:99 Ulus/Ankara"
        ]
    },
    {
        "length": 40,
        "samples": [
            "Guzelyali Mah. Hos Sok. No:37 Nilufer/Bursa",
            "Cumhuriyet Mah. Ozgurluk Cad. No:24/1 Bornova/Izmir"
        ]
    },
    {
        "length": 41,
        "samples": [
            "Zafer Mah. Kordon Cad. No:8 Konak/Izmir",
            "Sehitler Mah. Istiklal Cad. No:11 Esenyurt/Istanbul"
        ]
    },
    {
        "length": 42,
        "samples": [
            "Kultur Mah. Hurriyet Cad. No:12 Seyhan/Adana",
            "Yildirim Mah. Istiklal Sok. No:5 Merkez/Eskisehir"
        ]
    },
    {
        "length": 43,
        "samples": [
            "Hurriyet Mah. Kilicarslan Cad. No:14 Kecioren/Ankara",
            "Barbaros Mah. Ataturk Bulvari No:67 Muratpasa/Antalya"
        ]
    },
    {
        "length": 44,
        "samples": [
            "Yeni Mah. Modern Bulvari No:156 Bornova/Izmir",
            "Ataturk Mah. Ikinci Inonu Cad. No:23/5 Kadikoy/Istanbul"
        ]
    },
    {
        "length": 45,
        "samples": [
            "Kocatepe Mah. Mithatpasa Cad. No:56 Kocasinan/Kayseri",
            "Mehmet Akif Ersoy Mah. Cankiri Cad. No:89 Altindag/Ankara"
        ]
    },
    {
        "length": 46,
        "samples": [
            "Ataturk Mah. Inonu Cad. No:15 Kadikoy/Istanbul",
            "Guzelyali Mah. Sehit Cad. No:34 Atakum/Samsun"
        ]
    },
    {
        "length": 47,
        "samples": [
            "Yildirim Mah. Istiklal Sok. No:5 Merkez/Eskisehir",
            "Cumhuriyet Mah. Gazi Bulvari No:42 Cankaya/Ankara"
        ]
    },
    {
        "length": 48,
        "samples": [
            "Fatih Mah. Mimar Sinan Sok. No:23 Osmangazi/Bursa",
            "Yenimahalle Mah. Cumhuriyet Bulvari No:78 Pamukkale/Denizli"
        ]
    },
    {
        "length": 49,
        "samples": [
            "Fevzi Pasa Mah. Gaziler Cad. No:91 Sahinbey/Gaziantep",
            "Selcuklu Mah. Mevlana Bulvari No:25 Selcuklu/Konya"
        ]
    },
    {
        "length": 50,
        "samples": [
            "Inonu Mah. Ataturk Cad. No:47 Tepebasi/Eskisehir",
            "Camlik Mah. Sahil Yolu No:13 Bodrum/Mugla"
        ]
    }
]