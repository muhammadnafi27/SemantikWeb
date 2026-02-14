"""
Seed Data for Jakarta Tourist Destinations
12 destinations with comprehensive descriptions, history, and metadata
"""

DESTINATIONS_SEED = [
    {
        "slug": "ancol-dreamland",
        "name": "Ancol Dreamland",
        "region": "Jakarta Utara",
        "region_id": "mg:JakartaUtara",
        "lat": -6.1249,
        "lon": 106.8456,
        "image_url": "https://www.goersapp.com/blog/wp-content/uploads/2024/07/cover-andoldreamleand_.jpg",
        "year_established": 1966,
        "location": "Jl. Lodan Timur No.7, Ancol, Pademangan, Jakarta Utara",
        "category": "Recreation",
        "long_description": """Ancol Dreamland adalah kawasan rekreasi terpadu di tepi pantai yang dirancang sebagai destinasi hiburan keluarga, wisata air, dan pusat event. Di dalamnya terdapat beragam atraksi—mulai dari taman bermain, area pantai, ruang terbuka, hingga fasilitas komersial dan hiburan. Kawasan ini sering dijadikan tempat berlibur singkat karena aksesnya relatif mudah dari pusat kota, serta menawarkan pengalaman 'waterfront' yang jarang ditemukan di area urban Jakarta.

Bagi wisatawan, Ancol menarik karena fleksibel: kamu bisa memilih aktivitas santai seperti berjalan di area pantai dan menikmati pemandangan, atau memilih aktivitas berbayar di wahana tertentu. Dari perspektif mobilitas, Ancol juga relevan karena pengunjung bisa datang dengan kombinasi transportasi umum dan jalan kaki (last-mile).""",
        "long_history": """Perkembangan Ancol sebagai kawasan wisata modern berawal dari upaya memperluas ruang rekreasi kota dan memanfaatkan kawasan pesisir sebagai pusat hiburan publik. Seiring waktu, Ancol berkembang menjadi ekosistem wisata dengan beberapa zona dan atraksi yang terus diperbarui mengikuti kebutuhan pengunjung, baik untuk liburan keluarga, acara komunitas, maupun event skala besar. Hal ini membuat Ancol menjadi salah satu ikon wisata di Jakarta Utara.

Pembangunan Ancol dimulai pada era 1960-an sebagai bagian dari program pengembangan kawasan utara Jakarta. Sejak saat itu, berbagai wahana dan fasilitas terus ditambahkan, termasuk Dunia Fantasi (Dufan), Sea World, Atlantis Water Adventure, dan berbagai hotel serta restoran.""",
        "important_details": [
            "Jam operasional: 06:00 - 18:00 (area umum)",
            "Tiket masuk kawasan: Rp 25.000 (weekday) / Rp 35.000 (weekend)",
            "Wahana terpisah: Dufan, Sea World, Atlantis",
            "Fasilitas: Pantai, hotel, restoran, lapangan golf"
        ]
    },
    {
        "slug": "kota-tua-jakarta",
        "name": "Kota Tua Jakarta",
        "region": "Jakarta Barat",
        "region_id": "mg:JakartaBarat",
        "lat": -6.1352,
        "lon": 106.8133,
        "image_url": "https://blog-images.reddoorz.com/uploads/image/file/10117/kota-tua.jpg",
        "year_established": 1619,
        "location": "Jl. Taman Fatahillah, Pinangsia, Taman Sari, Jakarta Barat",
        "category": "Historical",
        "long_description": """Kota Tua Jakarta merupakan kawasan wisata sejarah yang menampilkan jejak perkembangan Jakarta pada masa kolonial. Area ini dikenal sebagai ruang publik yang kaya bangunan berarsitektur lama, museum, serta plaza yang sering menjadi titik temu wisatawan, komunitas seni, dan kegiatan budaya. Suasananya unik karena memadukan unsur edukasi—melalui museum dan tur sejarah—dengan aktivitas rekreasi seperti berjalan kaki menikmati sudut-sudut kota lama, berfoto, atau mengikuti pertunjukan jalanan.

Dalam konteks mobilitas, Kota Tua biasanya menjadi destinasi yang cocok dijangkau dengan kombinasi transportasi umum dan jalan kaki, karena area intinya nyaman dijelajahi dengan berjalan. Pengalaman wisata juga cenderung 'walkable'—pengunjung berpindah dari museum ke museum atau dari plaza ke titik kuliner di sekitarnya.""",
        "long_history": """Kota Tua berakar dari fase awal perkembangan kota pelabuhan yang kemudian menjadi pusat administrasi dan perdagangan. Berbagai bangunan di area ini merepresentasikan perubahan fungsi kota dari masa ke masa. Karena nilai sejarahnya, kawasan ini dijaga sebagai kawasan cagar budaya dan sering direvitalisasi untuk meningkatkan kenyamanan wisatawan, tanpa menghilangkan karakter sejarahnya.

Pada masa VOC (1619-1799), kawasan ini dikenal sebagai Batavia dan menjadi pusat perdagangan rempah-rempah. Banyak bangunan bersejarah yang masih berdiri hingga kini, termasuk Museum Fatahillah (bekas Balai Kota Batavia), Museum Bank Indonesia, dan Cafe Batavia.""",
        "important_details": [
            "Jam operasional: 24 jam (area terbuka), museum 09:00-15:00",
            "Tiket masuk kawasan: Gratis",
            "Museum Fatahillah: Rp 5.000",
            "Aktivitas: Foto, sepeda ontel, pertunjukan jalanan"
        ]
    },
    {
        "slug": "taman-mini-indonesia-indah",
        "name": "Taman Mini Indonesia Indah",
        "region": "Jakarta Timur",
        "region_id": "mg:JakartaTimur",
        "lat": -6.3024,
        "lon": 106.8951,
        "image_url": "https://images.unsplash.com/photo-1596402184320-417e7178b2cd?w=800",
        "year_established": 1975,
        "location": "Jl. Taman Mini Indonesia Indah, Ceger, Cipayung, Jakarta Timur",
        "category": "Cultural",
        "long_description": """TMII adalah taman budaya dan rekreasi yang menampilkan keragaman Indonesia dalam satu kawasan. Di sini, pengunjung dapat melihat representasi budaya dari berbagai provinsi melalui paviliun, koleksi museum, dan instalasi edukatif. TMII cocok untuk wisata keluarga karena menawarkan kegiatan yang menggabungkan edukasi dan rekreasi—mulai dari menjelajah museum, menyaksikan pertunjukan budaya, hingga menikmati ruang hijau dan area berjalan.

Dari sisi mobilitas, TMII biasanya memerlukan perencanaan rute yang baik karena lokasinya berada di Jakarta Timur dan area di dalamnya cukup luas. Karena itu, integrasi transportasi umum terdekat + last-mile (jalan kaki atau perpindahan jarak dekat) menjadi penting untuk pengalaman yang nyaman.""",
        "long_history": """TMII dibangun sebagai proyek yang bertujuan memperkenalkan kekayaan budaya Indonesia dalam format yang mudah diakses masyarakat. Seiring waktu, fasilitasnya berkembang, museum bertambah, serta area-area tematik diperbarui. Hal ini membuat TMII menjadi destinasi yang bukan hanya rekreasi, tetapi juga sarana edukasi budaya yang relevan lintas generasi.

Diresmikan pada 20 April 1975 oleh Presiden Soeharto, TMII menampilkan 33 anjungan provinsi dengan rumah adat tradisional. Kawasan seluas 150 hektar ini juga memiliki danau buatan berbentuk kepulauan Indonesia, kereta gantung, dan berbagai museum tematik.""",
        "important_details": [
            "Jam operasional: 07:00 - 22:00",
            "Tiket masuk: Rp 20.000",
            "Luas area: 150 hektar",
            "Fasilitas: Kereta gantung, museum, teater IMAX"
        ]
    },
    {
        "slug": "monumen-nasional",
        "name": "Monumen Nasional (Monas)",
        "region": "Jakarta Pusat",
        "region_id": "mg:JakartaPusat",
        "lat": -6.1754,
        "lon": 106.8272,
        "image_url": "https://images.unsplash.com/photo-1555333145-4acf190da740?w=800",
        "year_established": 1961,
        "location": "Jl. Medan Merdeka, Gambir, Jakarta Pusat",
        "category": "Historical",
        "long_description": """Monas adalah landmark utama Jakarta yang berada di kawasan pusat kota. Selain menjadi simbol nasional, area sekitarnya juga berfungsi sebagai ruang publik yang ramai untuk aktivitas warga: berjalan santai, olahraga, atau menghadiri acara tertentu. Bagi wisatawan, Monas menarik karena memberikan pengalaman 'pusat Jakarta'—dekat dengan banyak titik penting lain, dan sering dijadikan patokan navigasi karena lokasinya strategis.

Monas juga cocok untuk rute wisata 'multi-destinasi' karena bisa dikombinasikan dengan museum, pusat kuliner, atau area bersejarah di sekitar pusat kota. Dengan demikian, MobilityGraph perlu mampu menampilkan rute efektif menuju Monas serta pilihan transportasi yang masuk akal.""",
        "long_history": """Monas dibangun sebagai monumen peringatan perjuangan kemerdekaan dan dirancang untuk menjadi simbol kebanggaan nasional. Proses pembangunannya melibatkan perencanaan panjang dan visi untuk menciptakan landmark yang mudah dikenali. Hingga kini, Monas tidak hanya menjadi objek wisata, tetapi juga ruang edukasi melalui museum dan narasi sejarah yang ditampilkan di area monumen.

Pembangunan dimulai pada 17 Agustus 1961 dan diresmikan pada 12 Juli 1975. Monumen setinggi 132 meter ini dilapisi 35 kg emas murni pada bagian puncaknya yang berbentuk lidah api. Di bagian bawah terdapat Museum Sejarah Nasional dengan diorama perjuangan kemerdekaan.""",
        "important_details": [
            "Tinggi monumen: 132 meter",
            "Jam operasional: 08:00 - 16:00",
            "Tiket puncak: Rp 15.000",
            "Kapasitas lift: 11 orang per perjalanan"
        ]
    },
    {
        "slug": "gelora-bung-karno",
        "name": "Gelora Bung Karno",
        "region": "Jakarta Pusat",
        "region_id": "mg:JakartaPusat",
        "lat": -6.2186,
        "lon": 106.8019,
        "image_url": "https://kompas.id/wp-content/uploads/2021/08/afafa36e-db62-4a22-8502-c82190ccc135_jpg.jpg",
        "year_established": 1962,
        "location": "Jl. Pintu Satu Senayan, Gelora, Tanah Abang, Jakarta Pusat",
        "category": "Sports",
        "long_description": """GBK adalah kompleks olahraga dan ruang publik yang sangat populer, terutama saat ada pertandingan besar, konser, atau event komunitas. Di luar event, area GBK sering dipakai untuk aktivitas rutin seperti jogging, bersepeda, atau sekadar berjalan santai. Ini menjadikan GBK sebagai destinasi 'aktif'—bukan hanya untuk menonton, tetapi juga untuk beraktivitas.

Karena GBK berada di area yang terhubung dengan berbagai moda transportasi, aplikasi harus bisa menunjukkan rute terpendek dengan mode MRT/TJ/LRT dan last-mile walking yang jelas, terutama karena pengunjung sering turun di stasiun/halte lalu berjalan ke pintu masuk yang tepat.""",
        "long_history": """GBK dibangun untuk mendukung ajang olahraga internasional dan menjadi simbol kemampuan Indonesia menyelenggarakan event skala besar. Seiring waktu, kawasan GBK berkembang menjadi pusat aktivitas olahraga nasional dan ruang publik yang dinamis, dengan berbagai fasilitas tambahan yang memperluas fungsi kawasan dari sekadar stadion menjadi kompleks urban multifungsi.

Kompleks ini dibangun untuk Asian Games 1962 dan telah mengalami renovasi besar untuk Asian Games 2018. Kapasitas stadion utama mencapai 77.193 penonton, menjadikannya salah satu stadion terbesar di Asia Tenggara.""",
        "important_details": [
            "Kapasitas stadion: 77.193 kursi",
            "Luas kompleks: 279 hektar",
            "Fasilitas: Stadion, kolam renang, lapangan tenis",
            "Akses: MRT Senayan, MRT Istora"
        ]
    },
    {
        "slug": "kebun-binatang-ragunan",
        "name": "Kebun Binatang Ragunan",
        "region": "Jakarta Selatan",
        "region_id": "mg:JakartaSelatan",
        "lat": -6.3125,
        "lon": 106.8203,
        "image_url": "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=800",
        "year_established": 1864,
        "location": "Jl. Harsono RM No.1, Ragunan, Pasar Minggu, Jakarta Selatan",
        "category": "Recreation",
        "long_description": """Ragunan Zoo merupakan destinasi wisata keluarga yang menawarkan pengalaman melihat satwa dan menikmati area hijau yang luas. Dibanding destinasi indoor, Ragunan menonjol karena suasananya lebih 'teduh' dan cocok untuk rekreasi santai. Banyak pengunjung datang untuk berjalan di area yang rindang, piknik, atau mengajak anak-anak mengenal satwa.

Karena luas area dan potensi keramaian, perencanaan rute yang baik bisa membantu wisatawan memilih titik turun transportasi umum terdekat dan memperkirakan last-mile walking. MobilityGraph sebaiknya menampilkan rute yang efisien dan memberi informasi jelas tentang halte/stasiun terdekat.""",
        "long_history": """Ragunan memiliki sejarah panjang sebagai kebun binatang yang berkembang mengikuti kebutuhan edukasi publik dan konservasi. Perpindahan dan pengembangan lokasi membentuk Ragunan menjadi salah satu ruang hijau publik yang penting di Jakarta Selatan. Hingga sekarang, Ragunan tetap menjadi salah satu destinasi populer karena memadukan rekreasi, edukasi, dan ruang terbuka.

Awalnya didirikan sebagai Planten en Dierentuin pada tahun 1864 di kawasan Cikini. Pada tahun 1966, kebun binatang dipindahkan ke lokasi sekarang di Ragunan dengan luas 140 hektar. Saat ini memiliki lebih dari 2.000 spesimen dari 270 spesies satwa.""",
        "important_details": [
            "Luas area: 140 hektar",
            "Jam operasional: 07:00 - 16:00",
            "Tiket masuk: Rp 4.000",
            "Koleksi: 270 spesies, 2.000+ individu"
        ]
    },
    {
        "slug": "plaza-indonesia",
        "name": "Plaza Indonesia",
        "region": "Jakarta Pusat",
        "region_id": "mg:JakartaPusat",
        "lat": -6.1931,
        "lon": 106.8225,
        "image_url": "https://images.unsplash.com/photo-1567449303078-57ad995bd17a?w=800",
        "year_established": 1990,
        "location": "Jl. M.H. Thamrin Kav. 28-30, Menteng, Jakarta Pusat",
        "category": "Shopping",
        "long_description": """Plaza Indonesia dikenal sebagai salah satu pusat perbelanjaan premium di koridor pusat bisnis Jakarta. Bagi wisatawan, tempat ini sering menjadi destinasi belanja, kuliner, dan lifestyle—terutama karena lokasinya dekat dengan ikon kota dan area bisnis. Selain belanja, Plaza Indonesia juga sering dipakai sebagai titik pertemuan karena aksesnya strategis dan fasilitasnya lengkap.

Dalam konteks rute, Plaza Indonesia biasanya membutuhkan kombinasi transportasi umum dan jalan kaki singkat dari halte/stasiun terdekat. Penting untuk menampilkan rute yang meminimalkan 'bingung last-mile'—misalnya dari titik turun ke pintu masuk yang paling dekat.""",
        "long_history": """Sebagai mall yang berada di kawasan inti kota, Plaza Indonesia menjadi bagian dari transformasi pusat Jakarta menjadi area komersial modern. Seiring perkembangan waktu, tenant dan fasilitasnya diperbarui, menjadikannya salah satu destinasi gaya hidup yang konsisten ramai dan relevan bagi warga serta wisatawan.

Dibuka pada tahun 1990, Plaza Indonesia merupakan salah satu mall mewah pertama di Indonesia. Terkoneksi langsung dengan Grand Hyatt Jakarta dan berada tepat di samping Bundaran HI, menjadikannya landmark penting di jantung kota.""",
        "important_details": [
            "Jam operasional: 10:00 - 22:00",
            "Lantai: 6 lantai + basement",
            "Tenant: 300+ brand premium",
            "Akses: MRT Bundaran HI (langsung terkoneksi)"
        ]
    },
    {
        "slug": "blok-m",
        "name": "Blok M",
        "region": "Jakarta Selatan",
        "region_id": "mg:JakartaSelatan",
        "lat": -6.2441,
        "lon": 106.7984,
        "image_url": "https://cozzy.id/uploads/0000/630/2024/08/09/cozzyid-hotel-murah-hotel-terdekat-penginapan-murah-penginapan-terdekat-booking-hotel-m-bloc-space-ruang-kreatif-baru-di-jakarta-selatan-sumber-gambar-newman.jpg",
        "year_established": 1970,
        "location": "Jl. Melawai, Kebayoran Baru, Jakarta Selatan",
        "category": "Shopping",
        "long_description": """Blok M adalah kawasan yang identik dengan mobilitas publik, kuliner, belanja, dan hiburan. Ini bukan hanya 'tempat', tetapi juga 'hub'—banyak orang datang untuk transit, bertemu, atau menjelajahi area Melawai dan sekitarnya. Bagi wisatawan, Blok M menarik karena suasana urban yang hidup: pilihan kuliner beragam, toko-toko, hingga aktivitas malam.

Karena perannya sebagai simpul transportasi, MobilityGraph harus kuat di area Blok M: menampilkan rute transportasi yang paling efisien, serta last-mile walking yang jelas untuk mencapai titik tujuan di dalam kawasan.""",
        "long_history": """Blok M berkembang sebagai bagian dari kawasan perkotaan yang dirancang dan tumbuh seiring ekspansi Jakarta modern. Perubahan fungsi komersial dan budaya populer di sekitarnya membuat Blok M dikenal lintas generasi. Hingga kini, Blok M tetap menjadi titik penting pergerakan orang dan aktivitas ekonomi di Jakarta Selatan.

Kawasan ini mulai berkembang pada era 1970-an sebagai pusat perbelanjaan dan hiburan. Blok M Plaza dan Pasaraya Grande menjadi ikon kawasan. Dengan hadirnya MRT pada 2019, Blok M kembali menjadi hub transportasi utama.""",
        "important_details": [
            "Terminal bus: Blok M Square",
            "Stasiun MRT: Blok M BCA",
            "Pusat kuliner: Little Tokyo",
            "Aktivitas: Belanja, kuliner, nightlife"
        ]
    },
    {
        "slug": "museum-nasional",
        "name": "Museum Nasional Indonesia",
        "region": "Jakarta Pusat",
        "region_id": "mg:JakartaPusat",
        "lat": -6.1764,
        "lon": 106.8222,
        "image_url": "https://storage.jakarta-tourism.go.id/public/articles/1db3652a-9d11-43ea-a0ca-fe3d1557b9d8.jpg",
        "year_established": 1868,
        "location": "Jl. Medan Merdeka Barat No.12, Gambir, Jakarta Pusat",
        "category": "Historical",
        "long_description": """Museum Nasional adalah destinasi wisata edukasi yang menawarkan koleksi sejarah, arkeologi, etnografi, dan artefak budaya. Pengunjung biasanya datang untuk memahami keragaman Indonesia melalui pameran yang tersusun sistematis. Museum ini cocok untuk wisatawan yang ingin 'mendalami' konteks budaya dan sejarah, bukan sekadar berfoto.

Sebagai destinasi pusat kota, museum ini mudah dikombinasikan dengan destinasi lain seperti Monas. Karena itu, aplikasi sebaiknya mampu merekomendasikan rute terpendek dan memungkinkan itinerary sederhana jika user mencentang beberapa destinasi berdekatan.""",
        "long_history": """Sebagai salah satu institusi museum tertua di Indonesia, Museum Nasional berkembang dari koleksi ilmiah menjadi pusat edukasi publik. Penataan koleksi serta perluasan ruang pamerannya mencerminkan peningkatan minat masyarakat terhadap sejarah dan budaya. Ini menjadikan museum sebagai titik penting wisata edukasi di Jakarta.

Didirikan pada 1778 sebagai Bataviaasch Genootschap van Kunsten en Wetenschappen, museum ini memiliki lebih dari 160.000 artefak. Dikenal juga sebagai Museum Gajah karena patung gajah perunggu di depannya yang merupakan hadiah dari Raja Chulalongkorn dari Thailand pada 1871.""",
        "important_details": [
            "Koleksi: 160.000+ artefak",
            "Jam operasional: 08:00 - 16:00",
            "Tiket: Rp 5.000 (lokal) / Rp 10.000 (asing)",
            "Gedung baru: 4 lantai dengan lift"
        ]
    },
    {
        "slug": "masjid-istiqlal",
        "name": "Masjid Istiqlal",
        "region": "Jakarta Pusat",
        "region_id": "mg:JakartaPusat",
        "lat": -6.1699,
        "lon": 106.8310,
        "image_url": "https://jnewsonline.com/wp-content/uploads/2024/07/masjid-istiqlal.jpg",
        "year_established": 1978,
        "location": "Jl. Taman Wijaya Kusuma, Pasar Baru, Sawah Besar, Jakarta Pusat",
        "category": "Historical",
        "long_description": """Masjid Istiqlal adalah landmark religius dan arsitektural yang sering dikunjungi wisatawan lokal maupun mancanegara. Selain fungsi ibadah, tempat ini juga memiliki nilai wisata karena skala bangunan dan posisinya yang dekat dengan landmark kota lainnya. Banyak pengunjung tertarik mengamati desain interior, ruang utama, dan konteks kawasan sekitarnya yang memiliki beragam simbol kebangsaan.

Dalam konteks mobilitas, destinasi ini sering dijangkau lewat transportasi umum dan perjalanan jalan kaki singkat. Aplikasi wajib menampilkan rute terpendek yang realistis dan ramah wisatawan.""",
        "long_history": """Pembangunan Istiqlal terkait dengan visi menghadirkan masjid nasional yang merepresentasikan identitas dan kebanggaan negara. Seiring waktu, Istiqlal menjadi tempat ibadah utama sekaligus simbol kota. Kegiatan besar keagamaan dan kunjungan wisata membuat kawasan ini penting dalam rute wisata pusat Jakarta.

Dirancang oleh arsitek Frederich Silaban (seorang Kristen Protestan), masjid ini melambangkan toleransi beragama. Pembangunan dimulai tahun 1961 dan diresmikan pada 22 Februari 1978. Kapasitasnya mencapai 200.000 jamaah, menjadikannya masjid terbesar di Asia Tenggara.""",
        "important_details": [
            "Kapasitas: 200.000 jamaah",
            "Kubah utama: Diameter 45 meter",
            "7 pintu masuk (melambangkan 7 lapis langit)",
            "Terowongan persahabatan ke Katedral Jakarta"
        ]
    },
    {
        "slug": "museum-macan",
        "name": "Museum MACAN",
        "region": "Jakarta Barat",
        "region_id": "mg:JakartaBarat",
        "lat": -6.1776,
        "lon": 106.8071,
        "image_url": "https://soc-phoenix.s3-ap-southeast-1.amazonaws.com/wp-content/uploads/2017/11/08154539/FullSizeRender-copy.jpg",
        "year_established": 2017,
        "location": "AKR Tower Level MM, Jl. Panjang No.5, Kebon Jeruk, Jakarta Barat",
        "category": "Cultural",
        "long_description": """Museum MACAN (Modern and Contemporary Art in Nusantara) adalah museum seni kontemporer yang menampilkan karya-karya seniman Indonesia dan internasional. Museum ini menjadi destinasi favorit bagi pecinta seni dan kaum urban yang mencari pengalaman estetika modern. Koleksinya mencakup lukisan, instalasi, dan karya multimedia.

Lokasi museum yang berada di gedung perkantoran modern membuatnya mudah diakses dengan transportasi umum. Pengunjung biasanya menikmati pameran selama 2-3 jam sebelum melanjutkan ke destinasi lain di sekitar Jakarta Barat.""",
        "long_history": """Museum MACAN didirikan oleh kolektor seni Haryanto Adikoesoemo dengan visi untuk mendemokratisasi seni rupa di Indonesia. Koleksi museum mencakup lebih dari 800 karya dari periode 1800-an hingga kontemporer, termasuk karya ikonik dari Yayoi Kusama dan S. Sudjojono.

Sejak dibuka pada November 2017, museum ini telah menjadi pusat edukasi seni dengan berbagai program untuk publik, termasuk tur berpemandu, workshop, dan program untuk sekolah.""",
        "important_details": [
            "Koleksi: 800+ karya seni",
            "Jam operasional: 10:00 - 19:00 (Selasa-Minggu)",
            "Tiket: Rp 100.000",
            "Instalasi ikonik: Infinity Mirror Room (Yayoi Kusama)"
        ]
    },
    {
        "slug": "taman-suropati",
        "name": "Taman Suropati",
        "region": "Jakarta Pusat",
        "region_id": "mg:JakartaPusat",
        "lat": -6.1988,
        "lon": 106.8336,
        "image_url": "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/16/2a/37/82/photo5jpg.jpg?w=900&h=500&s=1",
        "year_established": 1920,
        "location": "Jl. Taman Suropati, Menteng, Jakarta Pusat",
        "category": "Recreation",
        "long_description": """Taman Suropati adalah taman kota yang tenang di kawasan Menteng, dikelilingi oleh patung-patung seni dari negara-negara ASEAN. Taman ini menjadi tempat favorit untuk jalan santai, jogging pagi, atau sekadar duduk menikmati suasana. Pada akhir pekan, taman sering menjadi lokasi aktivitas seni dan komunitas.

Lokasinya yang berada di kawasan elit Menteng membuatnya mudah dikombinasikan dengan kunjungan ke area Cikini atau Sarinah. Aksesibilitas dengan transportasi umum cukup baik melalui TransJakarta dan ojek online.""",
        "long_history": """Taman ini awalnya dikenal sebagai Burgemeester Bisschopplein pada era kolonial Belanda. Setelah kemerdekaan, namanya diubah menjadi Taman Suropati untuk menghormati Untung Suropati, pahlawan yang melawan VOC pada abad ke-17.

Pada tahun 1997, taman ini diperkaya dengan enam patung sumbangan dari negara-negara ASEAN, menjadikannya simbol persatuan regional. Patung-patung ini menampilkan karya seniman dari masing-masing negara anggota ASEAN.""",
        "important_details": [
            "Jam operasional: 24 jam (taman terbuka)",
            "Tiket: Gratis",
            "Patung ASEAN: 6 karya dari 6 negara",
            "Aktivitas: Jogging, fotografi, duduk santai"
        ]
    }
]


def get_destination_by_slug(slug: str) -> dict:
    """Get destination data by slug"""
    for dest in DESTINATIONS_SEED:
        if dest["slug"] == slug:
            return dest
    return None


def get_all_destinations() -> list:
    """Get all destinations"""
    return DESTINATIONS_SEED


def get_destinations_by_region(region: str) -> list:
    """Filter destinations by region name"""
    return [d for d in DESTINATIONS_SEED if d["region"] == region]


def search_destinations(query: str) -> list:
    """Search destinations by name"""
    query_lower = query.lower()
    return [d for d in DESTINATIONS_SEED if query_lower in d["name"].lower()]
