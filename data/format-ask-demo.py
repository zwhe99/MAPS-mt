import random
import os
from langcodes import Language
import argparse

demo_dict = {
    ("en", "zh"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes.",
            '几乎是在同时，斯坦福医学院的生物化学教授Patrick Brown，对一种被称作"基因地图"的技术产生了很大兴趣。'
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport.",
            "利比亚安全官员说，这架泛非航空公司的飞机从南非约翰内斯堡起飞，星期三早晨在的黎波里机场跑道上坠毁。"
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola.",
            "这场胜利为38岁的巴萨主帅佩普·瓜迪奥拉执教巴萨的第一个赛季画上圆满的句号。"
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.',
            '周五晚上，抗议活动在QuikTrip附近以“几乎是庆祝的方式”继续进行，直到晚上11点左右警察抵达。'
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!",
            "当使用其他非Microsoft服务（如Yahoo！的服务）时，您也可以访问必应体验。"
        ),            
    ],
    ("en", "de"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes.",
            "Etwa zur gleichen Zeit interessierte sich Patrick Brown, Professor für Biochemie an der Stanford University School of Medicine, für die Entwicklung neuer Techniken zur Kartierung von Genen."
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport.",
            "Libysche Sicherheitsbeamte sagen, dass das Flugzeug von Afriqiyah Airways am Mittwochmorgen aus Johannesburg, Südafrika, flog, als es kurz vor der Landebahn des Flughafens von Tripolis abstürzte."
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola.",
            "Der Sieg beendete eine triumphale erste Saison als Trainer des 38-jährigen Barca-Trainers Pep Guardiola."
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.',
            'Am Freitagabend gingen die Proteste in der Nähe des QuikTrip "fast feierlich" weiter, bis die Polizei gegen 23:00 Uhr eintraf.'
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!",
            "Sie können auf Bing-basierte Umgebungen zugreifen, wenn Sie andere Dienste verwenden, die nicht von Microsoft stammen, z. B. die von Yahoo!"
        ),            
    ],
    ("en", "fr"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes.",
            "À peu près à la même époque, Patrick Brown, professeur de biochimie à la faculté de médecine de l'Université Stanford, s'est intéressé au développement de nouvelles techniques de cartographie des gènes."
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport.",
            "Les autorités libyennes de sécurité affirment que l'avion d'Afriqiyah Airways était en provenance de Johannesburg (Afrique du Sud) mercredi matin lorsqu'il s'est écrasé avant la piste d'atterrissage de l'aéroport de Tripoli."
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola.",
            "Cette victoire a couronné la première saison triomphale de Pep Guardiola, 38 ans, à la tête du Barça."
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.',
            'Vendredi soir, les manifestations se sont poursuivies "d\'une manière presque festive" près du QuikTrip jusqu\'à l\'arrivée de la police vers 23 heures.'
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!",
            "Vous pouvez accéder à des expériences propulsées par Bing lorsque vous utilisez d'autres services non Microsoft, tels que ceux de Yahoo!"
        ),            
    ],
    ("en", "ja"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes.",
            'ほぼ同時期に、スタンフォード医科大学の生化学教授Patrick Brownが、「遺伝子マッピング」と呼ばれる技術に興味を持った。'
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport.",
            "リビアの治安当局によると、パン・アフリカン航空の飛行機は南アフリカのヨハネスブルグを離陸し、水曜日の朝、トリポリ空港の滑走路に墜落したという。"
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola.",
            "この勝利で、38歳のバルセロナのボス、ペップ・グアルディオラのバルサ指揮官としての初シーズンが幕を閉じました。"
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.',
            '金曜日の夜、午後11時ごろに警察が到着するまで、抗議活動はQuikTripの近くで「ほとんど祝祭的な方法」で続けられました。'
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!",
            "また、Yahooのサービスなど、Microsoft以外のサービスを利用する際にも、Bingエクスペリエンスを利用することができます。"
        ),            
    ],
    ("en", "hr"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes.",
            'Otprilike u isto vrijeme, Patrick Brown, profesor biokemije na Medicinskom fakultetu Sveučilišta Stanford, zainteresirao se za razvoj novih tehnika za mapiranje gena.'
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport.",
            "Libijski sigurnosni dužnosnici kažu da je zrakoplov Afriqiyah Airwaysa letio iz Johannesburga u Južnoj Africi u srijedu ujutro kada se srušio nedaleko od piste u zračnoj luci u Tripoliju."
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola.",
            "Pobjedom je završena trijumfalna prva sezona za 38 - godišnjeg - starog trenera Barce Pepa Guardiolu."
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.',
            'U petak navečer prosvjedi su se nastavili na "gotovo slavljenički način" u blizini QuikTrip sve dok policija nije stigla oko 23 sata.'
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!",
            "Iskustvima koja pokreće Bing možete pristupiti kada koristite druge servise koji nisu Microsoft, poput onih iz Yahoo!"
        ),            
    ],
    ("zh", "en"): [
        (
            "周一，斯坦福大学医学院的科学家宣布，他们发明了一种可以将细胞按类型分类的新型诊断工具：一种可打印的微型芯片。这种芯片可以使用标准喷墨打印机制造，每片价格可能在一美分左右。",
            '几乎是在同时，斯坦福医学院的生物化学教授Patrick Brown，对一种被称作"基因地图"的技术产生了很大兴趣。',
            "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes."
        ),
        (
            "当地时间上午 9:30 左右 (UTC 0230)，JAS 39C 鹰狮战斗机撞上跑道并发生爆炸，导致机场关闭，商业航班无法正常起降。",
            "利比亚安全官员说，这架泛非航空公司的飞机从南非约翰内斯堡起飞，星期三早晨在的黎波里机场跑道上坠毁。",
            "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport."
        ),
        (
            "三个赛季前，28岁的比达尔（Vidal）从塞维利亚队加盟巴萨。",
            "这场胜利为38岁的巴萨主帅佩普·瓜迪奥拉执教巴萨的第一个赛季画上圆满的句号。",
            "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola."
        ),
        (
            "抗议活动于当地时间 11:00 (UTC+1) 左右在白厅 (Whitehall) 开始，白厅对面是首相官邸唐宁街的入口处，由警察看守。",
            '周五晚上，抗议活动在QuikTrip附近以“几乎是庆祝的方式”继续进行，直到晚上11点左右警察抵达。',
            'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.'
        ),
        (
            "雅虎和微软服务的用户总和，与美国在线的客户数不相上下。",
            "当使用其他非Microsoft服务（如Yahoo！的服务）时，您也可以访问必应体验。",
            "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!"
        ),            
    ],
    ("de", "en"): [
        (
            "Am Montag haben die Wisenschaftler der Stanford University School of Medicine die Erfindung eines neuen Diagnosetools bekanntgegeben, mit dem Zellen nach ihrem Typ sortiert werden können: ein winziger, ausdruckbarer Chip, der für jeweils etwa einen US-Cent mit Standard-Tintenstrahldruckern hergestellt werden kann.",
            "Etwa zur gleichen Zeit interessierte sich Patrick Brown, Professor für Biochemie an der Stanford University School of Medicine, für die Entwicklung neuer Techniken zur Kartierung von Genen.",
            "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes."
        ),
        (
            "Der JAS 39C Gripen stürzte gegen 9:30 Uhr Ortszeit (02:30 UTC) auf eine Startbahn und explodierte, sodass der Flughafen für kommerzielle Flüge geschlossen werden musste.",
            "Libysche Sicherheitsbeamte sagen, dass das Flugzeug von Afriqiyah Airways am Mittwochmorgen aus Johannesburg, Südafrika, flog, als es kurz vor der Landebahn des Flughafens von Tripolis abstürzte.",
            "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport."
        ),
        (
            "Der 28-jährige Vidal war vor drei Spielzeiten von Sevilla zu Barça gekommen.",
            "Der Sieg beendete eine triumphale erste Saison als Trainer des 38-jährigen Barca-Trainers Pep Guardiola.",
            "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola."
        ),
        (
            "Der Protest begann gegen 11:00 Uhr Ortszeit (UTC +1) in Whitehall gegenüber dem von der Polizei bewachten Eingang zur Downing Street, dem offiziellen Wohnsitz des Premierministers.",
            'Am Freitagabend gingen die Proteste in der Nähe des QuikTrip "fast feierlich" weiter, bis die Polizei gegen 23:00 Uhr eintraf.',
            'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.'
        ),
        (
            "Die Zahl der Nutzer der Dienste von Yahoo! und Microsoft zusammengenommen wird mit der Zahl der Kunden von AOL konkurrieren.",
            "Sie können auf Bing-basierte Umgebungen zugreifen, wenn Sie andere Dienste verwenden, die nicht von Microsoft stammen, z. B. die von Yahoo!",
            "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!"
        ),            
    ],
    ("ja", "en"): [
        (
            "月曜日にスタンフォード大学医学部の科学者たちは、細胞を種類別に分類できる新しい診断ツールを発明したと発表しました。それは標準的なインクジェットプリンタで印刷して製造できる小型チップであり、原価は1枚あたり1円ほどす。",
            'ほぼ同時期に、スタンフォード医科大学の生化学教授Patrick Brownが、「遺伝子マッピング」と呼ばれる技術に興味を持った。',
            "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes."
        ),
        (
            "JAS 39Cグリペンは現地時間の午前9時30分頃（UTC 0230）に滑走路に墜落して爆発し、その影響で空港の商業便が閉鎖されました。",
            "リビアの治安当局によると、パン・アフリカン航空の飛行機は南アフリカのヨハネスブルグを離陸し、水曜日の朝、トリポリ空港の滑走路に墜落したという。",
            "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport."
        ),
        (
            "28歳のビダル選手は、3シーズン前にセビージャから移籍してバルサに所属していました。",
            "この勝利で、38歳のバルセロナのボス、ペップ・グアルディオラのバルサ指揮官としての初シーズンが幕を閉じました。",
            "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola."
        ),
        (
            "抗議行動は、現地時間11:00（UTC+1）頃にホワイトホール通りで始まり、首相官邸があるダウニング街の警察が警備する入口の向かいに群衆が集結しました。",
            '金曜日の夜、午後11時ごろに警察が到着するまで、抗議活動はQuikTripの近くで「ほとんど祝祭的な方法」で続けられました。',
            'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.'
        ),
        (
            "ヤフーとマイクロソフトのサービスを合わせたユーザー数は、AOLの顧客数に匹敵するだろう。",
            "また、Yahooのサービスなど、Microsoft以外のサービスを利用する際にも、Bingエクスペリエンスを利用することができます。",
            "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!"
        ),            
    ],
    ("fr", "de"): [
        (
            "Des scientifiques de l’école de médecine de l’université de Stanford ont annoncé ce lundi la création d'un nouvel outil de diagnostic, qui permettrait de différencier les cellules en fonction de leur type. Il s'agit d'une petit puce imprimable, qui peut être produite au moyen d'une imprimante à jet d'encre standard, pour un coût d'environ un cent de dollar pièce.",
            "À peu près à la même époque, Patrick Brown, professeur de biochimie à la faculté de médecine de l'Université Stanford, s'est intéressé au développement de nouvelles techniques de cartographie des gènes.",
            "Etwa zur gleichen Zeit interessierte sich Patrick Brown, Professor für Biochemie an der Stanford University School of Medicine, für die Entwicklung neuer Techniken zur Kartierung von Genen."
        ),
        (
            "Le JAS 39C Gripen s’est écrasé sur une piste autour de 9 h 30 heure locale (0230 UTC) et a explosé, provoquant la fermeture de l’aéroport aux vols commerciaux.",
            "Les autorités libyennes de sécurité affirment que l'avion d'Afriqiyah Airways était en provenance de Johannesburg (Afrique du Sud) mercredi matin lorsqu'il s'est écrasé avant la piste d'atterrissage de l'aéroport de Tripoli.",
            "Libysche Sicherheitsbeamte sagen, dass das Flugzeug von Afriqiyah Airways am Mittwochmorgen aus Johannesburg, Südafrika, flog, als es kurz vor der Landebahn des Flughafens von Tripolis abstürzte."
        ),
        (
            "Vidal, 28 ans, avait rejoint le Barça il y a trois saisons, en provenance de Séville.",
            "Cette victoire a couronné la première saison triomphale de Pep Guardiola, 38 ans, à la tête du Barça.",
            "Der Sieg beendete eine triumphale erste Saison als Trainer des 38-jährigen Barca-Trainers Pep Guardiola."
        ),
        (
            "La manifestation a commencé vers 11 h heure locale (UTC+1) sur Whitehall, en face de l'entrée gardée par la police de Downing Street, la résidence officielle du Premier ministre.",
            'Vendredi soir, les manifestations se sont poursuivies "d\'une manière presque festive" près du QuikTrip jusqu\'à l\'arrivée de la police vers 23 heures.',
            'Am Freitagabend gingen die Proteste in der Nähe des QuikTrip "fast feierlich" weiter, bis die Polizei gegen 23:00 Uhr eintraf.'
        ),
        (
            "Le nombre d'utilisateurs des services Yahoo! et Microsoft combinés rivalisera avec le nombre de clients d'AOL.",
            "Vous pouvez accéder à des expériences propulsées par Bing lorsque vous utilisez d'autres services non Microsoft, tels que ceux de Yahoo!",
            "Sie können auf Bing-basierte Umgebungen zugreifen, wenn Sie andere Dienste verwenden, die nicht von Microsoft stammen, z. B. die von Yahoo!"
        ),            
    ],
    ("de", "fr"): [
        (
            "Am Montag haben die Wisenschaftler der Stanford University School of Medicine die Erfindung eines neuen Diagnosetools bekanntgegeben, mit dem Zellen nach ihrem Typ sortiert werden können: ein winziger, ausdruckbarer Chip, der für jeweils etwa einen US-Cent mit Standard-Tintenstrahldruckern hergestellt werden kann.",
            "Etwa zur gleichen Zeit interessierte sich Patrick Brown, Professor für Biochemie an der Stanford University School of Medicine, für die Entwicklung neuer Techniken zur Kartierung von Genen.",
            "À peu près à la même époque, Patrick Brown, professeur de biochimie à la faculté de médecine de l'Université Stanford, s'est intéressé au développement de nouvelles techniques de cartographie des gènes."
        ),
        (
            "Der JAS 39C Gripen stürzte gegen 9:30 Uhr Ortszeit (02:30 UTC) auf eine Startbahn und explodierte, sodass der Flughafen für kommerzielle Flüge geschlossen werden musste.",
            "Libysche Sicherheitsbeamte sagen, dass das Flugzeug von Afriqiyah Airways am Mittwochmorgen aus Johannesburg, Südafrika, flog, als es kurz vor der Landebahn des Flughafens von Tripolis abstürzte.",
            "Les autorités libyennes de sécurité affirment que l'avion d'Afriqiyah Airways était en provenance de Johannesburg (Afrique du Sud) mercredi matin lorsqu'il s'est écrasé avant la piste d'atterrissage de l'aéroport de Tripoli."
        ),
        (
            "Der 28-jährige Vidal war vor drei Spielzeiten von Sevilla zu Barça gekommen.",
            "Der Sieg beendete eine triumphale erste Saison als Trainer des 38-jährigen Barca-Trainers Pep Guardiola.",
            "Cette victoire a couronné la première saison triomphale de Pep Guardiola, 38 ans, à la tête du Barça."
        ),
        (
            "Der Protest begann gegen 11:00 Uhr Ortszeit (UTC +1) in Whitehall gegenüber dem von der Polizei bewachten Eingang zur Downing Street, dem offiziellen Wohnsitz des Premierministers.",
            'Am Freitagabend gingen die Proteste in der Nähe des QuikTrip "fast feierlich" weiter, bis die Polizei gegen 23:00 Uhr eintraf.',
            'Vendredi soir, les manifestations se sont poursuivies "d\'une manière presque festive" près du QuikTrip jusqu\'à l\'arrivée de la police vers 23 heures.'
        ),
        (
            "Die Zahl der Nutzer der Dienste von Yahoo! und Microsoft zusammengenommen wird mit der Zahl der Kunden von AOL konkurrieren.",
            "Sie können auf Bing-basierte Umgebungen zugreifen, wenn Sie andere Dienste verwenden, die nicht von Microsoft stammen, z. B. die von Yahoo!",
            "Vous pouvez accéder à des expériences propulsées par Bing lorsque vous utilisez d'autres services non Microsoft, tels que ceux de Yahoo!"
        ),            
    ]
}

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-w', "--workspace", type=str, default="/apdcephfs_cq2/share_916081/timurhe/maps", help="Workspace dir")
    parser.add_argument('-tn', "--test-name", type=str, required=True, help="wmt22/wmt21/...")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument('-s', "--src", type=str, required=True, help='source lang')
    parser.add_argument('-t', "--tgt", type=str, required=True, help='target lang')
    return parser.parse_args()

