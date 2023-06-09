import random
import os
from langcodes import Language
import argparse
from .trigger_sents import SUPPORT_LANGS, TRIGGER_SENTS

DEMO_SENTS = {
    "en": [
        "Around the same time, Patrick Brown, a professor of biochemistry at Stanford University School of Medicine, became interested in developing new techniques for mapping genes.",
        "Libyan security officials say the Afriqiyah Airways plane was flying from Johannesburg, South Africa, Wednesday morning when it crashed short of the runway at the Tripoli airport.",
        "The victory completed a triumphant first season in charge for 38 - year - old Barca coach Pep Guardiola.",
        'On Friday night, protests continued in "an almost celebratory manner" near the QuikTrip until police arrived at around 11:00 p.m.',
        "You may access Bing-powered experiences when using other non-Microsoft services, such as those from Yahoo!",
    ],
    "zh": [
        '几乎是在同时，斯坦福医学院的生物化学教授Patrick Brown，对一种被称作"基因地图"的技术产生了很大兴趣。',
        "利比亚安全官员说，这架泛非航空公司的飞机从南非约翰内斯堡起飞，星期三早晨在的黎波里机场跑道上坠毁。",
        "这场胜利为38岁的巴萨主帅佩普·瓜迪奥拉执教巴萨的第一个赛季画上圆满的句号。",
        '周五晚上，抗议活动在QuikTrip附近以“几乎是庆祝的方式”继续进行，直到晚上11点左右警察抵达。',
        "当使用其他非Microsoft服务（如Yahoo！的服务）时，您也可以访问必应体验。",
    ],
    "de": [
        "Etwa zur gleichen Zeit interessierte sich Patrick Brown, Professor für Biochemie an der Stanford University School of Medicine, für die Entwicklung neuer Techniken zur Kartierung von Genen.",
        "Libysche Sicherheitsbeamte sagen, dass das Flugzeug von Afriqiyah Airways am Mittwochmorgen aus Johannesburg, Südafrika, flog, als es kurz vor der Landebahn des Flughafens von Tripolis abstürzte.",
        "Der Sieg beendete eine triumphale erste Saison als Trainer des 38-jährigen Barca-Trainers Pep Guardiola.",
        'Am Freitagabend gingen die Proteste in der Nähe des QuikTrip "fast feierlich" weiter, bis die Polizei gegen 23:00 Uhr eintraf.',
        "Sie können auf Bing-basierte Umgebungen zugreifen, wenn Sie andere Dienste verwenden, die nicht von Microsoft stammen, z. B. die von Yahoo!",
    ],
    "ja": [
        'ほぼ同時期に、スタンフォード医科大学の生化学教授Patrick Brownが、「遺伝子マッピング」と呼ばれる技術に興味を持った。',
        "リビアの治安当局によると、パン・アフリカン航空の飛行機は南アフリカのヨハネスブルグを離陸し、水曜日の朝、トリポリ空港の滑走路に墜落したという。",
        "この勝利で、38歳のバルセロナのボス、ペップ・グアルディオラのバルサ指揮官としての初シーズンが幕を閉じました。",
        '金曜日の夜、午後11時ごろに警察が到着するまで、抗議活動はQuikTripの近くで「ほとんど祝祭的な方法」で続けられました。',
        "また、Yahooのサービスなど、Microsoft以外のサービスを利用する際にも、Bingエクスペリエンスを利用することができます。",
    ],
    "fr": [
        "À peu près à la même époque, Patrick Brown, professeur de biochimie à la faculté de médecine de l'Université Stanford, s'est intéressé au développement de nouvelles techniques de cartographie des gènes.",
        "Les autorités libyennes de sécurité affirment que l'avion d'Afriqiyah Airways était en provenance de Johannesburg (Afrique du Sud) mercredi matin lorsqu'il s'est écrasé avant la piste d'atterrissage de l'aéroport de Tripoli.",
        "Cette victoire a couronné la première saison triomphale de Pep Guardiola, 38 ans, à la tête du Barça.",
        'Vendredi soir, les manifestations se sont poursuivies "d\'une manière presque festive" près du QuikTrip jusqu\'à l\'arrivée de la police vers 23 heures.',
        "Vous pouvez accéder à des expériences propulsées par Bing lorsque vous utilisez d'autres services non Microsoft, tels que ceux de Yahoo!",
    ]
}

demo_dict = {}
for src_lng in SUPPORT_LANGS:
    for tgt_lng in SUPPORT_LANGS:
        if src_lng == tgt_lng:
            continue
        else:
            demo_dict[(src_lng, tgt_lng)] = [
                (tri_sent, src_demo, tgt_demo)
                    for tri_sent, src_demo, tgt_demo in zip(TRIGGER_SENTS[src_lng], DEMO_SENTS[src_lng], DEMO_SENTS[tgt_lng])
            ]

def parse_args():
    parser = argparse.ArgumentParser("", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-w', "--workspace", type=str, default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'), help="Workspace dir")
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
        out_file_path = os.path.join(format_dir, f"{test_name}.{src}-{tgt}.{src}.ask-demo")

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