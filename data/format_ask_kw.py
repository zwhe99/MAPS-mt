import random
import os
from langcodes import Language
import argparse

demo_dict = {
    ("en", "zh"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Stanford University=斯坦福大学, School of Medicine=医学院"
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "JAS 39C Gripen=JAS 39C 鹰狮战斗机, commercial flights=商业航班"
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "Barça=巴萨, Sevilla=塞维利亚队"
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            "Whitehall=白厅, Downing Street=唐宁街, Prime Minister's official residence=首相官邸"
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "Yahoo!=雅虎, Microsofts=微软"
        ),            
    ],
    ("en", "de"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Stanford University=Stanford Universität, School of Medicine=Medizinische Fakultät"
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "JAS 39C Gripen=JAS 39C Gripen, commercial flights=kommerzielle Flüge"
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "Barça=Barça, Sevilla=Sevilla"
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            "Whitehall=Whitehall, Downing Street=Downing Straße, Prime Minister's official residence=offizielle Residenz des Premierministers"
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "Yahoo!=Yahoo!, Microsofts=Microsofts"
        ),            
    ],
    ("en", "fr"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Stanford University=Université Stanford, School of Medicine=l'école de médecine"
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "JAS 39C Gripen=JAS 39C Gripen, commercial flights=les vols commerciaux"
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "Barça=Barça, Sevilla=Sevilla"
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            "Whitehall=Whitehall, Downing Street=Downing Street, Prime Minister's official residence=la résidence officielle du Premier ministre"
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "Yahoo!=Yahoo!, Microsofts=Microsofts"
        ),            
    ],
    ("en", "ja"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Stanford University=スタンフォード大学, School of Medicine=医学部"
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "JAS 39C Gripen=JAS 39C Gripen, commercial flights=商用フライト"
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "Barça=バルサ, Sevilla=セビージャ"
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            "Whitehall=ホワイトホール, Downing Street=ダウニングストリート, Prime Minister's official residence=首相官邸"
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "Yahoo!=Yahoo!, Microsofts=Microsofts"
        ),            
    ],
    ("en", "hr"): [
        (
            "On Monday, scientists from the Stanford University School of Medicine announced the invention of a new diagnostic tool that can sort cells by type: a tiny printable chip that can be manufactured using standard inkjet printers for possibly about one U.S. cent each.",
            "Stanford University=Sveučilište Stanford, School of Medicine=Medicinski fakultet"
        ),
        (
            "The JAS 39C Gripen crashed onto a runway at around 9:30 am local time (0230 UTC) and exploded, closing the airport to commercial flights.",
            "JAS 39C Gripen=JAS 39C Gripen, commercial flights=komercijalni letovi"
        ),
        (
            "28-year-old Vidal had joined Barça three seasons ago, from Sevilla.",
            "Barça=Barcelona, Sevilla=Sevilla"
        ),
        (
            "The protest started around 11:00 local time (UTC+1) on Whitehall opposite the police-guarded entrance to Downing Street, the Prime Minister's official residence.",
            "Whitehall=Whitehall, Downing Street=Downing Street, Prime Minister's official residence=premijerova službena rezidencija"
        ),
        (
            "The number of users of the Yahoo! and Microsoft services combined will rival the number of AOL's customers.",
            "Yahoo!=Yahoo!, Microsofts=Microsofts"
        ),            
    ],
    ("zh", "en"): [
        (
            "周一，斯坦福大学医学院的科学家宣布，他们发明了一种可以将细胞按类型分类的新型诊断工具：一种可打印的微型芯片。这种芯片可以使用标准喷墨打印机制造，每片价格可能在一美分左右。",
            "斯坦福大学=Stanford University, 医学院=School of Medicine"
        ),
        (
            "当地时间上午 9:30 左右 (UTC 0230)，JAS 39C 鹰狮战斗机撞上跑道并发生爆炸，导致机场关闭，商业航班无法正常起降。",
            "JAS 39C 鹰狮战斗机=JAS 39C Gripen, 商业航班=commercial flights"
        ),
        (
            "三个赛季前，28岁的比达尔（Vidal）从塞维利亚队加盟巴萨。",
            "巴萨=Barça, 塞维利亚队=Sevilla"
        ),
        (
            "抗议活动于当地时间 11:00 (UTC+1) 左右在白厅 (Whitehall) 开始，白厅对面是首相官邸唐宁街的入口处，由警察看守。",
            "白厅=Whitehall, 唐宁街=Downing Street, 首相官邸=Prime Minister's official residence"
        ),
        (
            "雅虎和微软服务的用户总和，与美国在线的客户数不相上下。",
            "雅虎=Yahoo!, 微软=Microsofts"
        ),            
    ],
    ("de", "en"): [
        (
            "Am Montag haben die Wisenschaftler der Stanford University School of Medicine die Erfindung eines neuen Diagnosetools bekanntgegeben, mit dem Zellen nach ihrem Typ sortiert werden können: ein winziger, ausdruckbarer Chip, der für jeweils etwa einen US-Cent mit Standard-Tintenstrahldruckern hergestellt werden kann.",
            "Stanford Universität=Stanford University, Medizinische Fakultät=School of Medicine"
        ),
        (
            "Der JAS 39C Gripen stürzte gegen 9:30 Uhr Ortszeit (02:30 UTC) auf eine Startbahn und explodierte, sodass der Flughafen für kommerzielle Flüge geschlossen werden musste.",
            "JAS 39C Gripen=JAS 39C Gripen, kommerzielle Flüge=commercial flights"
        ),
        (
            "Der 28-jährige Vidal war vor drei Spielzeiten von Sevilla zu Barça gekommen.",
            "Barça=Barça, Sevilla=Sevilla"
        ),
        (
            "Der Protest begann gegen 11:00 Uhr Ortszeit (UTC +1) in Whitehall gegenüber dem von der Polizei bewachten Eingang zur Downing Street, dem offiziellen Wohnsitz des Premierministers.",
            "Whitehall=Whitehall, Downing Straße=Downing Street, offizielle Residenz des Premierministers=Prime Minister's official residence"
        ),
        (
            "Die Zahl der Nutzer der Dienste von Yahoo! und Microsoft zusammengenommen wird mit der Zahl der Kunden von AOL konkurrieren.",
            "Yahoo!=Yahoo!, Microsofts=Microsofts"
        ),            
    ],
    ("ja", "en"): [
        (
            "月曜日にスタンフォード大学医学部の科学者たちは、細胞を種類別に分類できる新しい診断ツールを発明したと発表しました。それは標準的なインクジェットプリンタで印刷して製造できる小型チップであり、原価は1枚あたり1円ほどす。",
            "スタンフォード大学=Stanford University, 医学部=School of Medicine"
        ),
        (
            "JAS 39Cグリペンは現地時間の午前9時30分頃（UTC 0230）に滑走路に墜落して爆発し、その影響で空港の商業便が閉鎖されました。",
            "JAS 39C Gripen=JAS 39C Gripen, 商用フライト=commercial flights"
        ),
        (
            "28歳のビダル選手は、3シーズン前にセビージャから移籍してバルサに所属していました。",
            "バルサ=Barça, セビージャ=Sevilla"
        ),
        (
            "抗議行動は、現地時間11:00（UTC+1）頃にホワイトホール通りで始まり、首相官邸があるダウニング街の警察が警備する入口の向かいに群衆が集結しました。",
            "ホワイトホール=Whitehall, ダウニングストリート=Downing Street, 首相官邸=Prime Minister's official residence"
        ),
        (
            "ヤフーとマイクロソフトのサービスを合わせたユーザー数は、AOLの顧客数に匹敵するだろう。",
            "Yahoo!=Yahoo!, Microsofts=Microsofts"
        ),            
    ],
    ("fr", "de"): [
        (
            "Des scientifiques de l’école de médecine de l’université de Stanford ont annoncé ce lundi la création d'un nouvel outil de diagnostic, qui permettrait de différencier les cellules en fonction de leur type. Il s'agit d'une petit puce imprimable, qui peut être produite au moyen d'une imprimante à jet d'encre standard, pour un coût d'environ un cent de dollar pièce.",
            "Université Stanford=Stanford Universität, l'école de médecine=Medizinische Fakultät"
        ),
        (
            "Le JAS 39C Gripen s’est écrasé sur une piste autour de 9 h 30 heure locale (0230 UTC) et a explosé, provoquant la fermeture de l’aéroport aux vols commerciaux.",
            "JAS 39C Gripen=JAS 39C Gripen, les vols commerciaux=kommerzielle Flüge"
        ),
        (
            "Vidal, 28 ans, avait rejoint le Barça il y a trois saisons, en provenance de Séville.",
            "Barça=Barça, Sevilla=Sevilla"
        ),
        (
            "La manifestation a commencé vers 11 h heure locale (UTC+1) sur Whitehall, en face de l'entrée gardée par la police de Downing Street, la résidence officielle du Premier ministre.",
            "Whitehall=Whitehall, Downing Street=Downing Straße, la résidence officielle du Premier ministre=offizielle Residenz des Premierministers"
        ),
        (
            "Le nombre d'utilisateurs des services Yahoo! et Microsoft combinés rivalisera avec le nombre de clients d'AOL.",
            "Yahoo!=Yahoo!, Microsoft=Microsoft"
        ),            
    ],
    ("de", "fr"): [
        (
            "Am Montag haben die Wisenschaftler der Stanford University School of Medicine die Erfindung eines neuen Diagnosetools bekanntgegeben, mit dem Zellen nach ihrem Typ sortiert werden können: ein winziger, ausdruckbarer Chip, der für jeweils etwa einen US-Cent mit Standard-Tintenstrahldruckern hergestellt werden kann.",
            "Stanford Universität=Université Stanford, Medizinische Fakultät=l'école de médecine"
        ),
        (
            "Der JAS 39C Gripen stürzte gegen 9:30 Uhr Ortszeit (02:30 UTC) auf eine Startbahn und explodierte, sodass der Flughafen für kommerzielle Flüge geschlossen werden musste.",
            "JAS 39C Gripen=JAS 39C Gripen, kommerzielle Flüge=les vols commerciaux"
        ),
        (
            "Der 28-jährige Vidal war vor drei Spielzeiten von Sevilla zu Barça gekommen.",
            "Barça=Barça, Sevilla=Sevilla"
        ),
        (
            "Der Protest begann gegen 11:00 Uhr Ortszeit (UTC +1) in Whitehall gegenüber dem von der Polizei bewachten Eingang zur Downing Street, dem offiziellen Wohnsitz des Premierministers.",
            "Whitehall=Whitehall, Downing Straße=Downing Street, offizielle Residenz des Premierministers=la résidence officielle du Premier ministre"
        ),
        (
            "Die Zahl der Nutzer der Dienste von Yahoo! und Microsoft zusammengenommen wird mit der Zahl der Kunden von AOL konkurrieren.",
            "Yahoo!=Yahoo!, Microsoft=Microsoft"
        ),            
    ]
}

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
        out_file_path = os.path.join(format_dir, f"{test_name}.{src}-{tgt}.{src}.ask-kw")

        demos = demo_dict[(src, tgt)]
        with open(out_file_path, 'w') as out_f:
            for id, src_line in enumerate(test_src_lines):
                all_items = demos + [(src_line, None)]
                prompt_lst = []
                for it in all_items:
                    it_src, it_kw = it
                    s = f"Let's extract the keywords in the following {src_full} sentence, and then translate these keywords into {tgt_full}.\n" + \
                    f"{src_full}: {it_src}\n" + \
                    (f"Keyword Pairs: {it_kw}" if it_kw else "Keyword Pairs:")
                    prompt_lst.append(s)

                prompt = "\n\n".join(prompt_lst)
                out_f.write(
                    f"{id:04}\n"
                    f"{prompt}\n\n\n"
                )

if __name__ == "__main__":
    args = parse_args()
    main(args)