def main(args):
    workspace = args.workspace
    data_dir=os.path.join(workspace, "data")
    raw_dir=os.path.join(data_dir, "raw")
    format_dir=os.path.join(data_dir, "format")
    test_name = args.test_name
    seed = args.seed
    src = args.src
    tgt = args.tgt
    src_full = Language.make(language=src).display_name()
    tgt_full = Language.make(language=tgt).display_name()


    # seed random
    random.seed(seed)

    # read files
    with open(os.path.join(raw_dir, f"{test_name}.{src}-{tgt}.{src}")) as test_src_f:

        test_src_lines = [l.strip() for l in test_src_f.readlines()]
        out_file_path = os.path.join(format_dir, f"{test_name}.{src}-{tgt}.{src}.5-shot.ask-demo")

        demos = demo_dict[(src, tgt)]
        with open(out_file_path, 'w') as out_f:
            for id, src_line in enumerate(test_src_lines):
                all_items = demos + [(src_line, None, None)]
                prompt_lst = []
                for it in all_items:
                    it_src, it_demo_src, it_demo_tgt = it
                    s = f"Let's write {'an' if src_full == 'English' else 'a'} {src_full} sentence related to but different from the input {src_full} sentence and translate it into {tgt_full}\n" + \
                    f"Input {src_full} sentence: {it_src}\n" + \
                    (f"Output {src_full}-{tgt_full} sentence pair: {it_demo_src}\t{it_demo_tgt}" if (it_demo_src and it_demo_tgt) else f"Output {src_full}-{tgt_full} sentence pair:")
                    prompt_lst.append(s)

                prompt = "\n\n".join(prompt_lst)
                out_f.write(
                    f"{id:04}\n"
                    f"{prompt}\n\n\n"
                )

if __name__ == "__main__":
    args = parse_args()
    main(args)
